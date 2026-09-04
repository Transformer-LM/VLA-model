"""Automatic single-snapshot LIBERO parameter-block compiler pilot.

The pilot enumerates simulator-native friction and load blocks, screens them
for negligible influence on a factual hold transcript, and then compiles every
certified pair whose candidate push activates the block and separates physical
task effects. Controls are still scripted; this is not the policy-supported
multi-task M1 gate.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Callable, Sequence

import numpy as np

from israc.certificate import (
    AliasCertificate,
    FrameTrace,
    PhysicalParameter,
    RolloutTrace,
    certify_alias_pair,
)
from libero_m0_alias import (
    PERSONAL_ROOT,
    array_sha256,
    max_trace_diff,
    probe,
    repeat_envelope,
    require_personal,
    target_geom_ids,
    target_in_contact,
    target_xy_speed,
)


@dataclass(frozen=True)
class NativeBlock:
    block_id: str
    family: str
    engine_field: str
    units: str
    values: tuple[float, ...]
    apply: Callable[[float], None]
    active: Callable[[], bool]

    def parameter(self, value: float) -> PhysicalParameter:
        return PhysicalParameter(
            block_id=self.block_id,
            family=self.family,
            engine_field=self.engine_field,
            value=float(value),
            lower=float(min(self.values)),
            upper=float(max(self.values)),
            physical_units=self.units,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bddl", required=True)
    parser.add_argument("--support-code", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=20260831)
    parser.add_argument("--steps", type=int, default=32)
    parser.add_argument("--height", type=int, default=64)
    parser.add_argument("--width", type=int, default=64)
    parser.add_argument("--repeat-count", type=int, default=3)
    parser.add_argument("--margin-m", type=float, default=0.010)
    parser.add_argument("--push-magnitude", type=float, default=0.8)
    parser.add_argument(
        "--blocks", nargs="*", default=[
            "target_contact_friction", "candidate_only_surface_compliance", "target_load_scale"
        ]
    )
    return parser.parse_args()


def make_blocks(
    env: Any,
    target: str,
    geom_ids: tuple[int, ...],
    candidate_only_surface_geoms: tuple[int, ...],
) -> tuple[NativeBlock, ...]:
    model = env.sim.model
    obj = env.env.objects_dict[target]
    body_id = int(model.body_name2id(obj.root_body))
    original_friction = np.asarray(model.geom_friction, dtype=np.float64).copy()
    original_mass = np.asarray(model.body_mass, dtype=np.float64).copy()
    original_inertia = np.asarray(model.body_inertia, dtype=np.float64).copy()
    original_solref = np.asarray(model.geom_solref, dtype=np.float64).copy()

    def reset_native() -> None:
        model.geom_friction[:] = original_friction
        model.body_mass[:] = original_mass
        model.body_inertia[:] = original_inertia
        model.geom_solref[:] = original_solref

    def apply_friction(value: float) -> None:
        reset_native()
        indices = np.asarray(geom_ids, dtype=np.int64)
        model.geom_friction[indices, 0] = float(value)
        model.geom_friction[indices, 1] = float(value) * 0.05
        model.geom_friction[indices, 2] = float(value) * 0.001
        env.sim.forward()

    def apply_load_scale(value: float) -> None:
        reset_native()
        model.body_mass[body_id] = original_mass[body_id] * float(value)
        model.body_inertia[body_id] = original_inertia[body_id] * float(value)
        env.sim.forward()

    def apply_contact_compliance(value: float) -> None:
        reset_native()
        indices = np.asarray(geom_ids, dtype=np.int64)
        # Positive solref format: [time constant (s), damping ratio].
        model.geom_solref[indices, 0] = float(value)
        model.geom_solref[indices, 1] = 1.0
        env.sim.forward()

    def dynamic_contact() -> bool:
        return target_in_contact(env, set(geom_ids)) and target_xy_speed(env, target) > 1e-5

    candidate_only_set = set(candidate_only_surface_geoms)

    def candidate_surface_active() -> bool:
        for index in range(int(env.sim.data.ncon)):
            contact = env.sim.data.contact[index]
            if int(contact.geom1) in candidate_only_set or int(contact.geom2) in candidate_only_set:
                return True
        return False

    def apply_candidate_surface_compliance(value: float) -> None:
        reset_native()
        if not candidate_only_surface_geoms:
            raise RuntimeError("candidate-only surface block has no discovered native geoms")
        indices = np.asarray(candidate_only_surface_geoms, dtype=np.int64)
        model.geom_solref[indices, 0] = float(value)
        model.geom_solref[indices, 1] = 1.0
        env.sim.forward()

    return (
        NativeBlock(
            block_id="target_contact_friction",
            family="object_surface_friction",
            engine_field="mujoco.model.geom_friction[target_contact_geoms,0:3]",
            units="dimensionless_coulomb_coefficients",
            values=(0.05, 0.10, 0.30, 0.60, 1.00, 1.50),
            apply=apply_friction,
            active=dynamic_contact,
        ),
        NativeBlock(
            block_id="target_contact_compliance",
            family="contact_compliance",
            engine_field="mujoco.model.geom_solref[target_contact_geoms,0:2]",
            units="positive_solref_time_constant_seconds",
            values=(0.004, 0.008, 0.015, 0.030, 0.060, 0.100),
            apply=apply_contact_compliance,
            active=dynamic_contact,
        ),
        NativeBlock(
            block_id="candidate_only_surface_compliance",
            family="candidate_activated_contact_compliance",
            engine_field=(
                "mujoco.model.geom_solref[contact_graph(candidate)-contact_graph(factual),0:2]"
            ),
            units="positive_solref_time_constant_seconds",
            values=(0.004, 0.008, 0.015, 0.030, 0.060, 0.100),
            apply=apply_candidate_surface_compliance,
            active=candidate_surface_active,
        ),
        NativeBlock(
            block_id="target_load_scale",
            family="object_load",
            engine_field="mujoco.model.body_mass+body_inertia[target_root]",
            units="multiplicative_scale_of_native_kg_and_kg_m2",
            values=(0.50, 0.75, 1.00, 1.50, 2.00, 3.00),
            apply=apply_load_scale,
            active=dynamic_contact,
        ),
    )


def rollout_block(
    env: Any,
    modes: Any,
    restore_canonical: Any,
    capture: Any,
    robot_vector: Any,
    object_pose: Any,
    start_state: np.ndarray,
    target: str,
    block: NativeBlock,
    value: float,
    action_id: str,
    action_rank: int,
    commands: np.ndarray,
    height: int,
    width: int,
) -> RolloutTrace:
    restore_canonical(env, start_state, modes)
    block.apply(value)
    initial_pose = object_pose(env, target)
    initial_robot: np.ndarray | None = None
    frames: list[FrameTrace] = []
    for command in commands:
        modes.trace()
        obs, _, _, _ = env.step(np.asarray(command, dtype=np.float32))
        state = np.asarray(env.sim.get_state().flatten(), dtype=np.float64)
        proprio = np.asarray(robot_vector(obs), dtype=np.float64)
        if initial_robot is None:
            initial_robot = proprio.copy()
        image = capture(env, modes, height, width)
        target_effect = np.asarray(object_pose(env, target)[:3] - initial_pose[:3], dtype=np.float64)
        robot_effect = np.asarray(proprio[:3] - initial_robot[:3], dtype=np.float64)
        effect = np.concatenate((target_effect, robot_effect))
        frames.append(
            FrameTrace(
                state=probe(state, 512),
                proprio=probe(proprio, 32),
                rgb_sha256=array_sha256(image["rgb"]),
                depth_sha256=array_sha256(image["depth"]),
                physical_effect_probe=tuple(float(x) for x in effect),
                task_effect=tuple(float(x) for x in effect),
                active_parameter_blocks=(block.block_id,) if block.active() else (),
            )
        )
    value_token = str(value).replace(".", "p")
    return RolloutTrace(
        world_id=f"{block.block_id}_{value_token}",
        action_id=action_id,
        action_rank=action_rank,
        frames=tuple(frames),
        parameters=(block.parameter(value),),
    )


def main() -> None:
    args = parse_args()
    if os.environ.get("MUJOCO_GL", "").casefold() != "osmesa" or os.environ.get(
        "PYOPENGL_PLATFORM", ""
    ).casefold() != "osmesa":
        raise RuntimeError("registered OSMesa environment is required")
    bddl = require_personal(Path(args.bddl), must_exist=True)
    support = require_personal(Path(args.support_code), must_exist=True)
    output = require_personal(Path(args.output), must_exist=False)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    sys.path.insert(0, str(support))
    from collect_e1_paired_rollouts import (  # type: ignore
        ObservableModes,
        capture,
        construct_prestate,
        discover_valid_placement_template,
        goal_spec,
        object_pose,
        restore_canonical,
        robot_vector,
    )
    from libero.libero.envs import SegmentationRenderEnv

    env = SegmentationRenderEnv(
        bddl_file_name=str(bddl),
        camera_heights=args.height,
        camera_widths=args.width,
        camera_depths=True,
        camera_segmentations="instance",
    )
    try:
        env.seed(args.seed)
        env.reset()
        modes = ObservableModes(env.env)
        relation, target, reference, argument = goal_spec(env)
        base = env.sim.get_state().flatten().copy()
        template = discover_valid_placement_template(
            env, modes, base, relation, target, reference, argument, 12
        )
        start_state, construction = construct_prestate(
            env, modes, base, target, reference, argument,
            np.asarray((1.0, 0.0), dtype=np.float64), args.margin_m,
            template, 12, 80,
        )
        if start_state is None:
            raise RuntimeError(f"prestate construction failed: {construction}")
        geoms = target_geom_ids(env, target)
        hold = np.zeros((args.steps, 7), dtype=np.float32)
        push = np.zeros((args.steps, 7), dtype=np.float32)
        push[: args.steps // 2, 0] = float(args.push_magnitude)

        # Discover native surfaces reached only by the candidate action. This
        # contact-graph step is blind to all WAM scores and rankings.
        from libero_contact_graph_probe import execute_contacts
        reference_geoms = set(target_geom_ids(env, reference))
        relevant_geoms = set(geoms) | reference_geoms
        factual_pairs, _ = execute_contacts(
            env, modes, restore_canonical, start_state, hold, relevant_geoms
        )
        candidate_pairs, _ = execute_contacts(
            env, modes, restore_canonical, start_state, push, relevant_geoms
        )
        factual_contact_geoms = {value for pair in factual_pairs for value in pair}
        candidate_contact_geoms = {value for pair in candidate_pairs for value in pair}
        candidate_only_surface_geoms = tuple(
            sorted((candidate_contact_geoms - factual_contact_geoms) & reference_geoms)
        )
        all_blocks = make_blocks(env, target, geoms, candidate_only_surface_geoms)
        requested = set(args.blocks)
        blocks = tuple(block for block in all_blocks if block.block_id in requested)
        if not blocks or {block.block_id for block in blocks} != requested:
            raise ValueError(f"unknown or empty native block selection: {args.blocks}")

        # Calibrate on repeated factual rollouts at the first native block/value.
        repeats = [
            rollout_block(
                env, modes, restore_canonical, capture, robot_vector, object_pose,
                start_state, target, blocks[0], blocks[0].values[0],
                "factual_hold", 1, hold, args.height, args.width,
            )
            for _ in range(args.repeat_count)
        ]
        envelope = repeat_envelope(repeats)
        total_rollouts = len(repeats)
        compiled: list[dict[str, Any]] = []
        block_summary: list[dict[str, Any]] = []

        for block in blocks:
            factual: dict[float, RolloutTrace] = {}
            candidate: dict[float, RolloutTrace] = {}
            for value in block.values:
                factual[value] = rollout_block(
                    env, modes, restore_canonical, capture, robot_vector, object_pose,
                    start_state, target, block, value, "factual_hold", 1,
                    hold, args.height, args.width,
                )
                candidate[value] = rollout_block(
                    env, modes, restore_canonical, capture, robot_vector, object_pose,
                    start_state, target, block, value, "candidate_push", 2,
                    push, args.height, args.width,
                )
                total_rollouts += 2
            valid_count = 0
            best_separation = 0.0
            attempted = 0
            failure_counts: Counter[str] = Counter()
            for left_index, left_value in enumerate(block.values):
                for right_value in block.values[left_index + 1 :]:
                    attempted += 1
                    certificate = AliasCertificate(
                        factual_action_id="factual_hold",
                        candidate_action_id="candidate_push",
                        top_k=8,
                        search_objective_terms=(
                            "native_parameter_influence_zero",
                            "task_effect_separation",
                            "factual_transcript_constraint",
                        ),
                        compiler_seed=args.seed,
                        simulator="LIBERO-MuJoCo",
                        task_id=bddl.name,
                        snapshot_id=hashlib.sha256(np.asarray(start_state).tobytes()).hexdigest(),
                        allowed_activation_lag=1,
                    )
                    result = certify_alias_pair(
                        factual[left_value], factual[right_value],
                        candidate[left_value], candidate[right_value],
                        certificate, envelope,
                    )
                    if result.passed:
                        valid_count += 1
                        separation = float(result.measurements["candidate_task_effect_max_abs"])
                        best_separation = max(best_separation, separation)
                        compiled.append({
                            "block_id": block.block_id,
                            "family": block.family,
                            "left_value": left_value,
                            "right_value": right_value,
                            "certificate_sha256": result.certificate_sha256,
                            "measurements": dict(result.measurements),
                        })
                    else:
                        failure_counts.update(result.failures)
            block_summary.append({
                "block_id": block.block_id,
                "family": block.family,
                "values": list(block.values),
                "attempted_pairs": attempted,
                "certified_pairs": valid_count,
                "yield": valid_count / attempted if attempted else 0.0,
                "best_task_effect_separation_m": best_separation,
                "failure_reason_counts": dict(sorted(failure_counts.items())),
            })

        compiled.sort(
            key=lambda row: float(row["measurements"]["candidate_task_effect_max_abs"]),
            reverse=True,
        )
        payload = {
            "kind": "israc_libero_single_snapshot_compiler_pilot",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "claim_limit": (
                "Automatic native-parameter pair compilation on one LIBERO snapshot with "
                "scripted controls; not policy-supported, multi-task, matched-baseline, "
                "RoboTwin, WAM correction-harm, or VLA evidence."
            ),
            "passed": all(row["certified_pairs"] > 0 for row in block_summary),
            "total_simulator_rollouts": total_rollouts,
            "repeat_noise_envelope": asdict(envelope),
            "block_summary": block_summary,
            "compiled_pair_count": len(compiled),
            "best_pairs": compiled[:10],
            "compiler_blind_to_target_wam": True,
            "manual_per_pair_tuning": False,
            "task": bddl.name,
            "target": target,
            "candidate_only_surface_geoms": list(candidate_only_surface_geoms),
            "prestate_construction": construction,
            "arguments": vars(args),
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(temporary, output)
        print(json.dumps(payload, indent=2, sort_keys=True))
        raise SystemExit(0 if payload["passed"] else 2)
    finally:
        env.close()


if __name__ == "__main__":
    main()
