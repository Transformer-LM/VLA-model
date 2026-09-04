"""Collect controlled LIBERO relation events with RGB, depth, and PointMaps.

This is a representation/headroom pilot. Controlled simulator interventions
are recorded as interventions, not mislabeled as executed VLA actions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path

import numpy as np
from libero.libero.envs import SegmentationRenderEnv
from robosuite.utils.camera_utils import get_camera_transform_matrix, get_real_depth_map


LABELS = {"preserved": 0, "invalidated": 1, "unobservable": 2, "wrong_object": 3}
DECISIONS = {"continue": 0, "retract": 1, "reobserve": 2}
EVENTS = ("preserved", "comotion", "camera_shift", "invalidated", "unobservable", "wrong_object")
EVENT_IDS = {name: index for index, name in enumerate(EVENTS)}
CAMERAS = (("agentview", "agentview"), ("robot0_eye_in_hand", "robot0_eye_in_hand"))

DEFAULT_TASKS = (
    "LIVING_ROOM_SCENE1_pick_up_the_alphabet_soup_and_put_it_in_the_basket.bddl",
    "LIVING_ROOM_SCENE3_pick_up_the_ketchup_and_put_it_in_the_tray.bddl",
    "LIVING_ROOM_SCENE5_put_the_red_mug_on_the_left_plate.bddl",
    "KITCHEN_SCENE2_stack_the_black_bowl_at_the_front_on_the_black_bowl_in_the_middle.bddl",
    "KITCHEN_SCENE5_put_the_black_bowl_on_the_plate.bddl",
)
DEFAULT_TASK_FAMILY_IDS = (
    "packaged_food_in_basket",
    "condiment_in_tray",
    "mug_on_plate",
    "bowl_on_bowl_stack",
    "bowl_on_plate",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bddl-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--height", type=int, default=96)
    parser.add_argument("--width", type=int, default=96)
    parser.add_argument("--seeds-per-task", type=int, default=12)
    parser.add_argument("--seed", type=int, default=20260830)
    parser.add_argument("--settle-steps", type=int, default=20)
    parser.add_argument("--event-retries", type=int, default=8)
    parser.add_argument("--tasks", nargs="*", default=list(DEFAULT_TASKS))
    parser.add_argument("--task-family-ids", nargs="*", default=None)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def object_instance_ids(env: SegmentationRenderEnv) -> dict[str, int]:
    """Return LIBERO's authoritative observation instance-value mapping."""

    if not env.instance_to_id:
        raise RuntimeError("SegmentationRenderEnv did not initialize instance_to_id")
    return {str(name): int(value) for name, value in env.instance_to_id.items()}


def observation(env: SegmentationRenderEnv) -> dict[str, np.ndarray]:
    return env.env._get_observations(force_update=True)


def capture(env: SegmentationRenderEnv, obs: dict[str, np.ndarray], height: int, width: int) -> dict[str, np.ndarray]:
    rgbs, depths, segs, pixel_to_world = [], [], [], []
    for camera_name, key in CAMERAS:
        rgbs.append(np.asarray(obs[f"{key}_image"], dtype=np.uint8))
        depth = get_real_depth_map(env.sim, np.asarray(obs[f"{key}_depth"], dtype=np.float32))
        depths.append(depth[..., 0].astype(np.float32))
        segs.append(np.asarray(obs[f"{key}_segmentation_instance"], dtype=np.int16)[..., 0])
        world_to_pixel = get_camera_transform_matrix(env.sim, camera_name, height, width)
        pixel_to_world.append(np.linalg.inv(world_to_pixel).astype(np.float32))
    return {
        "rgb": np.stack(rgbs),
        "depth": np.stack(depths),
        "seg": np.stack(segs),
        "pixel_to_world": np.stack(pixel_to_world),
    }


def pose_of(env: SegmentationRenderEnv, object_name: str) -> np.ndarray:
    obj = env.env.objects_dict[object_name]
    return np.asarray(env.sim.data.get_joint_qpos(obj.joints[0]), dtype=np.float32).copy()


