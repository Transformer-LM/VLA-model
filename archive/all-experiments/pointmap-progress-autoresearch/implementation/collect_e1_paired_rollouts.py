"""Collect P1 physics-mediated relation rollouts for E1/B2.

Direct object placement is confined to pre-state construction. Once the
transition-start snapshot is taken, every world-state change is caused by a
control passed to ``env.step``. Learned inputs contain only observations,
commands, and robot-only kinematics; simulator states and poses are written to
a separate audit archive.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any
import uuid

import numpy as np

from e1_geometry import relation_geometry_54


CAMERAS = (("agentview", "agentview"), ("robot0_eye_in_hand", "robot0_eye_in_hand"))
REQUIRED_PROPRIO = (
    "robot0_eef_pos",
    "robot0_eef_quat",
    "robot0_gripper_qpos",
    "robot0_joint_pos",
)
ACTION_FAMILIES = (
    ("push_pos_x", (1.0, 0.0)),
    ("push_neg_x", (-1.0, 0.0)),
    ("push_pos_y", (0.0, 1.0)),
    ("push_neg_y", (0.0, -1.0)),
)
DEFAULT_TASKS = (
    "LIVING_ROOM_SCENE3_pick_up_the_ketchup_and_put_it_in_the_tray.bddl",
    "KITCHEN_SCENE5_put_the_black_bowl_on_the_plate.bddl",
)
PERSONAL_ROOT = Path("<PERSONAL_RESEARCH_ROOT_ALIAS>")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bddl-root", required=True)
    parser.add_argument("--output", required=True, help="Main learned-input NPZ path")
    parser.add_argument("--height", type=int, default=96)
    parser.add_argument("--width", type=int, default=96)
    parser.add_argument("--seed", type=int, default=20260830)
    parser.add_argument("--tasks", nargs="*", default=list(DEFAULT_TASKS))
    parser.add_argument("--margins-m", nargs="*", type=float, default=[
        0.002, 0.004, 0.006, 0.008, 0.010, 0.013, 0.016, 0.020,
        0.026, 0.032, 0.038, 0.045, 0.052, 0.060, 0.070, 0.080,
    ])
    parser.add_argument("--push-magnitude", type=float, default=0.8)
    parser.add_argument("--push-steps", type=int, default=8)
    parser.add_argument("--settle-steps", type=int, default=8)
    parser.add_argument("--placement-settle-steps", type=int, default=12)
    parser.add_argument("--approach-steps", type=int, default=80)
    parser.add_argument("--max-samples", type=int, default=0)
    return parser.parse_args()


def resolve_contract(args: argparse.Namespace) -> tuple[Path, Path]:
    if os.environ.get("MUJOCO_GL", "").casefold() != "osmesa":
        raise RuntimeError("MUJOCO_GL=osmesa is required")
    if os.environ.get("PYOPENGL_PLATFORM", "").casefold() != "osmesa":
        raise RuntimeError("PYOPENGL_PLATFORM=osmesa is required")
    if args.height <= 0 or args.width <= 0 or args.push_steps <= 0 or args.settle_steps <= 0:
        raise ValueError("image sizes and transition step counts must be positive")
    if args.push_steps + args.settle_steps != 16:
        raise ValueError("registered E1 trace is exactly 16 steps")
    if not (0.0 < args.push_magnitude <= 1.0):
        raise ValueError("push magnitude must lie in (0, 1]")
    if not args.tasks or len(set(args.tasks)) != len(args.tasks):
        raise ValueError("tasks must be non-empty and unique")
    if len(args.margins_m) < 8 or any(value <= 0 for value in args.margins_m):
        raise ValueError("P1 requires at least eight positive planned margins")
    root = PERSONAL_ROOT.resolve(strict=True)
    bddl_root = Path(args.bddl_root).resolve(strict=True)
    output = Path(args.output).resolve(strict=False)
    if not bddl_root.is_relative_to(root):
        raise RuntimeError("BDDL root must be below the personal root")
    if not output.is_relative_to(root) or output == root or output.suffix != ".npz":
        raise RuntimeError("output must be a .npz file below the personal root")
    for task in args.tasks:
        task_path = (bddl_root / task).resolve(strict=True)
        if not task_path.is_file() or not task_path.is_relative_to(root):
            raise RuntimeError(f"invalid personal BDDL task path: {task_path}")
    return bddl_root, output


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_array(value: np.ndarray) -> str:
    value = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(value.dtype).encode())
    digest.update(str(value.shape).encode())
    digest.update(value.tobytes())
    return digest.hexdigest()


def atomic_npz(path: Path, arrays: dict[str, np.ndarray], run_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{run_id}.tmp")
    try:
        with temporary.open("wb") as handle:
            np.savez_compressed(handle, **arrays)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_json(path: Path, payload: dict[str, Any], run_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{run_id}.tmp")
    serialized = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False)
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def package_version(name: str) -> str:
    import importlib.metadata

    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "editable-or-unregistered"


def reference_name(env: Any, goal_argument: str) -> str:
    suffixes = (
        "_left_contain_region", "_right_contain_region", "_front_contain_region",
        "_back_contain_region", "_contain_region", "_top_region", "_bottom_region",
        "_top_side",
    )
    for suffix in suffixes:
        if goal_argument.endswith(suffix):
            candidate = goal_argument[: -len(suffix)]
            if candidate in env.env.objects_dict:
                return candidate
            raise RuntimeError(f"E1 requires a movable reference object, got {candidate}")
    if goal_argument in env.env.objects_dict:
        return goal_argument
    raise RuntimeError(f"cannot resolve reference object from {goal_argument}")


def goal_spec(env: Any) -> tuple[str, str, str, str]:
    goals = env.env.parsed_problem["goal_state"]
    if len(goals) != 1 or goals[0][0] not in {"in", "on"}:
        raise RuntimeError(f"P1 expects one in/on predicate, got {goals}")
    relation, target, argument = goals[0]
    return relation, target, reference_name(env, argument), argument


def object_pose(env: Any, name: str) -> np.ndarray:
    obj = env.env.objects_dict[name]
    return np.asarray(env.sim.data.get_joint_qpos(obj.joints[0]), dtype=np.float64).copy()


def set_object_pose_preconstruction(env: Any, name: str, pose: np.ndarray) -> None:
    """The only direct object mutation in this collector; never call after snapshot."""
    obj = env.env.objects_dict[name]
    env.sim.data.set_joint_qpos(obj.joints[0], np.asarray(pose, dtype=np.float64))


def instance_ids(env: Any) -> dict[str, int]:
    if not env.instance_to_id:
        raise RuntimeError("SegmentationRenderEnv instance mapping is empty")
    return {str(name): int(value) for name, value in env.instance_to_id.items()}


class ObservableModes:
    def __init__(self, core: Any):
        self.core = core
        self.original = {
            name: (observable.is_enabled(), observable.is_active())
            for name, observable in core._observables.items()
        }
        missing = [name for name in REQUIRED_PROPRIO if name not in self.original]
        if missing:
            raise RuntimeError(f"missing registered robot observables: {missing}")

    def trace(self) -> None:
        for name in self.original:
            keep = name in REQUIRED_PROPRIO
            self.core.modify_observable(name, "enabled", keep)
            self.core.modify_observable(name, "active", keep)
        self.core._obs_cache = {}

    def capture(self) -> None:
        for name, (enabled, active) in self.original.items():
            self.core.modify_observable(name, "enabled", enabled)
            self.core.modify_observable(name, "active", active)
        self.core._obs_cache = {}


def robot_vector(obs: dict[str, np.ndarray]) -> np.ndarray:
    values = []
    for key in REQUIRED_PROPRIO:
        if key not in obs:
            raise RuntimeError(f"missing robot-only trace field: {key}")
        value = np.asarray(obs[key], dtype=np.float64).reshape(-1)
        if not np.isfinite(value).all():
            raise RuntimeError(f"non-finite robot-only trace field: {key}")
        values.append(value)
    vector = np.concatenate(values)
    if vector.shape != (16,):
        raise RuntimeError(f"registered robot state must be 16-D, got {vector.shape}")
    return vector


def restore_canonical(env: Any, state: np.ndarray, modes: ObservableModes) -> dict[str, np.ndarray]:
    """Reset all controller/buffer/counter state, restore physics, and canonicalize OSC."""
    core = env.env
    modes.trace()
    core.deterministic_reset = True
    env.reset()
    core.sim.set_state_from_flattened(np.asarray(state, dtype=np.float64))
    core.sim.forward()
    core.cur_time = 0.0
    core.timestep = 0
    core.done = False
    for robot in core.robots:
        controller = robot.controller
        controller.update(force=True)
        current_joints = np.asarray(
            [core.sim.data.qpos[index] for index in robot._ref_joint_pos_indexes],
            dtype=np.float64,
        )
        controller.update_initial_joints(current_joints)
        controller.reset_goal()
    core._obs_cache = {}
    for observable in core._observables.values():
        observable.reset()
    obs = core._get_observations(force_update=True)
    restored = core.sim.get_state().flatten().copy()
    error = float(np.max(np.abs(restored - np.asarray(state))))
    if error > 1e-12:
        raise RuntimeError(f"canonical restore error {error}")
    robot_vector(obs)
    return obs


def capture(env: Any, modes: ObservableModes, height: int, width: int) -> dict[str, np.ndarray]:
    from robosuite.utils.camera_utils import get_camera_transform_matrix, get_real_depth_map

    modes.capture()
    obs = env.env._get_observations(force_update=True)
    rgb, depth, seg, pixel_to_world = [], [], [], []
    for camera_name, key in CAMERAS:
        raw_rgb = np.asarray(obs[f"{key}_image"])
        raw_depth = np.asarray(obs[f"{key}_depth"])
        raw_seg = np.asarray(obs[f"{key}_segmentation_instance"])
        if raw_rgb.shape != (height, width, 3) or raw_rgb.dtype != np.uint8:
            raise RuntimeError(f"invalid RGB capture for {key}: {raw_rgb.shape}/{raw_rgb.dtype}")
        if raw_depth.shape != (height, width, 1) or not np.isfinite(raw_depth).all():
            raise RuntimeError(f"invalid depth capture for {key}")
        if raw_seg.shape != (height, width, 1) or not np.issubdtype(raw_seg.dtype, np.integer):
            raise RuntimeError(f"invalid segmentation capture for {key}")
        metric = np.asarray(get_real_depth_map(env.sim, raw_depth), dtype=np.float32)
        transform = np.asarray(
            get_camera_transform_matrix(env.sim, camera_name, height, width), dtype=np.float64
        )
        inverse = np.linalg.inv(transform).astype(np.float32)
        if not np.isfinite(metric).all() or not np.isfinite(inverse).all():
            raise RuntimeError(f"non-finite metric geometry for {key}")
        rgb.append(raw_rgb.copy())
        depth.append(metric[..., 0])
        seg.append(raw_seg[..., 0].astype(np.int32))
        pixel_to_world.append(inverse)
    return {
        "rgb": np.stack(rgb),
        "depth": np.stack(depth),
        "seg": np.stack(seg),
        "pixel_to_world": np.stack(pixel_to_world),
    }


def settle(env: Any, modes: ObservableModes, steps: int) -> None:
    modes.trace()
    action = np.zeros(7, dtype=np.float32)
    for _ in range(steps):
        env.step(action)


def move_eef(
    env: Any,
    modes: ObservableModes,
    waypoint: np.ndarray,
    max_steps: int,
    tolerance_m: float = 0.012,
) -> tuple[bool, int, float]:
    modes.trace()
    last_error = float("inf")
    for step in range(max_steps):
        obs = env.env._get_observations(force_update=True)
        current = np.asarray(obs["robot0_eef_pos"], dtype=np.float64)
        error = np.asarray(waypoint, dtype=np.float64) - current
        last_error = float(np.linalg.norm(error))
        if last_error <= tolerance_m:
            return True, step, last_error
        action = np.zeros(7, dtype=np.float32)
        action[:3] = np.clip(error / 0.04, -1.0, 1.0).astype(np.float32)
        env.step(action)
    return False, max_steps, last_error


def goal_site_geometry(env: Any, argument: str, reference: str) -> tuple[np.ndarray, np.ndarray]:
    """Return the relation-valid center/extent for site or direct-object goals."""
    if argument in env.env.object_sites_dict:
        site_id = env.sim.model.site_name2id(argument)
        center = np.asarray(env.sim.data.site_xpos[site_id], dtype=np.float64).copy()
        rotation = np.asarray(env.sim.data.site_xmat[site_id], dtype=np.float64).reshape(3, 3)
        size = np.asarray(env.env.object_sites_dict[argument].size, dtype=np.float64)
        return center, np.abs(rotation @ size)
    if argument != reference or reference not in env.env.objects_dict:
        raise RuntimeError(f"goal argument is neither a known site nor reference object: {argument}")
    obj = env.env.objects_dict[reference]
    body_id = env.sim.model.body_name2id(obj.root_body)
    center = np.asarray(env.sim.data.body_xpos[body_id], dtype=np.float64).copy()
    # LIBERO ObjectState.check_ontop requires the two object centers to be
    # within 3 cm horizontally. This is the relation-valid extent, even when
    # the rendered support object is physically wider.
    relation_radius = min(float(getattr(obj, "horizontal_radius", 0.028)), 0.028)
    return center, np.asarray([relation_radius, relation_radius, 0.01], dtype=np.float64)


def discover_valid_placement_template(
    env: Any,
    modes: ObservableModes,
    base_state: np.ndarray,
    relation: str,
    target: str,
    reference: str,
    argument: str,
    placement_settle_steps: int,
) -> np.ndarray:
    restore_canonical(env, base_state, modes)
    center, _ = goal_site_geometry(env, argument, reference)
    original = object_pose(env, target)
    offsets = (
        (-0.06, -0.04, -0.02, 0.0, 0.02, 0.04, 0.06, 0.08)
        if relation == "in"
        else (0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10, 0.12, 0.15)
    )
    for offset in offsets:
        restore_canonical(env, base_state, modes)
        candidate = original.copy()
        candidate[:2] = center[:2]
        candidate[2] = center[2] + offset
        set_object_pose_preconstruction(env, target, candidate)
        env.sim.forward()
        settle(env, modes, placement_settle_steps)
        if bool(env.check_success()):
            settled_pose = object_pose(env, target)
            # Preserve both the stable vertical offset and the orientation
            # reached under physics. Reusing only z would reintroduce the
            # task's original, potentially unstable bowl/mug orientation.
            return np.concatenate(
                ([settled_pose[2] - center[2]], settled_pose[3:7])
            ).astype(np.float64)
    raise RuntimeError(f"could not discover relation-valid center height for {target}/{argument}")


def construct_prestate(
    env: Any,
    modes: ObservableModes,
    base_state: np.ndarray,
    target: str,
    reference: str,
    argument: str,
    direction: np.ndarray,
    margin_m: float,
    placement_template: np.ndarray,
    placement_settle_steps: int,
    approach_steps: int,
) -> tuple[np.ndarray | None, dict[str, Any]]:
    """Direct placement and robot approach; returns before the registered snapshot."""
    restore_canonical(env, base_state, modes)
    center, half_extent = goal_site_geometry(env, argument, reference)
    original = object_pose(env, target)
    active_axis = int(np.argmax(np.abs(direction)))
    offset_m = max(0.0, float(half_extent[active_axis]) - float(margin_m))
    candidate = original.copy()
    candidate[:2] = center[:2] + direction * offset_m
    candidate[2] = center[2] + float(placement_template[0])
    candidate[3:7] = np.asarray(placement_template[1:5], dtype=np.float64)
    set_object_pose_preconstruction(env, target, candidate)
    env.sim.forward()
    settle(env, modes, placement_settle_steps)
    if not bool(env.check_success()):
        return None, {"reason": "relation_invalid_after_placement_settle"}

    target_position = object_pose(env, target)[:3]
    obj = env.env.objects_dict[target]
    radius = float(np.clip(getattr(obj, "horizontal_radius", 0.035), 0.02, 0.08))
    side_xy = target_position[:2] - direction * (radius + 0.035)
    high = np.array([side_xy[0], side_xy[1], target_position[2] + 0.12])
    contact = np.array([side_xy[0], side_xy[1], target_position[2] + 0.015])
    ok_high, high_steps, high_error = move_eef(env, modes, high, approach_steps)
    ok_contact, contact_steps, contact_error = move_eef(env, modes, contact, approach_steps)
    settle(env, modes, 4)
    relation_after_approach = bool(env.check_success())
    diagnostics: dict[str, Any] = {
        "planned_margin_m": float(margin_m),
        "site_half_extent_m": float(half_extent[active_axis]),
        "placed_offset_m": float(offset_m),
        "approach_high_steps": float(high_steps),
        "approach_contact_steps": float(contact_steps),
        "approach_high_error_m": high_error,
        "approach_contact_error_m": contact_error,
        "approach_high_reached": bool(ok_high),
        "approach_contact_reached": bool(ok_contact),
        "relation_after_approach": relation_after_approach,
    }
    if not (ok_high and ok_contact and relation_after_approach):
        diagnostics["reason"] = "approach_or_postapproach_relation_failed"
        return None, diagnostics
    prestate = env.sim.get_state().flatten().copy()
    return prestate, diagnostics


def command_chunk(direction: np.ndarray, magnitude: float, push_steps: int, settle_steps: int) -> np.ndarray:
    commands = np.zeros((push_steps + settle_steps, 7), dtype=np.float32)
    commands[:push_steps, :2] = np.asarray(direction, dtype=np.float32) * float(magnitude)
    return commands


def execute_transition(
    env: Any,
    modes: ObservableModes,
    start_state: np.ndarray,
    commands: np.ndarray,
) -> dict[str, Any]:
    start_obs = restore_canonical(env, start_state, modes)
    initial_robot = robot_vector(start_obs)
    traces = []
    for command in commands:
        obs, _, _, _ = env.step(np.asarray(command, dtype=np.float32))
        state_delta = robot_vector(obs) - initial_robot
        traces.append(np.concatenate((np.asarray(command, dtype=np.float64), state_delta)))
    trace = np.stack(traces).astype(np.float32)
    if trace.shape != (16, 23) or not np.isfinite(trace).all():
        raise RuntimeError(f"invalid realized-kinematic trace: {trace.shape}")
    return {
        "trace": trace,
        "initial_robot": initial_robot.astype(np.float32),
        "final_state": env.sim.get_state().flatten().copy(),
        "relation_after": bool(env.check_success()),
    }


def visibility_bin(counts: dict[str, int]) -> int:
    count = min(counts["target_reduced"], counts["reference_reduced"])
    return 0 if count < 16 else 1 if count < 32 else 2 if count < 64 else 3


def collect(args: argparse.Namespace, bddl_root: Path, output: Path, run_id: str) -> dict[str, Any]:
    from libero.libero.envs import SegmentationRenderEnv
    import robosuite.utils.transform_utils as transform_utils

    transition: dict[str, list[np.ndarray]] = {}
    observation: dict[str, list[np.ndarray]] = {}
    supervision: dict[str, list[np.ndarray]] = {}
    matching: dict[str, list[np.ndarray]] = {}
    audit_uniform: dict[str, list[np.ndarray]] = {}
    audit_states: dict[str, np.ndarray] = {}
    samples: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    start_time = time.time()
    stop = False

    for task_index, task in enumerate(args.tasks):
        task_path = bddl_root / task
        env = SegmentationRenderEnv(
            bddl_file_name=str(task_path),
            camera_heights=args.height,
            camera_widths=args.width,
            camera_depths=True,
            camera_segmentations="instance",
        )
        try:
            env.seed(args.seed + task_index * 10000)
            env.reset()
            modes = ObservableModes(env.env)
            relation, target, reference, argument = goal_spec(env)
            ids = instance_ids(env)
            if target not in ids or reference not in ids:
                raise RuntimeError(f"instance IDs missing for {target}/{reference}")
            base_state = env.sim.get_state().flatten().copy()
            placement_template = discover_valid_placement_template(
                env, modes, base_state, relation, target, reference, argument,
                args.placement_settle_steps,
            )
            base_position = np.asarray(env.robots[0].base_pos, dtype=np.float64)
            base_rotation = transform_utils.quat2mat(np.asarray(env.robots[0].base_ori, dtype=np.float64))

            for action_index, (action_name, direction_values) in enumerate(ACTION_FAMILIES):
                direction = np.asarray(direction_values, dtype=np.float64)
                for margin_index, margin_m in enumerate(args.margins_m):
                    cell = {
                        "task": task,
                        "task_index": task_index,
                        "relation": relation,
                        "action_family": action_name,
                        "action_family_index": action_index,
                        "margin_index": margin_index,
                        "planned_margin_m": float(margin_m),
                    }
                    preconstruction_state, construction = construct_prestate(
                        env, modes, base_state, target, reference, argument, direction, margin_m,
                        placement_template, args.placement_settle_steps, args.approach_steps,
                    )
                    if preconstruction_state is None:
                        rejection = {**cell, **construction}
                        rejected.append(rejection)
                        print(json.dumps({"event": "rejected", **rejection}), flush=True)
                        continue

                    # Canonicalization marks the information boundary. No
                    # direct object mutation is permitted below this line.
                    start_obs = restore_canonical(env, preconstruction_state, modes)
                    transition_start = env.sim.get_state().flatten().copy()
                    if not bool(env.check_success()):
                        rejected.append({**cell, "reason": "relation_failed_after_canonicalization"})
                        continue
                    pre_target_pose = object_pose(env, target)
                    pre_reference_pose = object_pose(env, reference)
                    pre_capture = capture(env, modes, args.height, args.width)
                    pre_geometry, pre_counts = relation_geometry_54(
                        pre_capture["depth"], pre_capture["seg"], pre_capture["pixel_to_world"],
                        ids[target], ids[reference], base_position, base_rotation, relation,
                    )
                    commands = command_chunk(
                        direction, args.push_magnitude, args.push_steps, args.settle_steps
                    )
                    original = execute_transition(env, modes, transition_start, commands)
                    original_final_state = original["final_state"].copy()
                    original_relation_after = bool(original["relation_after"])
                    post_target_pose = object_pose(env, target)
                    post_reference_pose = object_pose(env, reference)
                    post_capture = capture(env, modes, args.height, args.width)
                    post_geometry, post_counts = relation_geometry_54(
                        post_capture["depth"], post_capture["seg"], post_capture["pixel_to_world"],
                        ids[target], ids[reference], base_position, base_rotation, relation,
                    )

                    replay = execute_transition(env, modes, transition_start, commands)
                    state_replay_error = float(
                        np.max(np.abs(original_final_state - replay["final_state"]))
                    )
                    trace_replay_error = float(
                        np.max(np.abs(original["trace"].astype(np.float64) - replay["trace"].astype(np.float64)))
                    )
                    relation_replay_match = original_relation_after == bool(replay["relation_after"])
                    if state_replay_error > 1e-10 or trace_replay_error > 1e-10 or not relation_replay_match:
                        rejected.append({
                            **cell,
                            "reason": "exact_replay_failed",
                            "state_replay_error": state_replay_error,
                            "trace_replay_error": trace_replay_error,
                        })
                        continue

                    sample_index = len(samples)
                    state_key = f"state_{sample_index:05d}"
                    audit_states[state_key] = transition_start.astype(np.float64)
                    label_invalidated = int(not original_relation_after)
                    transition_sample = {
                        "pre_relation_belief": np.asarray([1.0], dtype=np.float32),
                        "pre_geometry_54": pre_geometry,
                        "tau_cmd": commands,
                        "tau_kin": original["trace"],
                        "trace_mask": np.ones(16, dtype=np.bool_),
                        "relation_id": np.int8(0 if relation == "in" else 1),
                    }
                    observation_sample = {
                        "pre_rgb": pre_capture["rgb"],
                        "post_rgb": post_capture["rgb"],
                        "pre_depth": pre_capture["depth"],
                        "post_depth": post_capture["depth"],
                        "pre_seg": pre_capture["seg"],
                        "post_seg": post_capture["seg"],
                        "pre_pixel_to_world": pre_capture["pixel_to_world"],
                        "post_pixel_to_world": post_capture["pixel_to_world"],
                        "post_geometry_54": post_geometry,
                    }
                    supervision_sample = {
                        "label_invalidated": np.int64(label_invalidated),
                    }
                    matching_sample = {
                        "task_index": np.int16(task_index),
                        "action_family_index": np.int8(action_index),
                        "margin_bin": np.int8(min(margin_index // 4, 3)),
                        "post_visibility_bin": np.int8(visibility_bin(post_counts)),
                        "group_id": np.int64(sample_index),
                        "target_instance_id": np.int16(ids[target]),
                        "reference_instance_id": np.int16(ids[reference]),
                    }
                    for destination, values in (
                        (transition, transition_sample),
                        (observation, observation_sample),
                        (supervision, supervision_sample),
                        (matching, matching_sample),
                    ):
                        for key, value in values.items():
                            destination.setdefault(key, []).append(np.asarray(value))
                    audit_sample = {
                        "pre_target_pose": pre_target_pose,
                        "post_target_pose": post_target_pose,
                        "pre_reference_pose": pre_reference_pose,
                        "post_reference_pose": post_reference_pose,
                        "state_replay_error": np.float64(state_replay_error),
                        "trace_replay_error": np.float64(trace_replay_error),
                        "relation_before": np.bool_(True),
                        "relation_after": np.bool_(original_relation_after),
                        "relation_replay_match": np.bool_(relation_replay_match),
                        "planned_margin_m": np.float64(margin_m),
                        "pre_target_raw_visibility": np.int32(pre_counts["target_raw"]),
                        "pre_reference_raw_visibility": np.int32(pre_counts["reference_raw"]),
                        "post_target_raw_visibility": np.int32(post_counts["target_raw"]),
                        "post_reference_raw_visibility": np.int32(post_counts["reference_raw"]),
                        "initial_robot_state": original["initial_robot"],
                        "robot_base_position": base_position,
                        "robot_base_rotation": base_rotation,
                    }
                    for key, value in audit_sample.items():
                        audit_uniform.setdefault(key, []).append(np.asarray(value))
                    samples.append({
                        **cell,
                        **construction,
                        "sample_index": sample_index,
                        "state_key": state_key,
                        "transition_start_sha256": sha256_array(transition_start),
                        "target": target,
                        "reference": reference,
                        "goal_argument": argument,
                        "label_invalidated": label_invalidated,
                        "relation_after": original_relation_after,
                        "pre_visibility": pre_counts,
                        "post_visibility": post_counts,
                        "state_replay_error": state_replay_error,
                        "trace_replay_error": trace_replay_error,
                        "direct_mutation_after_snapshot": False,
                    })
                    print(json.dumps({
                        "event": "accepted",
                        "sample": sample_index,
                        "task": task_index,
                        "action": action_name,
                        "margin": margin_m,
                        "invalidated": label_invalidated,
                    }), flush=True)
                    if args.max_samples > 0 and len(samples) >= args.max_samples:
                        stop = True
                        break
                if stop:
                    break
            if stop:
                break
        finally:
            env.close()

    if not samples:
        raise RuntimeError("P1 collector accepted zero physics-mediated rollouts")
    transition_arrays = {key: np.stack(values) for key, values in transition.items()}
    observation_arrays = {key: np.stack(values) for key, values in observation.items()}
    supervision_arrays = {key: np.stack(values) for key, values in supervision.items()}
    matching_arrays = {key: np.stack(values) for key, values in matching.items()}
    transition_input_allowlist = {
        "pre_relation_belief", "pre_geometry_54", "tau_cmd", "tau_kin", "trace_mask", "relation_id"
    }
    if set(transition_arrays) != transition_input_allowlist:
        raise RuntimeError(
            f"transition archive role violation: {set(transition_arrays)} != {transition_input_allowlist}"
        )
    audit_arrays = {key: np.stack(values) for key, values in audit_uniform.items()}
    audit_arrays.update(audit_states)
    audit_arrays["audit_only_not_model_input"] = np.asarray(True)
    observation_path = output.with_suffix(".observation.npz")
    supervision_path = output.with_suffix(".supervision.npz")
    matching_path = output.with_suffix(".matching.npz")
    audit_path = output.with_suffix(".audit.npz")
    manifest_path = output.with_suffix(".manifest.json")
    atomic_npz(output, transition_arrays, run_id)
    atomic_npz(observation_path, observation_arrays, run_id)
    atomic_npz(supervision_path, supervision_arrays, run_id)
    atomic_npz(matching_path, matching_arrays, run_id)
    atomic_npz(audit_path, audit_arrays, run_id)

    labels = supervision_arrays["label_invalidated"].astype(np.int64)
    family_outcomes: dict[str, dict[str, int]] = {}
    for action_index, (action_name, _) in enumerate(ACTION_FAMILIES):
        mask = matching_arrays["action_family_index"] == action_index
        family_outcomes[action_name] = {
            "preserved": int(np.sum(mask & (labels == 0))),
            "invalidated": int(np.sum(mask & (labels == 1))),
        }
    manifest = {
        "schema_version": 1,
        "kind": "e1_p1_paired_physics_rollouts",
        "claim_limit": "Scripted LIBERO physics P1 only; not VLA-distribution, WAM gain, recovery, or closed-loop evidence.",
        "run_id": run_id,
        "complete": True,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": time.time() - start_time,
        "command": [str(value) for value in sys.argv],
        "script_sha256": sha256_file(Path(__file__).resolve(strict=True)),
        "geometry_sha256": sha256_file((Path(__file__).resolve().parent / "e1_geometry.py")),
        "transition_output": str(output),
        "transition_output_sha256": sha256_file(output),
        "transition_input_allowlist": sorted(transition_input_allowlist),
        "observation_output": str(observation_path),
        "observation_output_sha256": sha256_file(observation_path),
        "supervision_output": str(supervision_path),
        "supervision_output_sha256": sha256_file(supervision_path),
        "matching_output": str(matching_path),
        "matching_output_sha256": sha256_file(matching_path),
        "audit_output": str(audit_path),
        "audit_output_sha256": sha256_file(audit_path),
        "bddl_sha256": {task: sha256_file(bddl_root / task) for task in args.tasks},
        "tasks": list(args.tasks),
        "actions": [name for name, _ in ACTION_FAMILIES],
        "arguments": vars(args),
        "accepted_samples": len(samples),
        "rejected_attempts": len(rejected),
        "outcomes": {
            "preserved": int(np.sum(labels == 0)),
            "invalidated": int(np.sum(labels == 1)),
            "by_action_family": family_outcomes,
        },
        "role_shapes": {
            "transition": {key: list(value.shape) for key, value in transition_arrays.items()},
            "observation": {key: list(value.shape) for key, value in observation_arrays.items()},
            "supervision": {key: list(value.shape) for key, value in supervision_arrays.items()},
            "matching": {key: list(value.shape) for key, value in matching_arrays.items()},
            "audit": {key: list(value.shape) for key, value in audit_arrays.items()},
        },
        "role_dtypes": {
            "transition": {key: str(value.dtype) for key, value in transition_arrays.items()},
            "observation": {key: str(value.dtype) for key, value in observation_arrays.items()},
            "supervision": {key: str(value.dtype) for key, value in supervision_arrays.items()},
            "matching": {key: str(value.dtype) for key, value in matching_arrays.items()},
            "audit": {key: str(value.dtype) for key, value in audit_arrays.items()},
        },
        "samples": samples,
        "rejected": rejected,
        "information_boundary": {
            "direct_target_pose_mutation": "preconstruction_only",
            "post_snapshot_world_changes": "env.step_only",
            "tau_cmd": "exact_controls_passed_to_env.step",
            "tau_kin": "tau_cmd_plus_robot_only_delta_proprioception",
            "simulator_state": "separate_audit_npz_only",
        },
        "runtime": {
            "python": sys.version,
            "numpy": np.__version__,
            "libero": package_version("libero"),
            "robosuite": package_version("robosuite"),
            "MUJOCO_GL": os.environ.get("MUJOCO_GL"),
            "PYOPENGL_PLATFORM": os.environ.get("PYOPENGL_PLATFORM"),
        },
    }
    atomic_json(manifest_path, manifest, run_id)
    return {
        "transition": str(output),
        "observation": str(observation_path),
        "supervision": str(supervision_path),
        "matching": str(matching_path),
        "manifest": str(manifest_path),
        "audit": str(audit_path),
        "accepted": len(samples),
        "preserved": int(np.sum(labels == 0)),
        "invalidated": int(np.sum(labels == 1)),
        "elapsed_seconds": manifest["elapsed_seconds"],
    }


def main() -> None:
    args = parse_args()
    bddl_root, output = resolve_contract(args)
    run_id = f"e1p1-{uuid.uuid4().hex}"
    result = collect(args, bddl_root, output, run_id)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
