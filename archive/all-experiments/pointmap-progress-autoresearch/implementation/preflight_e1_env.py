"""E1 environment / robot-trace engineering preflight.

This script is deliberately narrower than an experiment. It verifies that a
LIBERO transition can be replayed from a fully reset controller state, that
the claim-bearing trace contains robot-only proprioception, and that two-view
RGB-D / instance observations are captured only after the final trace entry.
It does not test a WAM, a VLA, task success, or a physics outcome claim.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys
from typing import Any
import uuid

import numpy as np


DEFAULT_TASK = "LIVING_ROOM_SCENE1_pick_up_the_alphabet_soup_and_put_it_in_the_basket.bddl"
CAMERAS = (("agentview", "agentview"), ("robot0_eye_in_hand", "robot0_eye_in_hand"))
REQUIRED_PROPRIO = (
    "robot0_eef_pos",
    "robot0_eef_quat",
    "robot0_gripper_qpos",
    "robot0_joint_pos",
)
PERSONAL_ROOT = Path("<PERSONAL_RESEARCH_ROOT_ALIAS>")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bddl-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--task", default=DEFAULT_TASK)
    parser.add_argument("--height", type=int, default=96)
    parser.add_argument("--width", type=int, default=96)
    parser.add_argument("--seed", type=int, default=20260830)
    parser.add_argument("--steps", type=int, default=4)
    return parser.parse_args()


def resolve_safe_output(raw_output: str) -> Path:
    """Resolve the only writable artifact path before any fallible preflight work."""
    personal_root = PERSONAL_ROOT.resolve(strict=True)
    output_path = Path(raw_output).resolve(strict=False)
    if not output_path.is_relative_to(personal_root) or output_path == personal_root:
        raise RuntimeError(f"output must be a file below personal root: {personal_root}")
    return output_path


def require_runtime_contract(args: argparse.Namespace) -> Path:
    """Validate OSMesa and the BDDL path before importing MuJoCo/LIBERO."""
    if os.environ.get("MUJOCO_GL", "").casefold() != "osmesa":
        raise RuntimeError("MUJOCO_GL=osmesa is required before process start")
    if os.environ.get("PYOPENGL_PLATFORM", "").casefold() != "osmesa":
        raise RuntimeError("PYOPENGL_PLATFORM=osmesa is required before process start")
    if args.steps <= 0 or args.height <= 0 or args.width <= 0:
        raise ValueError("steps, height, and width must be positive")

    personal_root = PERSONAL_ROOT.resolve(strict=True)
    bddl_path = (Path(args.bddl_root).resolve(strict=True) / args.task).resolve(strict=True)
    if not bddl_path.is_relative_to(personal_root) or not bddl_path.is_file():
        raise RuntimeError(f"BDDL must be a file below personal root: {personal_root}")
    return bddl_path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "editable-or-unregistered"


def atomic_write_json(path: Path, payload: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False)
    temporary = path.with_name(f".{path.name}.{payload['run_id']}.{os.getpid()}.tmp")
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return serialized


def camera_observables(core: Any) -> list[str]:
    names = [name for name, observable in core._observables.items() if observable.modality == "image"]
    if not names:
        raise RuntimeError("no image-modality observables were registered")
    return names


def set_camera_observables(core: Any, names: list[str], enabled: bool) -> None:
    for name in names:
        core.modify_observable(name, "enabled", enabled)
        core.modify_observable(name, "active", enabled)
    core._obs_cache = {}


def action_dim(env: Any) -> int:
    value = getattr(env.env, "action_dim", None)
    if value is not None:
        return int(value)
    low, _ = env.env.action_spec
    return int(len(low))


def restore_transition_start(
    env: Any,
    start_state: np.ndarray,
    camera_names: list[str],
) -> tuple[float, dict[str, np.ndarray]]:
    """Reset counters, observables, robots, and controllers, then restore physics."""
    core = env.env
    set_camera_observables(core, camera_names, enabled=False)
    core.deterministic_reset = True
    env.reset()
    core.sim.set_state_from_flattened(start_state)
    core.sim.forward()
    restored = core.sim.get_state().flatten().copy()
    restore_error = float(np.max(np.abs(restored - start_state)))
    start_obs = core._get_observations(force_update=True)
    leaked = [name for name in camera_names if name in start_obs]
    if leaked:
        raise RuntimeError(f"camera observables remained active during trace restore: {leaked}")
    return restore_error, start_obs


def validate_proprio_step(
    obs: dict[str, np.ndarray],
    expected_shapes: dict[str, tuple[int, ...]],
) -> dict[str, np.ndarray]:
    step: dict[str, np.ndarray] = {}
    for key in REQUIRED_PROPRIO:
        if key not in obs:
            raise RuntimeError(f"missing trace field after action: {key}")
        raw = np.asarray(obs[key])
        if raw.shape != expected_shapes[key]:
            raise RuntimeError(f"trace shape changed for {key}: {raw.shape} != {expected_shapes[key]}")
        if not np.issubdtype(raw.dtype, np.number) or np.issubdtype(raw.dtype, np.complexfloating):
            raise RuntimeError(f"trace dtype is not real numeric for {key}: {raw.dtype}")
        if not np.isfinite(raw).all():
            raise RuntimeError(f"non-finite trace value in {key}")
        step[key] = raw.copy()
    return step


def capture(
    env: Any,
    camera_names: list[str],
    height: int,
    width: int,
    events: list[str],
) -> tuple[dict[str, np.ndarray], dict[str, dict[str, bool]], dict[str, str]]:
    """Enable cameras and synchronously capture one internally consistent state."""
    from robosuite.utils.camera_utils import get_camera_transform_matrix, get_real_depth_map

    core = env.env
    set_camera_observables(core, camera_names, enabled=True)
    events.append("camera_observables_enabled")
    obs = core._get_observations(force_update=True)
    events.append("post_observation_captured")

    rgb, depth, seg, pixel_to_world = [], [], [], []
    per_view: dict[str, dict[str, bool]] = {}
    raw_dtypes: dict[str, str] = {}
    for camera_name, key in CAMERAS:
        raw_rgb = np.asarray(obs[f"{key}_image"])
        raw_depth = np.asarray(obs[f"{key}_depth"])
        raw_seg = np.asarray(obs[f"{key}_segmentation_instance"])
        raw_dtypes[f"{key}_image"] = str(raw_rgb.dtype)
        raw_dtypes[f"{key}_depth"] = str(raw_depth.dtype)
        raw_dtypes[f"{key}_segmentation_instance"] = str(raw_seg.dtype)
        checks = {
            "rgb_shape": raw_rgb.shape == (height, width, 3),
            "rgb_uint8": raw_rgb.dtype == np.uint8,
            "rgb_finite": bool(np.isfinite(raw_rgb).all()),
            "depth_shape": raw_depth.shape == (height, width, 1),
            "depth_real_float": bool(
                np.issubdtype(raw_depth.dtype, np.floating)
                and not np.issubdtype(raw_depth.dtype, np.complexfloating)
            ),
            "depth_finite": bool(np.isfinite(raw_depth).all()),
            "seg_shape": raw_seg.shape == (height, width, 1),
            "seg_integer": bool(np.issubdtype(raw_seg.dtype, np.integer)),
            "seg_finite": bool(np.isfinite(raw_seg).all()),
            "seg_has_foreground": bool(np.any(raw_seg > 0)),
        }
        per_view[key] = checks
        if not all(checks.values()):
            raise RuntimeError(f"invalid raw render for {key}: {checks}")

        metric = np.asarray(get_real_depth_map(core.sim, raw_depth))
        if metric.shape != (height, width, 1) or not np.isfinite(metric).all():
            raise RuntimeError(f"invalid metric depth for {key}: {metric.shape}")
        world_to_pixel = np.asarray(
            get_camera_transform_matrix(core.sim, camera_name, height, width)
        )
        inverse = np.linalg.inv(world_to_pixel)
        if world_to_pixel.shape != (4, 4) or not np.isfinite(inverse).all():
            raise RuntimeError(f"invalid camera transform for {key}")

        rgb.append(raw_rgb.copy())
        depth.append(metric[..., 0].astype(np.float32))
        seg.append(raw_seg[..., 0].astype(np.int32))
        pixel_to_world.append(inverse.astype(np.float32))
    return (
        {
            "rgb": np.stack(rgb),
            "depth": np.stack(depth),
            "seg": np.stack(seg),
            "pixel_to_world": np.stack(pixel_to_world),
        },
        per_view,
        raw_dtypes,
    )


def rollout(
    env: Any,
    start_state: np.ndarray,
    actions: np.ndarray,
    camera_names: list[str],
    expected_shapes: dict[str, tuple[int, ...]],
    capture_post: bool,
    height: int,
    width: int,
) -> dict[str, Any]:
    events: list[str] = []
    restore_error, start_obs = restore_transition_start(env, start_state, camera_names)
    events.append("transition_start_restored")
    validate_proprio_step(start_obs, expected_shapes)
    trace: list[dict[str, np.ndarray]] = []
    for index, action in enumerate(actions):
        obs, _, _, _ = env.step(np.asarray(action, dtype=np.float32))
        events.append(f"action_{index}_applied")
        trace.append(validate_proprio_step(obs, expected_shapes))
        events.append(f"proprio_{index}_captured")

    rendered = None
    view_checks = None
    raw_render_dtypes = None
    if capture_post:
        rendered, view_checks, raw_render_dtypes = capture(
            env, camera_names, height, width, events
        )
    return {
        "final_state": env.sim.get_state().flatten().copy(),
        "restore_error": restore_error,
        "trace": trace,
        "rendered": rendered,
        "view_checks": view_checks,
        "raw_render_dtypes": raw_render_dtypes,
        "events": events,
    }


def max_trace_error(
    first: list[dict[str, np.ndarray]],
    second: list[dict[str, np.ndarray]],
) -> float:
    return float(
        max(
            np.max(np.abs(first[step][key].astype(np.float64) - second[step][key].astype(np.float64)))
            for step in range(len(first))
            for key in REQUIRED_PROPRIO
        )
    )


def trace_precedes_post_observation(events: list[str], steps: int) -> bool:
    expected_tail = ["camera_observables_enabled", "post_observation_captured"]
    return bool(
        len(events) >= 2
        and events[-2:] == expected_tail
        and all(events.index(f"proprio_{index}_captured") < len(events) - 2 for index in range(steps))
    )


def run_preflight(
    args: argparse.Namespace,
    bddl_path: Path,
    output_path: Path,
    run_id: str,
    started_at: str,
) -> dict[str, Any]:
    # Imports occur only after require_runtime_contract has checked OSMesa.
    from libero.libero.envs import SegmentationRenderEnv
    from OpenGL import platform as opengl_platform

    env = SegmentationRenderEnv(
        bddl_file_name=str(bddl_path),
        camera_heights=args.height,
        camera_widths=args.width,
        camera_depths=True,
        camera_segmentations="instance",
    )
    try:
        env.seed(args.seed)
        reset_obs = env.reset()
        initial_state = env.sim.get_state().flatten().copy()
        observed_keys = sorted(str(key) for key in reset_obs)
        missing = [key for key in REQUIRED_PROPRIO if key not in reset_obs]
        if missing:
            raise RuntimeError(f"missing required robot-only proprioception: {missing}")
        expected_shapes = {key: np.asarray(reset_obs[key]).shape for key in REQUIRED_PROPRIO}
        expected_dtypes = {key: str(np.asarray(reset_obs[key]).dtype) for key in REQUIRED_PROPRIO}
        dim = action_dim(env)
        if dim != 7:
            raise RuntimeError(f"registered E1 assumes a 7-D action, got {dim}")
        action_low, action_high = (np.asarray(part) for part in env.env.action_spec)
        if action_low.shape != (dim,) or action_high.shape != (dim,):
            raise RuntimeError("unexpected action_spec shape")

        image_observables = camera_observables(env.env)
        zeros = np.zeros((args.steps, dim), dtype=np.float32)
        commands = np.zeros((args.steps, dim), dtype=np.float32)
        commands[:, 0] = 0.20

        zero_a = rollout(
            env, initial_state, zeros, image_observables, expected_shapes, False, args.height, args.width
        )
        zero_b = rollout(
            env, initial_state, zeros, image_observables, expected_shapes, False, args.height, args.width
        )
        # Capture must remain paired with rollout A's simulator state. Therefore
        # action A captures immediately, before action B is restored or executed.
        action_a = rollout(
            env, initial_state, commands, image_observables, expected_shapes, True, args.height, args.width
        )
        action_b = rollout(
            env, initial_state, commands, image_observables, expected_shapes, False, args.height, args.width
        )

        zero_state_error = float(
            np.max(np.abs(zero_a["final_state"] - zero_b["final_state"]))
        )
        action_state_error = float(
            np.max(np.abs(action_a["final_state"] - action_b["final_state"]))
        )
        zero_trace_error = max_trace_error(zero_a["trace"], zero_b["trace"])
        action_trace_error = max_trace_error(action_a["trace"], action_b["trace"])
        restore_errors = [
            zero_a["restore_error"],
            zero_b["restore_error"],
            action_a["restore_error"],
            action_b["restore_error"],
        ]
        eef_start = np.asarray(reset_obs["robot0_eef_pos"], dtype=np.float64)
        eef_end = np.asarray(action_a["trace"][-1]["robot0_eef_pos"], dtype=np.float64)
        eef_displacement = float(np.linalg.norm(eef_end - eef_start))

        rendered = action_a["rendered"]
        assert rendered is not None
        render_shapes = {key: list(value.shape) for key, value in rendered.items()}
        actual_gl_platform = type(opengl_platform.PLATFORM).__name__
        render_context = type(env.sim._render_context_offscreen).__name__
        checks = {
            "required_proprio_present": not missing,
            "four_traces_fixed_shape_real_numeric_finite": True,
            "all_four_restore_errors_le_1e_12": max(restore_errors) <= 1e-12,
            "zero_action_state_replay_max_error_le_1e_10": zero_state_error <= 1e-10,
            "zero_action_trace_replay_max_error_le_1e_10": zero_trace_error <= 1e-10,
            "nonzero_action_state_replay_max_error_le_1e_10": action_state_error <= 1e-10,
            "nonzero_action_trace_replay_max_error_le_1e_10": action_trace_error <= 1e-10,
            "eef_displacement_gt_1e_5": eef_displacement > 1e-5,
            "each_view_raw_rgb_depth_seg_valid": bool(
                all(all(view.values()) for view in action_a["view_checks"].values())
            ),
            "two_view_metric_capture_shapes_valid": bool(
                rendered["rgb"].shape == (2, args.height, args.width, 3)
                and rendered["depth"].shape == (2, args.height, args.width)
                and rendered["seg"].shape == (2, args.height, args.width)
                and rendered["pixel_to_world"].shape == (2, 4, 4)
                and np.isfinite(rendered["depth"]).all()
                and np.isfinite(rendered["pixel_to_world"]).all()
            ),
            "post_observation_captured_after_final_trace": trace_precedes_post_observation(
                action_a["events"], args.steps
            ),
            "actual_pyopengl_platform_is_osmesa": "osmesa" in actual_gl_platform.casefold(),
            "output_and_bddl_resolve_under_personal_root": bool(
                output_path.is_relative_to(PERSONAL_ROOT.resolve(strict=True))
                and bddl_path.is_relative_to(PERSONAL_ROOT.resolve(strict=True))
            ),
        }
        return {
            "schema_version": 2,
            "kind": "e1_environment_trace_preflight",
            "claim_limit": "Engineering substrate only; no physics outcome, WAM, VLA, or closed-loop claim.",
            "run_id": run_id,
            "started_at_utc": started_at,
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "complete": True,
            "complete_semantics": "All registered preflight checks executed without an exception.",
            "pass": bool(all(checks.values())),
            "checks": checks,
            "resolved_bddl_path": str(bddl_path),
            "resolved_output_path": str(output_path),
            "task": args.task,
            "task_sha256": sha256_file(bddl_path),
            "script_sha256": sha256_file(Path(__file__).resolve(strict=True)),
            "seed": args.seed,
            "action_dim": dim,
            "action_spec": {"low": action_low.tolist(), "high": action_high.tolist()},
            "steps": args.steps,
            "commands": commands.tolist(),
            "required_proprio_shapes": {key: list(value) for key, value in expected_shapes.items()},
            "required_proprio_dtypes": expected_dtypes,
            "observed_keys": observed_keys,
            "image_observable_names": image_observables,
            "trace_capture_events": action_a["events"],
            "render_shapes": render_shapes,
            "raw_render_dtypes": action_a["raw_render_dtypes"],
            "per_view_raw_render_checks": action_a["view_checks"],
            "restore_max_errors": restore_errors,
            "zero_state_replay_max_error": zero_state_error,
            "zero_trace_replay_max_error": zero_trace_error,
            "action_state_replay_max_error": action_state_error,
            "action_trace_replay_max_error": action_trace_error,
            "eef_displacement_m": eef_displacement,
            "runtime": {
                "python": sys.version,
                "platform": platform.platform(),
                "numpy": np.__version__,
                "libero": package_version("libero"),
                "robosuite": package_version("robosuite"),
                "mujoco_py": package_version("mujoco-py"),
                "MUJOCO_GL": os.environ.get("MUJOCO_GL"),
                "PYOPENGL_PLATFORM": os.environ.get("PYOPENGL_PLATFORM"),
                "actual_pyopengl_platform": actual_gl_platform,
                "render_context": render_context,
            },
            "cli": [str(value) for value in sys.argv],
        }
    finally:
        env.close()


def main() -> None:
    args = parse_args()
    run_id = f"e1p0-{uuid.uuid4().hex}"
    started_at = datetime.now(timezone.utc).isoformat()
    try:
        output_path = resolve_safe_output(args.output)
    except Exception as error:
        # Refuse to write when the requested destination itself is outside the
        # personal root or cannot be resolved safely.
        payload = {
            "schema_version": 2,
            "kind": "e1_environment_trace_preflight",
            "run_id": run_id,
            "complete": False,
            "pass": False,
            "error_type": type(error).__name__,
            "error": str(error),
        }
        print(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False), flush=True)
        raise SystemExit(1)

    try:
        bddl_path = require_runtime_contract(args)
        success_payload = run_preflight(args, bddl_path, output_path, run_id, started_at)
        # Serialization and the atomic write are part of the preflight
        # transaction. If either fails, the exception path below replaces any
        # stale success artifact with a fixed, JSON-safe failure payload.
        serialized = atomic_write_json(output_path, success_payload)
        payload = success_payload
        exit_code = 0 if payload["pass"] else 2
    except Exception as error:
        payload = {
            "schema_version": 2,
            "kind": "e1_environment_trace_preflight",
            "claim_limit": "Engineering substrate only; exception before all checks completed.",
            "run_id": run_id,
            "started_at_utc": started_at,
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "complete": False,
            "complete_semantics": "False means at least one registered check did not execute.",
            "pass": False,
            "error_type": type(error).__name__,
            "error": str(error),
            "cli": [str(value) for value in sys.argv],
            "runtime_contract": {
                "MUJOCO_GL": os.environ.get("MUJOCO_GL"),
                "PYOPENGL_PLATFORM": os.environ.get("PYOPENGL_PLATFORM"),
            },
        }
        serialized = atomic_write_json(output_path, payload)
        exit_code = 1
    print(serialized, flush=True)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