def set_pose(env: SegmentationRenderEnv, object_name: str, pose: np.ndarray) -> None:
    obj = env.env.objects_dict[object_name]
    env.sim.data.set_joint_qpos(obj.joints[0], np.asarray(pose, dtype=np.float64))


def settle(env: SegmentationRenderEnv, steps: int) -> dict[str, np.ndarray]:
    obs = observation(env)
    for _ in range(steps):
        obs, _, _, _ = env.step(np.zeros(7, dtype=np.float32))
    return obs


def reference_name(env: SegmentationRenderEnv, goal_argument: str) -> str:
    # Match the specific directional suffixes before the generic suffix.
    suffixes = (
        "_left_contain_region", "_right_contain_region", "_front_contain_region", "_back_contain_region",
        "_contain_region", "_top_region", "_bottom_region", "_top_side",
    )
    for suffix in suffixes:
        if goal_argument.endswith(suffix):
            candidate = goal_argument[: -len(suffix)]
            if candidate in env.env.objects_dict:
                return candidate
            raise RuntimeError(f"E0 requires a movable object reference, got fixture/unknown {candidate}")
    return goal_argument


def find_success_state(env: SegmentationRenderEnv, settle_steps: int) -> tuple[np.ndarray, str, str, str, str]:
    goal = env.env.parsed_problem["goal_state"]
    if len(goal) != 1 or goal[0][0] not in {"in", "on"}:
        raise RuntimeError(f"pilot expects one in/on goal, got {goal}")
    predicate, target, argument = goal[0]
    reference = reference_name(env, argument)
    initial = env.sim.get_state().flatten().copy()
    target_pose = pose_of(env, target)
    if predicate == "in":
        center = env.sim.data.site_xpos[env.sim.model.site_name2id(argument)].copy()
        offsets = (-0.08, -0.06, -0.04, -0.02, 0.0, 0.02, 0.04)
    else:
        try:
            center = env.sim.data.site_xpos[env.sim.model.site_name2id(argument)].copy()
        except ValueError:
            ref_obj = env.env.objects_dict[reference]
            center = env.sim.data.body_xpos[env.sim.model.body_name2id(ref_obj.root_body)].copy()
        offsets = (0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10, 0.12, 0.15)
    for dz in offsets:
        env.sim.set_state_from_flattened(initial)
        env.sim.forward()
        candidate = target_pose.copy()
        candidate[:2] = center[:2]
        candidate[2] = center[2] + dz
        set_pose(env, target, candidate)
        env.sim.forward()
        settle(env, settle_steps)
        if bool(env.check_success()):
            return env.sim.get_state().flatten().copy(), predicate, target, reference, argument
    raise RuntimeError(f"could not synthesize successful state for {goal}")


def movable(env: SegmentationRenderEnv, name: str) -> bool:
    return name in env.env.objects_dict and bool(env.env.objects_dict[name].joints)


def choose_distractor(env: SegmentationRenderEnv, target: str, reference: str) -> str | None:
    for name, obj in env.env.objects_dict.items():
        if name not in {target, reference} and obj.joints:
            return name
    return None


def translate(env: SegmentationRenderEnv, object_name: str, delta: np.ndarray) -> None:
    pose = pose_of(env, object_name)
    pose[:3] += np.asarray(delta, dtype=np.float32)
    set_pose(env, object_name, pose)


def visibility(seg: np.ndarray, instance_id: int) -> np.ndarray:
    return np.asarray([(frame == instance_id).sum() for frame in seg], dtype=np.int32)


def apply_target_mask(record: dict[str, np.ndarray], target_id: int) -> np.ndarray:
    # Sensor-side occlusion proxy: remove only the target evidence in the post frame.
    masks = []
    for camera_idx in range(record["seg"].shape[0]):
        mask = record["seg"][camera_idx] == target_id
        masks.append(mask.copy())
        record["rgb"][camera_idx][mask] = 0
        record["depth"][camera_idx][mask] = np.nan
        record["seg"][camera_idx][mask] = 0
    return np.stack(masks)


