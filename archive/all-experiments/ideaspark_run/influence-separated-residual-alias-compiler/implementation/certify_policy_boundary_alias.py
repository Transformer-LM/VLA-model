"""Certify native-physics aliases on adjacent saved chunks of a successful VLA rollout.

The factual and candidate chunks are both frozen-policy outputs.  They are
evaluated from their exact saved policy boundaries because a MuJoCo flat state
does not serialize every OSC controller cache.  This is a boundary-snapshot E0,
not yet a continuous hidden-controller replay.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Sequence

import numpy as np

from israc.certificate import (
    AliasCertificate,
    FrameTrace,
    NoiseEnvelope,
    PhysicalParameter,
    RolloutTrace,
    certify_alias_pair,
)
from libero_m0_alias import array_sha256, max_trace_diff, probe, repeat_envelope


ROOT = Path("<PERSONAL_RESEARCH_ROOT>").resolve()
FAMILY_VALUES = {
    "compliance": (0.004, 0.020, 0.100),
    "friction": (0.05, 0.30, 1.50),
}
BLOCK_SELECTORS = ("israc", "candidate-contact", "random-scene")


def existing(raw: str) -> Path:
    path = Path(raw).resolve()
    if path == ROOT or ROOT not in path.parents or not path.exists():
        raise ValueError(path)
    return path


def new_output(raw: str) -> Path:
    path = Path(raw).resolve()
    if path == ROOT or ROOT not in path.parents or path.exists():
        raise ValueError(path)
    return path


def contacts(env: Any) -> set[tuple[int, int]]:
    pairs = set()
    for index in range(int(env.sim.data.ncon)):
        contact = env.sim.data.contact[index]
        pairs.add(tuple(sorted((int(contact.geom1), int(contact.geom2)))))
    return pairs


def is_robot_body(name: str | None) -> bool:
    lowered = (name or "").casefold()
    return any(token in lowered for token in ("robot", "gripper", "panda"))


def groups_from_pairs(
    model: Any,
    pairs: set[tuple[int, int]],
    allowed_geoms: set[int] | None = None,
) -> dict[str, set[int]]:
    """Group non-robot contact geometries by their owning body."""

    groups: dict[str, set[int]] = {}
    for left, right in pairs:
        for geom_id in (left, right):
            if allowed_geoms is not None and geom_id not in allowed_geoms:
                continue
            body_id = int(model.geom_bodyid[geom_id])
            body_name = model.body_id2name(body_id)
            if is_robot_body(body_name):
                continue
            groups.setdefault(body_name or f"body_{body_id}", set()).add(geom_id)
    return groups


def all_nonrobot_groups(model: Any) -> dict[str, set[int]]:
    """Return every legal non-robot geometry block in the scene."""

    groups: dict[str, set[int]] = {}
    for geom_id in range(int(model.ngeom)):
        body_id = int(model.geom_bodyid[geom_id])
        body_name = model.body_id2name(body_id)
        if is_robot_body(body_name):
            continue
        groups.setdefault(body_name or f"body_{body_id}", set()).add(geom_id)
    return groups


def choose_groups(
    groups: dict[str, set[int]],
    count: int | None,
    seed: int,
) -> list[tuple[str, set[int]]]:
    """Choose body blocks without looking at rollout outcomes or WAM scores."""

    rows = sorted(groups.items())
    if count is None or count >= len(rows):
        return rows
    if count <= 0:
        return []
    generator = np.random.default_rng(seed)
    indices = sorted(int(index) for index in generator.choice(len(rows), size=count, replace=False))
    return [rows[index] for index in indices]


def dynamic_nonrobot_vector(env: Any) -> np.ndarray:
    """Return a task-agnostic physical state for movable scene bodies.

    LIBERO goals include object-object relations, fixed receptacle regions, and
    articulated fixtures.  Resolving a single movable ``target`` therefore
    makes a cross-task compiler accidentally task-specific.  World-space poses
    of every non-robot body owning at least one joint cover free objects and
    articulated links without consulting the task predicate or a WAM score.
    """

    model = env.sim.model
    data = env.sim.data
    values: list[float] = []
    for body_id in range(1, int(model.nbody)):
        body_name = model.body_id2name(body_id)
        if is_robot_body(body_name) or int(model.body_jntnum[body_id]) == 0:
            continue
        values.extend(np.asarray(data.body_xpos[body_id], dtype=np.float64).tolist())
        values.extend(np.asarray(data.body_xquat[body_id], dtype=np.float64).tolist())
    if not values:
        raise RuntimeError("no movable non-robot bodies found")
    return np.asarray(values, dtype=np.float64)


def execute_contacts(
    env: Any,
    modes: Any,
    restore: Any,
    state: np.ndarray,
    actions: np.ndarray,
) -> set[tuple[int, int]]:
    restore(env, state, modes)
    result: set[tuple[int, int]] = set()
    for action in actions:
        modes.trace()
        env.step(np.asarray(action, dtype=np.float32))
        result.update(contacts(env))
    return result


def combine_envelopes(left: NoiseEnvelope, right: NoiseEnvelope) -> NoiseEnvelope:
    return NoiseEnvelope(**{
        field: max(float(getattr(left, field)), float(getattr(right, field)))
        for field in ("state", "proprio", "physical_effect_probe", "task_effect")
    })


def parameter(
    block_id: str,
    geom_ids: Sequence[int],
    value: float,
    family: str,
    values: Sequence[float],
) -> PhysicalParameter:
    if family == "compliance":
        semantic_family = "candidate_activated_contact_compliance"
        engine_field = f"mujoco.model.geom_solref[{','.join(map(str, geom_ids))},0:2]"
        units = "positive_solref_time_constant_seconds"
    else:
        semantic_family = "candidate_activated_surface_friction"
        engine_field = f"mujoco.model.geom_friction[{','.join(map(str, geom_ids))},0:3]"
        units = "dimensionless_coulomb_coefficients"
    return PhysicalParameter(
        block_id=block_id,
        family=semantic_family,
        engine_field=engine_field,
        value=float(value),
        lower=min(values),
        upper=max(values),
        physical_units=units,
    )


def rollout(
    env: Any,
    modes: Any,
    restore: Any,
    capture: Any,
    robot_vector: Any,
    original_solref: np.ndarray,
    original_friction: np.ndarray,
    state: np.ndarray,
    actions: np.ndarray,
    block_id: str,
    geom_ids: tuple[int, ...],
    value: float,
    family: str,
    values: Sequence[float],
    action_id: str,
    action_rank: int,
    height: int,
    width: int,
) -> RolloutTrace:
    obs = restore(env, state, modes)
    env.sim.model.geom_solref[:] = original_solref
    env.sim.model.geom_friction[:] = original_friction
    indices = np.asarray(geom_ids, dtype=np.int64)
    if family == "compliance":
        env.sim.model.geom_solref[indices, 0] = float(value)
        env.sim.model.geom_solref[indices, 1] = 1.0
    else:
        env.sim.model.geom_friction[indices, 0] = float(value)
        env.sim.model.geom_friction[indices, 1] = float(value) * 0.05
        env.sim.model.geom_friction[indices, 2] = float(value) * 0.001
    env.sim.forward()
    initial_world = dynamic_nonrobot_vector(env)
    initial_robot = robot_vector(obs)
    geom_set = set(geom_ids)
    frames: list[FrameTrace] = []
    for action in actions:
        modes.trace()
        obs, _, _, _ = env.step(np.asarray(action, dtype=np.float32))
        state_now = np.asarray(env.sim.get_state().flatten(), dtype=np.float64)
        proprio = np.asarray(robot_vector(obs), dtype=np.float64)
        image = capture(env, modes, height, width)
        world_effect = dynamic_nonrobot_vector(env) - initial_world
        robot_effect = proprio[:3] - initial_robot[:3]
        physical_effect_probe = np.concatenate((world_effect, robot_effect))
        active = any(left in geom_set or right in geom_set for left, right in contacts(env))
        frames.append(
            FrameTrace(
                state=probe(state_now, 512),
                proprio=probe(proprio, 32),
                rgb_sha256=array_sha256(image["rgb"]),
                depth_sha256=array_sha256(image["depth"]),
                physical_effect_probe=tuple(float(item) for item in physical_effect_probe),
                task_effect=tuple(float(item) for item in world_effect),
                active_parameter_blocks=(block_id,) if active else (),
            )
        )
    token = str(value).replace(".", "p")
    return RolloutTrace(
        world_id=f"{block_id}@{token}",
        action_id=action_id,
        action_rank=action_rank,
        frames=tuple(frames),
        parameters=(parameter(block_id, geom_ids, value, family, values),),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rollout", required=True)
    parser.add_argument("--support-code", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--candidate-index", type=int, required=True)
    parser.add_argument("--candidate-chunks", type=int, default=1)
    parser.add_argument("--family", choices=sorted(FAMILY_VALUES), default="compliance")
    parser.add_argument("--block-selector", choices=BLOCK_SELECTORS, default="israc")
    parser.add_argument("--selector-seed", type=int, default=0)
    parser.add_argument(
        "--match-israc-block-count",
        action="store_true",
        help="Give a baseline exactly the number of parameter blocks found by ISRAC.",
    )
    parser.add_argument("--height", type=int, default=64)
    parser.add_argument("--width", type=int, default=64)
    args = parser.parse_args()
    rollout_path = existing(args.rollout)
    support = existing(args.support_code)
    output = new_output(args.output)
    manifest = json.loads(rollout_path.read_text(encoding="utf-8"))
    arrays_path = existing(manifest["arrays"])
    arrays = np.load(arrays_path)
    states = np.asarray(arrays["boundary_states"], dtype=np.float64)
    chunks = np.asarray(arrays["action_chunks"], dtype=np.float32)
    index = args.candidate_index
    if not 1 <= index < min(len(states), len(chunks)):
        raise IndexError(index)
    if args.candidate_chunks < 1:
        raise ValueError("candidate-chunks must be positive")

    sys.path.insert(0, str(support))
    from collect_e1_paired_rollouts import (
        ObservableModes,
        capture,
        restore_canonical,
        robot_vector,
    )
    from libero.libero.envs import SegmentationRenderEnv

    env = SegmentationRenderEnv(
        bddl_file_name=str(existing(manifest["bddl"])),
        camera_heights=args.height,
        camera_widths=args.width,
        camera_depths=True,
        camera_segmentations="instance",
    )
    compiled = []
    block_rows = []
    try:
        env.seed(int(manifest["seed"]))
        env.reset()
        modes = ObservableModes(env.env)
        original_solref = np.asarray(env.sim.model.geom_solref, dtype=np.float64).copy()
        original_friction = np.asarray(env.sim.model.geom_friction, dtype=np.float64).copy()
        values = FAMILY_VALUES[args.family]
        factual_state, candidate_state = states[index - 1], states[index]
        factual_actions = chunks[index - 1]
        suffix_end = min(index + args.candidate_chunks, len(chunks))
        candidate_actions = np.concatenate(chunks[index:suffix_end], axis=0)

        factual_pairs = execute_contacts(
            env, modes, restore_canonical, factual_state, factual_actions
        )
        candidate_pairs = execute_contacts(
            env, modes, restore_canonical, candidate_state, candidate_actions
        )
        candidate_only = candidate_pairs - factual_pairs
        factual_geoms = {geom_id for pair in factual_pairs for geom_id in pair}
        candidate_geoms = {geom_id for pair in candidate_pairs for geom_id in pair}
        candidate_only_geoms = candidate_geoms - factual_geoms
        model = env.sim.model
        israc_groups = groups_from_pairs(model, candidate_only, candidate_only_geoms)
        if args.block_selector == "israc":
            pool = israc_groups
        elif args.block_selector == "candidate-contact":
            pool = groups_from_pairs(model, candidate_pairs)
        else:
            pool = all_nonrobot_groups(model)
        target_count = len(israc_groups) if args.match_israc_block_count else None
        selected_groups = choose_groups(
            pool,
            target_count,
            int(manifest["seed"]) + args.selector_seed,
        )

        for body_name, raw_ids in selected_groups:
            geom_ids = tuple(sorted(raw_ids))
            block_id = f"{args.block_selector}_{args.family}:{body_name}"
            factual: dict[float, RolloutTrace] = {}
            candidate: dict[float, RolloutTrace] = {}
            for value in values:
                factual[value] = rollout(
                    env, modes, restore_canonical, capture, robot_vector,
                    original_solref, original_friction, factual_state, factual_actions, block_id,
                    geom_ids, value, args.family, values, f"policy_chunk_{index - 1}", 1,
                    args.height, args.width,
                )
                candidate[value] = rollout(
                    env, modes, restore_canonical, capture, robot_vector,
                    original_solref, original_friction, candidate_state, candidate_actions, block_id,
                    geom_ids, value, args.family, values, f"policy_suffix_{index}_to_{suffix_end - 1}", 1,
                    args.height, args.width,
                )
            factual_repeat = rollout(
                env, modes, restore_canonical, capture, robot_vector,
                original_solref, original_friction, factual_state, factual_actions, block_id,
                geom_ids, values[0], args.family, values, f"policy_chunk_{index - 1}", 1,
                args.height, args.width,
            )
            candidate_repeat = rollout(
                env, modes, restore_canonical, capture, robot_vector,
                original_solref, original_friction, candidate_state, candidate_actions, block_id,
                geom_ids, values[0], args.family, values, f"policy_suffix_{index}_to_{suffix_end - 1}", 1,
                args.height, args.width,
            )
            envelope = combine_envelopes(
                repeat_envelope((factual[values[0]], factual_repeat)),
                repeat_envelope((candidate[values[0]], candidate_repeat)),
            )
            attempts = 0
            passes = 0
            best = 0.0
            failures: dict[str, int] = {}
            for left_pos, left_value in enumerate(values):
                for right_value in values[left_pos + 1 :]:
                    attempts += 1
                    certificate = AliasCertificate(
                        factual_action_id=f"policy_chunk_{index - 1}",
                        candidate_action_id=f"policy_suffix_{index}_to_{suffix_end - 1}",
                        top_k=1,
                        search_objective_terms=(
                            f"block_selector:{args.block_selector}",
                            "native_parameter_block",
                            "task_effect_separation",
                            "factual_transcript_constraint",
                        ),
                        compiler_seed=int(manifest["seed"]),
                        simulator="LIBERO-MuJoCo",
                        task_id=str(manifest["task"]),
                        snapshot_id=hashlib.sha256(
                            np.concatenate((factual_state, candidate_state)).tobytes()
                        ).hexdigest(),
                        allowed_activation_lag=1,
                    )
                    result = certify_alias_pair(
                        factual[left_value], factual[right_value],
                        candidate[left_value], candidate[right_value],
                        certificate, envelope,
                    )
                    if result.passed:
                        passes += 1
                        separation = float(result.measurements["candidate_task_effect_max_abs"])
                        best = max(best, separation)
                        compiled.append({
                            "block_id": block_id,
                            "geom_ids": list(geom_ids),
                            "left_value": left_value,
                            "right_value": right_value,
                            "measurements": dict(result.measurements),
                            "certificate_sha256": result.certificate_sha256,
                        })
                    else:
                        for failure in result.failures:
                            failures[failure] = failures.get(failure, 0) + 1
            block_rows.append({
                "block_id": block_id,
                "geom_ids": list(geom_ids),
                "attempted_pairs": attempts,
                "certified_pairs": passes,
                "best_task_effect_max_component": best,
                "failure_reason_counts": dict(sorted(failures.items())),
                "repeat_noise_envelope": asdict(envelope),
            })
    finally:
        env.close()

    compiled.sort(
        key=lambda row: float(row["measurements"]["candidate_task_effect_max_abs"]),
        reverse=True,
    )
    payload = {
        "kind": "israc_policy_supported_boundary_snapshot_alias_e0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "claim_limit": (
            "The factual chunk and open-loop candidate suffix are frozen VLA outputs from one "
            "successful trajectory and are "
            "evaluated at their exact saved boundaries. This does not yet serialize or replay "
            "the hidden OSC controller state continuously, test multiple tasks, or measure WAM harm."
        ),
        "passed": bool(compiled),
        "rollout": str(rollout_path),
        "rollout_sha256": hashlib.sha256(rollout_path.read_bytes()).hexdigest(),
        "arrays_sha256": hashlib.sha256(arrays_path.read_bytes()).hexdigest(),
        "factual_chunk_index": index - 1,
        "candidate_chunk_index": index,
        "candidate_suffix_end_index": suffix_end - 1,
        "candidate_suffix_action_count": len(candidate_actions),
        "candidate_boundary_step": int(arrays["boundary_steps"][index]),
        "policy_candidate_rank": 1,
        "compiler_blind_to_target_wam": True,
        "manual_parameter_pair_tuning": False,
        "task_effect_metric": "world_pose_delta_of_all_jointed_nonrobot_bodies",
        "candidate_only_contact_pair_count": len(candidate_only),
        "candidate_only_geom_count": len(candidate_only_geoms),
        "block_selector": args.block_selector,
        "selector_seed": args.selector_seed,
        "selector_pool_block_count": len(pool),
        "israc_reference_block_count": len(israc_groups),
        "selected_block_count": len(selected_groups),
        "matched_israc_block_count": bool(args.match_israc_block_count),
        "selection_contact_rollouts": 2,
        "physics_rollouts_per_selected_block": 8,
        "total_rollouts_including_selection": 2 + 8 * len(selected_groups),
        "total_simulator_steps": (
            len(factual_actions) + len(candidate_actions)
            + len(selected_groups) * 4 * (len(factual_actions) + len(candidate_actions))
        ),
        "blocks": block_rows,
        "compiled_pair_count": len(compiled),
        "best_pairs": compiled[:10],
        "arguments": vars(args),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, output)
    print(json.dumps({
        "passed": payload["passed"],
        "compiled_pair_count": payload["compiled_pair_count"],
        "blocks": [{"id": row["block_id"], "pairs": row["certified_pairs"]} for row in block_rows],
    }, sort_keys=True))
    raise SystemExit(0 if payload["passed"] else 2)


if __name__ == "__main__":
    main()
