"""Bounded LIBERO/MuJoCo M0 for one native-friction residual-alias pair.

This script validates the real simulator adapter and certificate path.  It uses
scripted factual/candidate controls, so its output is engineering evidence only
and must not be reported as policy-supported compiler yield.
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


PERSONAL_ROOT = Path("<PERSONAL_RESEARCH_ROOT>")
PARAMETER_BLOCK = "target_contact_friction"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bddl", required=True)
    parser.add_argument("--support-code", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=20260831)
    parser.add_argument("--height", type=int, default=64)
    parser.add_argument("--width", type=int, default=64)
    parser.add_argument("--steps", type=int, default=16)
    parser.add_argument("--friction-low", type=float, default=0.10)
    parser.add_argument("--friction-high", type=float, default=1.10)
    parser.add_argument("--push-magnitude", type=float, default=0.8)
    parser.add_argument("--margin-m", type=float, default=0.010)
    parser.add_argument("--repeat-count", type=int, default=3)
    return parser.parse_args()


def require_personal(path: Path, *, must_exist: bool) -> Path:
    root = PERSONAL_ROOT.resolve(strict=True)
    resolved = path.resolve(strict=must_exist)
    if not resolved.is_relative_to(root) or resolved == root:
        raise RuntimeError(f"path escapes personal root: {resolved}")
    return resolved


def target_geom_ids(env: Any, target: str) -> tuple[int, ...]:
    obj = env.env.objects_dict[target]
    names = tuple(str(name) for name in getattr(obj, "contact_geoms", ()))
    ids = []
    for name in names:
        try:
            ids.append(int(env.sim.model.geom_name2id(name)))
        except Exception:
            continue
    if not ids:
        root = int(env.sim.model.body_name2id(obj.root_body))
        parent = np.asarray(env.sim.model.body_parentid, dtype=np.int64)
        descendants = {root}
        changed = True
        while changed:
            changed = False
            for body_id, parent_id in enumerate(parent.tolist()):
                if parent_id in descendants and body_id not in descendants:
                    descendants.add(body_id)
                    changed = True
        geom_body = np.asarray(env.sim.model.geom_bodyid, dtype=np.int64)
        ids = np.flatnonzero(np.isin(geom_body, list(descendants))).astype(int).tolist()
    if not ids:
        raise RuntimeError(f"no target geoms resolved for {target}")
    return tuple(sorted(set(ids)))


def set_target_friction(env: Any, geom_ids: Sequence[int], value: float) -> None:
    # MuJoCo's native per-geom triple is [sliding, torsional, rolling].
    env.sim.model.geom_friction[np.asarray(geom_ids, dtype=np.int64), 0] = float(value)
    env.sim.model.geom_friction[np.asarray(geom_ids, dtype=np.int64), 1] = float(value) * 0.05
    env.sim.model.geom_friction[np.asarray(geom_ids, dtype=np.int64), 2] = float(value) * 0.001
    env.sim.forward()


def parameter(world_value: float) -> PhysicalParameter:
    return PhysicalParameter(
        block_id=PARAMETER_BLOCK,
        family="object_surface_friction",
        engine_field="mujoco.model.geom_friction[target_contact_geoms,0:3]",
        value=float(world_value),
        lower=0.05,
        upper=1.50,
        physical_units="dimensionless_coulomb_coefficients",
    )


def probe(array: np.ndarray, count: int = 128) -> tuple[float, ...]:
    flat = np.asarray(array, dtype=np.float64).reshape(-1)
    if flat.size <= count:
        return tuple(float(value) for value in flat)
    indices = np.linspace(0, flat.size - 1, num=count, dtype=np.int64)
    return tuple(float(value) for value in flat[indices])


def array_sha256(array: np.ndarray) -> str:
    contiguous = np.ascontiguousarray(array)
    digest = hashlib.sha256()
    digest.update(str(contiguous.dtype).encode("ascii"))
    digest.update(str(contiguous.shape).encode("ascii"))
    digest.update(contiguous.tobytes())
    return digest.hexdigest()


def target_xy_speed(env: Any, target: str) -> float:
    obj = env.env.objects_dict[target]
    velocity = np.asarray(env.sim.data.get_body_xvelp(obj.root_body), dtype=np.float64)
    return float(np.linalg.norm(velocity[:2]))


def target_in_contact(env: Any, geom_ids: set[int]) -> bool:
    for index in range(int(env.sim.data.ncon)):
        contact = env.sim.data.contact[index]
        if int(contact.geom1) in geom_ids or int(contact.geom2) in geom_ids:
            return True
    return False


def rollout(
    env: Any,
    modes: Any,
    restore_canonical: Any,
    capture: Any,
    robot_vector: Any,
    object_pose: Any,
    start_state: np.ndarray,
    target: str,
    geom_ids: tuple[int, ...],
    world_id: str,
    friction: float,
    action_id: str,
    action_rank: int,
    commands: np.ndarray,
    height: int,
    width: int,
) -> RolloutTrace:
    restore_canonical(env, start_state, modes)
    set_target_friction(env, geom_ids, friction)
    initial_pose = object_pose(env, target)
    frames: list[FrameTrace] = []
    geom_set = set(geom_ids)
    for command in commands:
        modes.trace()
        obs, _, _, _ = env.step(np.asarray(command, dtype=np.float32))
        state = np.asarray(env.sim.get_state().flatten(), dtype=np.float64)
        proprio = np.asarray(robot_vector(obs), dtype=np.float64)
        image = capture(env, modes, height, width)
        pose = object_pose(env, target)
        effect = np.asarray(pose[:3] - initial_pose[:3], dtype=np.float64)
        slip_active = target_in_contact(env, geom_set) and target_xy_speed(env, target) > 1e-5
        frames.append(
            FrameTrace(
                state=probe(state, 512),
                proprio=probe(proprio, 32),
                rgb_sha256=array_sha256(image["rgb"]),
                depth_sha256=array_sha256(image["depth"]),
                # Simulator-native effect proxy only. WAM residuals belong to a
                # separate post-hoc audit artifact and never enter this manifest.
                physical_effect_probe=tuple(float(value) for value in effect),
                task_effect=tuple(float(value) for value in effect),
                active_parameter_blocks=(PARAMETER_BLOCK,) if slip_active else (),
            )
        )
    return RolloutTrace(
        world_id=world_id,
        action_id=action_id,
        action_rank=action_rank,
        frames=tuple(frames),
        parameters=(parameter(friction),),
    )


def max_trace_diff(left: RolloutTrace, right: RolloutTrace, field: str) -> float:
    if len(left.frames) != len(right.frames):
        return float("inf")
    maximum = 0.0
    for a, b in zip(left.frames, right.frames):
        x = np.asarray(getattr(a, field), dtype=np.float64)
        y = np.asarray(getattr(b, field), dtype=np.float64)
        if x.shape != y.shape:
            return float("inf")
        maximum = max(maximum, float(np.max(np.abs(x - y), initial=0.0)))
    return maximum


def repeat_envelope(repeats: Sequence[RolloutTrace]) -> NoiseEnvelope:
    fields = ("state", "proprio", "physical_effect_probe", "task_effect")
    maxima = {field: 0.0 for field in fields}
    for index in range(1, len(repeats)):
        for field in fields:
            maxima[field] = max(maxima[field], max_trace_diff(repeats[0], repeats[index], field))
    # Exact runs remain exact; non-zero repeat noise receives a 5% numerical guard.
    def guarded(value: float) -> float:
        return 0.0 if value == 0.0 else value * 1.05 + 1e-12
    # MuJoCo's registered exact-replay contract uses 1e-10 for simulator
    # state / realized trace.  Keep that pre-existing numerical floor separate
    # from empirical rerun noise; an exact zero repeat must not imply bitwise
    # equality after changing an otherwise dormant native model coefficient.
    return NoiseEnvelope(
        state=max(guarded(maxima["state"]), 1e-10),
        proprio=max(guarded(maxima["proprio"]), 1e-10),
        physical_effect_probe=max(guarded(maxima["physical_effect_probe"]), 1e-10),
        task_effect=max(guarded(maxima["task_effect"]), 1e-6),
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    args = parse_args()
    if os.environ.get("MUJOCO_GL", "").casefold() != "osmesa":
        raise RuntimeError("MUJOCO_GL=osmesa is required")
    if os.environ.get("PYOPENGL_PLATFORM", "").casefold() != "osmesa":
        raise RuntimeError("PYOPENGL_PLATFORM=osmesa is required")
    if args.steps < 4 or args.repeat_count < 2:
        raise ValueError("steps>=4 and repeat-count>=2 are required")
    bddl = require_personal(Path(args.bddl), must_exist=True)
    support_code = require_personal(Path(args.support_code), must_exist=True)
    output = require_personal(Path(args.output), must_exist=False)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    sys.path.insert(0, str(support_code))
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
        base_state = env.sim.get_state().flatten().copy()
        template = discover_valid_placement_template(
            env, modes, base_state, relation, target, reference, argument, 12
        )
        direction = np.asarray((1.0, 0.0), dtype=np.float64)
        start_state, construction = construct_prestate(
            env, modes, base_state, target, reference, argument, direction,
            args.margin_m, template, 12, 80,
        )
        if start_state is None:
            raise RuntimeError(f"prestate construction failed: {construction}")
        geoms = target_geom_ids(env, target)
        factual_commands = np.zeros((args.steps, 7), dtype=np.float32)
        candidate_commands = np.zeros((args.steps, 7), dtype=np.float32)
        candidate_commands[: args.steps // 2, 0] = float(args.push_magnitude)

        low_repeats = [
            rollout(
                env, modes, restore_canonical, capture, robot_vector, object_pose,
                start_state, target, geoms, "world_low", args.friction_low,
                "factual_hold", 1, factual_commands, args.height, args.width,
            )
            for _ in range(args.repeat_count)
        ]
        envelope = repeat_envelope(low_repeats)
        factual_low = low_repeats[0]
        factual_high = rollout(
            env, modes, restore_canonical, capture, robot_vector, object_pose,
            start_state, target, geoms, "world_high", args.friction_high,
            "factual_hold", 1, factual_commands, args.height, args.width,
        )
        candidate_low = rollout(
            env, modes, restore_canonical, capture, robot_vector, object_pose,
            start_state, target, geoms, "world_low", args.friction_low,
            "candidate_push", 2, candidate_commands, args.height, args.width,
        )
        candidate_high = rollout(
            env, modes, restore_canonical, capture, robot_vector, object_pose,
            start_state, target, geoms, "world_high", args.friction_high,
            "candidate_push", 2, candidate_commands, args.height, args.width,
        )
        result = certify_alias_pair(
            factual_low,
            factual_high,
            candidate_low,
            candidate_high,
            AliasCertificate(
                factual_action_id="factual_hold",
                candidate_action_id="candidate_push",
                top_k=8,
                search_objective_terms=("task_effect_separation", "factual_transcript_constraint"),
                compiler_seed=args.seed,
                simulator="LIBERO-MuJoCo",
                task_id=bddl.name,
                snapshot_id=hashlib.sha256(np.asarray(start_state).tobytes()).hexdigest(),
                allowed_activation_lag=1,
            ),
            envelope,
        )
        payload = {
            "kind": "israc_libero_m0_native_friction",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "claim_limit": (
                "Real LIBERO deterministic/certificate M0 with scripted controls only; "
                "not automatic compiler yield, policy support, WAM correction harm, or VLA gain."
            ),
            "passed": result.passed,
            "failures": list(result.failures),
            "measurements": dict(result.measurements),
            "certificate_sha256": result.certificate_sha256,
            "repeat_noise_envelope": asdict(envelope),
            "physics": {
                "target": target,
                "target_geom_ids": list(geoms),
                "friction_low": args.friction_low,
                "friction_high": args.friction_high,
                "engine_field": parameter(args.friction_low).engine_field,
            },
            "prestate_construction": construction,
            "bddl": str(bddl),
            "bddl_sha256": sha256_file(bddl),
            "script_sha256": sha256_file(Path(__file__)),
            "arguments": vars(args),
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(temporary, output)
        print(json.dumps(payload, indent=2, sort_keys=True))
        raise SystemExit(0 if result.passed else 2)
    finally:
        env.close()


if __name__ == "__main__":
    main()