def event_sample(
    env: SegmentationRenderEnv,
    success_state: np.ndarray,
    event: str,
    target: str,
    reference: str,
    distractor: str | None,
    ids: dict[str, int],
    rng: np.random.Generator,
    height: int,
    width: int,
    settle_steps: int,
) -> tuple[dict[str, np.ndarray], dict[str, object]] | None:
    env.sim.set_state_from_flattened(success_state)
    env.sim.forward()
    pre_obs = observation(env)
    pre = capture(env, pre_obs, height, width)
    pre_target_pose = pose_of(env, target)
    if not movable(env, reference):
        raise RuntimeError(f"configured E0 reference must be movable: {reference}")
    pre_reference_pose = pose_of(env, reference)

    camera_backup = None
    scripted_delta = np.zeros(12, dtype=np.float32)
    intervention_actor = 0  # 0 none, 1 target, 2 target+reference, 3 distractor, 4 camera, 5 sensor mask
    if event == "preserved" or event == "unobservable":
        post_obs = settle(env, 2)
        label = "preserved" if event == "preserved" else "unobservable"
    elif event == "comotion":
        if not movable(env, reference):
            return None
        delta = np.array([rng.uniform(-0.04, 0.04), rng.uniform(-0.04, 0.04), 0.0], dtype=np.float32)
        translate(env, target, delta)
        translate(env, reference, delta)
        scripted_delta[:3] = delta
        scripted_delta[3:6] = delta
        intervention_actor = 2
        env.sim.forward()
        post_obs = settle(env, max(2, settle_steps // 4))
        label = "preserved"
    elif event == "camera_shift":
        camera_id = env.sim.model.camera_name2id("agentview")
        camera_backup = env.sim.model.cam_pos[camera_id].copy()
        camera_delta = np.array(
            [rng.uniform(-0.08, 0.08), rng.uniform(-0.08, 0.08), rng.uniform(-0.03, 0.05)]
        )
        env.sim.model.cam_pos[camera_id] += camera_delta
        scripted_delta[9:12] = camera_delta
        intervention_actor = 4
        env.sim.forward()
        post_obs = observation(env)
        label = "preserved"
    elif event == "invalidated":
        direction = rng.uniform(0.0, 2.0 * np.pi)
        magnitude = rng.uniform(0.18, 0.28)
        delta = np.array([magnitude * np.cos(direction), magnitude * np.sin(direction), 0.04], dtype=np.float32)
        translate(env, target, delta)
        scripted_delta[:3] = delta
        intervention_actor = 1
        env.sim.forward()
        post_obs = settle(env, max(3, settle_steps // 3))
        label = "invalidated"
    elif event == "wrong_object":
        if distractor is None:
            return None
        direction = rng.uniform(0.0, 2.0 * np.pi)
        magnitude = rng.uniform(0.12, 0.22)
        delta = np.array([magnitude * np.cos(direction), magnitude * np.sin(direction), 0.03], dtype=np.float32)
        translate(env, distractor, delta)
        scripted_delta[6:9] = delta
        intervention_actor = 3
        env.sim.forward()
        post_obs = settle(env, max(3, settle_steps // 3))
        label = "wrong_object"
    else:
        raise ValueError(event)

    post = capture(env, post_obs, height, width)
    occlusion_mask = np.zeros_like(post["seg"], dtype=bool)
    pre_occlusion_target_visibility = visibility(post["seg"], ids[target])
    if event == "unobservable":
        occlusion_mask = apply_target_mask(post, ids[target])
        intervention_actor = 5
        if int(occlusion_mask.sum()) == 0:
            return None
    post_target_pose = pose_of(env, target)
    post_reference_pose = pose_of(env, reference)
    relation_after = bool(env.check_success())
    if camera_backup is not None:
        camera_id = env.sim.model.camera_name2id("agentview")
        env.sim.model.cam_pos[camera_id] = camera_backup
        env.sim.forward()

    # Reject physics outcomes that contradict the intended controlled label.
    if label == "invalidated" and relation_after:
        return None
    if label in {"preserved", "unobservable", "wrong_object"} and not relation_after:
        return None

    sample = {
        "rgb": np.stack((pre["rgb"], post["rgb"])),
        "depth": np.stack((pre["depth"], post["depth"])),
        "seg": np.stack((pre["seg"], post["seg"])),
        "pixel_to_world": np.stack((pre["pixel_to_world"], post["pixel_to_world"])),
        "target_pose": np.stack((pre_target_pose, post_target_pose)),
        "reference_pose": np.stack((pre_reference_pose, post_reference_pose)),
        "target_visibility": np.stack((visibility(pre["seg"], ids[target]), visibility(post["seg"], ids[target]))),
        "reference_visibility": np.stack((visibility(pre["seg"], ids[reference]), visibility(post["seg"], ids[reference]))),
        "scripted_intervention_delta": scripted_delta,
        "intervention_actor": np.int8(intervention_actor),
        "event_id": np.int8(EVENT_IDS[event]),
        "occlusion_mask": occlusion_mask,
        "pre_occlusion_target_visibility": pre_occlusion_target_visibility,
        "not_executed_vla_actions": np.bool_(True),
        "label": np.int64(LABELS[label]),
        "decision_label": np.int64(
            DECISIONS["retract" if label == "invalidated" else "reobserve" if label == "unobservable" else "continue"]
        ),
        "target_id": np.int16(ids[target]),
        "reference_id": np.int16(ids[reference]),
    }
    meta = {"event": event, "label_name": label, "relation_after": relation_after, "distractor": distractor}
    return sample, meta


def main() -> None:
    args = parse_args()
    if args.seeds_per_task <= 0 or args.event_retries <= 0 or args.settle_steps < 0:
        raise ValueError("seeds-per-task/event-retries must be positive and settle-steps must be non-negative")
    if args.task_family_ids is None:
        task_family_ids = (
            list(DEFAULT_TASK_FAMILY_IDS)
            if list(args.tasks) == list(DEFAULT_TASKS)
            else [Path(task).stem for task in args.tasks]
        )
    else:
        task_family_ids = list(args.task_family_ids)
    if len(task_family_ids) != len(args.tasks) or len(set(task_family_ids)) != len(task_family_ids):
        raise ValueError("task-family-ids must provide one unique family ID per task")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    arrays: dict[str, list[np.ndarray]] = {}
    metadata: list[dict[str, object]] = []
    requested_grid: list[dict[str, object]] = []
    reset_seeds_by_task: dict[str, list[int]] = {}
    start = time.time()
    for task_index, (task_file, task_family_id) in enumerate(zip(args.tasks, task_family_ids)):
        bddl_path = Path(args.bddl_root) / task_file
        env = SegmentationRenderEnv(
            bddl_file_name=str(bddl_path),
            camera_heights=args.height,
            camera_widths=args.width,
            camera_depths=True,
            camera_segmentations="instance",
        )
        reset_seeds_by_task[task_file] = []
        for local_seed in range(args.seeds_per_task):
            reset_seed = args.seed + task_index * 10000 + local_seed
            reset_seeds_by_task[task_file].append(reset_seed)
            requested_grid.extend({"task": task_file, "seed": reset_seed, "event": event} for event in EVENTS)
            env.seed(reset_seed)
            env.reset()
            try:
                success_state, predicate, target, reference, goal_argument = find_success_state(env, args.settle_steps)
            except RuntimeError as exc:
                metadata.append({"task": task_file, "seed": reset_seed, "rejected": True, "reason": str(exc)})
                continue
            ids = object_instance_ids(env)
            if target not in ids or reference not in ids:
                metadata.append(
                    {
                        "task": task_file,
                        "seed": reset_seed,
                        "rejected": True,
                        "reason": f"authoritative instance mapping missing target/reference: {target}/{reference}",
                    }
                )
                continue
            distractor = choose_distractor(env, target, reference)
            for event in EVENTS:
                result = None
                for attempt in range(args.event_retries):
                    result = event_sample(
                        env,
                        success_state,
                        event,
                        target,
                        reference,
                        distractor,
                        ids,
                        rng,
                        args.height,
                        args.width,
                        args.settle_steps,
                    )
                    if result is not None:
                        break
                if result is None:
                    metadata.append(
                        {
                            "task": task_file,
                            "task_index": task_index,
                            "seed": reset_seed,
                            "event": event,
                            "rejected": True,
                            "attempts": args.event_retries,
                        }
                    )
                    continue
                sample, meta = result
                for key, value in sample.items():
                    arrays.setdefault(key, []).append(np.asarray(value))
                metadata.append(
                    {
                        "task": task_file,
                        "task_index": task_index,
                        "task_family_index": task_index,
                        "task_family_id": task_family_id,
                        "seed": reset_seed,
                        "predicate": predicate,
                        "target": target,
                        "reference": reference,
                        "goal_argument": goal_argument,
                        "rejected": False,
                        "attempts": attempt + 1,
                        **meta,
                    }
                )
        env.close()
    stacked = {key: np.stack(values) for key, values in arrays.items()}
    accepted_meta = [entry for entry in metadata if not entry.get("rejected", False)]
    stacked["task_index"] = np.asarray([entry["task_index"] for entry in accepted_meta], dtype=np.int16)
    stacked["task_family_index"] = np.asarray([entry["task_family_index"] for entry in accepted_meta], dtype=np.int16)
    stacked["seed"] = np.asarray([entry["seed"] for entry in accepted_meta], dtype=np.int64)
    stacked["dataset_claim_ceiling"] = np.asarray("controlled_representation_only_not_vla_actions")
    np.savez_compressed(output, **stacked)
    bddl_sha256 = {task: sha256_file(Path(args.bddl_root) / task) for task in args.tasks}
    requested_cells = {(item["task"], int(item["seed"]), item["event"]) for item in requested_grid}
    accepted_cells = {(item["task"], int(item["seed"]), item["event"]) for item in accepted_meta}
    grid_complete = requested_cells == accepted_cells and len(accepted_meta) == len(requested_cells)
    manifest = {
        "schema_version": 1,
        "kind": "controlled_relation_event_representation_pilot",
        "not_executed_vla_actions": True,
        "complete": grid_complete,
        "command": " ".join(os.sys.argv),
        "arguments": {
            "bddl_root": args.bddl_root,
            "height": args.height,
            "width": args.width,
            "seeds_per_task": args.seeds_per_task,
            "base_seed": args.seed,
            "settle_steps": args.settle_steps,
            "event_retries": args.event_retries,
            "tasks": list(args.tasks),
            "task_family_ids": task_family_ids,
        },
        "created_unix": time.time(),
        "elapsed_seconds": time.time() - start,
        "output": str(output),
        "output_sha256": sha256_file(output),
        "collector_sha256": sha256_file(Path(__file__)),
        "shape": {key: list(value.shape) for key, value in stacked.items()},
        "labels": LABELS,
        "decisions": DECISIONS,
        "events": EVENTS,
        "tasks": list(args.tasks),
        "task_family_ids": task_family_ids,
        "bddl_sha256": bddl_sha256,
        "seeds_per_task": args.seeds_per_task,
        "reset_seeds_by_task": reset_seeds_by_task,
        "requested_grid": requested_grid,
        "samples": accepted_meta,
        "all_attempts": metadata,
    }
    manifest_path = output.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(output),
                "manifest": str(manifest_path),
                "samples": len(accepted_meta),
                "elapsed_seconds": manifest["elapsed_seconds"],
                "complete": grid_complete,
            },
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
