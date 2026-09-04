"""Deterministic integrity audit for the controlled E0 relation-event dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from geometry import masked_world_points, relation_pointmap_features


EVENTS = ("preserved", "comotion", "camera_shift", "invalidated", "unobservable", "wrong_object")
EVENT_IDS = {name: index for index, name in enumerate(EVENTS)}
EVENT_TO_LABEL = {"preserved": 0, "comotion": 0, "camera_shift": 0, "invalidated": 1, "unobservable": 2, "wrong_object": 3}
EVENT_TO_DECISION = {"preserved": 0, "comotion": 0, "camera_shift": 0, "invalidated": 1, "unobservable": 2, "wrong_object": 0}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-rigid-cloud-error-m", type=float, default=0.02)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def array_equal_with_nan(left: np.ndarray, right: np.ndarray) -> bool:
    return bool(np.array_equal(left, right, equal_nan=True))


def quaternion_wxyz_matrix(quaternion: np.ndarray) -> np.ndarray:
    """Convert MuJoCo free-joint wxyz orientation to a 3x3 rotation matrix."""

    w, x, y, z = np.asarray(quaternion, dtype=np.float64)
    norm = float(np.linalg.norm([w, x, y, z]))
    if norm <= 0.0:
        raise ValueError("zero-norm quaternion")
    w, x, y, z = np.asarray([w, x, y, z], dtype=np.float64) / norm
    return np.asarray(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ],
        dtype=np.float64,
    )


def rigid_cloud_alignment_error(before_points: np.ndarray, after_points: np.ndarray, poses: np.ndarray) -> float:
    """Median bidirectional cloud distance after applying the simulator rigid transform."""

    pre_pose, post_pose = np.asarray(poses[0], dtype=np.float64), np.asarray(poses[1], dtype=np.float64)
    pre_rotation = quaternion_wxyz_matrix(pre_pose[3:7])
    post_rotation = quaternion_wxyz_matrix(post_pose[3:7])
    before = np.asarray(before_points, dtype=np.float64)
    after = np.asarray(after_points, dtype=np.float64)
    # Deterministic subsampling keeps the audit bounded without introducing RNG.
    if len(before) > 512:
        before = before[np.linspace(0, len(before) - 1, 512, dtype=np.int64)]
    if len(after) > 512:
        after = after[np.linspace(0, len(after) - 1, 512, dtype=np.int64)]
    expected = post_pose[:3] + (post_rotation @ pre_rotation.T @ (before - pre_pose[:3]).T).T
    pairwise = np.linalg.norm(expected[:, None, :] - after[None, :, :], axis=-1)
    bidirectional = np.concatenate((pairwise.min(axis=1), pairwise.min(axis=0)))
    return float(np.median(bidirectional))


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.dataset)
    manifest_path = Path(args.manifest)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    archive = np.load(dataset_path, allow_pickle=False)
    data = {key: archive[key] for key in archive.files}
    sample_count = len(data["decision_label"])
    accepted = manifest["samples"]
    checks: dict[str, object] = {}
    failures: list[str] = []

    actual_hash = sha256_file(dataset_path)
    checks["dataset_sha256"] = actual_hash
    if actual_hash != manifest.get("output_sha256"):
        failures.append("dataset SHA-256 does not match collector manifest")
    if sample_count != len(accepted):
        failures.append(f"array/manifest accepted sample count mismatch: {sample_count} vs {len(accepted)}")
    required = {
        "rgb", "depth", "seg", "pixel_to_world", "target_pose", "reference_pose",
        "target_visibility", "reference_visibility", "label", "decision_label",
        "target_id", "reference_id", "task_index", "seed", "occlusion_mask",
        "not_executed_vla_actions", "event_id", "scripted_intervention_delta",
        "pre_occlusion_target_visibility", "intervention_actor", "dataset_claim_ceiling",
        "task_family_index",
    }
    missing = sorted(required - set(data))
    if missing:
        failures.append(f"missing arrays: {missing}")

    requested = {(item["task"], int(item["seed"]), item["event"]) for item in manifest.get("requested_grid", [])}
    accepted_cells = {(item["task"], int(item["seed"]), item["event"]) for item in accepted}
    duplicate_cells = len(accepted) - len(accepted_cells)
    expected_count = 5 * 12 * len(EVENT_TO_LABEL)
    checks["requested_grid_count"] = len(requested)
    checks["accepted_grid_count"] = len(accepted_cells)
    checks["duplicate_grid_cells"] = duplicate_cells
    manifest_tasks = list(manifest.get("tasks", []))
    task_family_ids = list(manifest.get("task_family_ids", []))
    reset_seeds = manifest.get("reset_seeds_by_task", {})
    if (
        len(manifest_tasks) != 5
        or len(set(manifest_tasks)) != 5
        or len(task_family_ids) != 5
        or len(set(task_family_ids)) != 5
        or int(manifest.get("seeds_per_task", -1)) != 12
        or set(reset_seeds) != set(manifest_tasks)
        or any(len(values) != 12 or len(set(int(value) for value in values)) != 12 for values in reset_seeds.values())
    ):
        failures.append("registered E0 must contain exactly five tasks and 12 reset seeds per task")
    if len(requested) != expected_count or requested != accepted_cells or duplicate_cells:
        missing_cells = sorted(requested - accepted_cells)[:10]
        extra_cells = sorted(accepted_cells - requested)[:10]
        failures.append(
            f"incomplete/non-unique requested grid: expected={expected_count}, requested={len(requested)}, "
            f"accepted={len(accepted_cells)}, duplicates={duplicate_cells}, missing_head={missing_cells}, extra_head={extra_cells}"
        )
    if not bool(manifest.get("complete", False)) or not bool(manifest.get("not_executed_vla_actions", False)):
        failures.append("collector manifest completion or claim-ceiling flag missing")
    if not np.all(data["not_executed_vla_actions"]):
        failures.append("archive claim-ceiling flag is not true for every sample")
    if data["dataset_claim_ceiling"].shape != () or str(data["dataset_claim_ceiling"].item()) != "controlled_representation_only_not_vla_actions":
        failures.append("archive dataset claim ceiling is missing or incorrect")

    event_counts: dict[str, int] = {}
    relation_mismatches = 0
    label_mismatches = 0
    for index, meta in enumerate(accepted):
        event = str(meta["event"])
        event_counts[event] = event_counts.get(event, 0) + 1
        if (
            int(data["label"][index]) != EVENT_TO_LABEL[event]
            or int(data["decision_label"][index]) != EVENT_TO_DECISION[event]
            or int(data["task_index"][index]) != int(meta["task_index"])
            or int(data["task_family_index"][index]) != int(meta["task_family_index"])
            or int(data["seed"][index]) != int(meta["seed"])
            or manifest_tasks[int(data["task_index"][index])] != meta["task"]
            or task_family_ids[int(data["task_family_index"][index])] != meta["task_family_id"]
        ):
            label_mismatches += 1
        if bool(meta["relation_after"]) != (event != "invalidated"):
            relation_mismatches += 1
        if int(data["event_id"][index]) != EVENT_IDS[event]:
            label_mismatches += 1
    checks.update(event_counts=event_counts, label_mismatches=label_mismatches, relation_mismatches=relation_mismatches)
    if label_mismatches:
        failures.append(f"event/label mismatches: {label_mismatches}")
    if relation_mismatches:
        failures.append(f"event/relation predicate mismatches: {relation_mismatches}")

    group_indices: dict[tuple[int, int], list[int]] = {}
    for index in range(sample_count):
        group_indices.setdefault((int(data["task_index"][index]), int(data["seed"][index])), []).append(index)
    prestate_mismatches = 0
    for indices in group_indices.values():
        anchor = indices[0]
        for index in indices[1:]:
            for key in ("rgb", "depth", "seg", "pixel_to_world", "target_pose", "reference_pose"):
                if not array_equal_with_nan(data[key][anchor, 0], data[key][index, 0]):
                    prestate_mismatches += 1
                    break
    checks["same_prestate_group_count"] = len(group_indices)
    checks["prestate_mismatches"] = prestate_mismatches
    if prestate_mismatches:
        failures.append(f"controlled events do not share exact pre-state in {prestate_mismatches} comparisons")

    invalid_nan_samples = 0
    invalid_occlusion_samples = 0
    for index, meta in enumerate(accepted):
        nan_mask = ~np.isfinite(data["depth"][index])
        event = str(meta["event"])
        occlusion = data["occlusion_mask"][index].astype(bool)
        if np.any(nan_mask[0]) or not np.array_equal(nan_mask[1], occlusion):
            invalid_nan_samples += 1
        if event == "unobservable":
            if (
                int(occlusion.sum()) == 0
                or not np.array_equal(
                    occlusion.reshape(occlusion.shape[0], -1).sum(axis=1),
                    data["pre_occlusion_target_visibility"][index],
                )
                or np.any(data["rgb"][index, 1][occlusion] != 0)
                or np.any(data["seg"][index, 1][occlusion] != 0)
                or int(data["target_visibility"][index, 1].sum()) != 0
            ):
                invalid_occlusion_samples += 1
        elif (
            np.any(occlusion)
            or not np.array_equal(
                data["pre_occlusion_target_visibility"][index],
                data["target_visibility"][index, 1],
            )
        ):
            invalid_occlusion_samples += 1
    checks["invalid_nan_samples"] = invalid_nan_samples
    checks["invalid_occlusion_samples"] = invalid_occlusion_samples
    if invalid_nan_samples:
        failures.append(f"unexpected depth NaN pattern in {invalid_nan_samples} samples")
    if invalid_occlusion_samples:
        failures.append(f"invalid synthetic target-occlusion provenance in {invalid_occlusion_samples} samples")

    feature_invalid = 0
    association_mismatches = 0
    strata = {
        "comotion_target": [],
        "comotion_reference": [],
        "invalidated_target": [],
        "camera_shift_target": [],
        "camera_shift_reference": [],
    }
    coverage = {name: set() for name in strata}
    for index in range(sample_count):
        feature = relation_pointmap_features(
            data["depth"][index], data["seg"][index], data["pixel_to_world"][index],
            int(data["target_id"][index]), int(data["reference_id"][index]),
        )
        if feature.shape != (112,) or not np.isfinite(feature).all():
            feature_invalid += 1
        target_id = int(data["target_id"][index])
        reference_id = int(data["reference_id"][index])
        if target_id == reference_id:
            association_mismatches += 1
        for time_idx in range(2):
            observed_target = np.asarray([(data["seg"][index, time_idx, cam] == target_id).sum() for cam in range(2)])
            observed_reference = np.asarray([(data["seg"][index, time_idx, cam] == reference_id).sum() for cam in range(2)])
            if not np.array_equal(observed_target, data["target_visibility"][index, time_idx]):
                association_mismatches += 1
            if not np.array_equal(observed_reference, data["reference_visibility"][index, time_idx]):
                association_mismatches += 1
        if int(data["target_visibility"][index, 0].sum()) < 16 or int(data["reference_visibility"][index, 0].sum()) < 16:
            association_mismatches += 1
        event = str(accepted[index]["event"])
        for camera_idx in range(data["depth"].shape[2]):
            target_before = masked_world_points(
                data["depth"][index, 0, camera_idx], data["seg"][index, 0, camera_idx],
                target_id, data["pixel_to_world"][index, 0, camera_idx],
            )
            target_after = masked_world_points(
                data["depth"][index, 1, camera_idx], data["seg"][index, 1, camera_idx],
                target_id, data["pixel_to_world"][index, 1, camera_idx],
            )
            reference_before = masked_world_points(
                data["depth"][index, 0, camera_idx], data["seg"][index, 0, camera_idx],
                reference_id, data["pixel_to_world"][index, 0, camera_idx],
            )
            reference_after = masked_world_points(
                data["depth"][index, 1, camera_idx], data["seg"][index, 1, camera_idx],
                reference_id, data["pixel_to_world"][index, 1, camera_idx],
            )
            task_camera = (int(data["task_family_index"][index]), camera_idx)
            if len(target_before) >= 16 and len(target_after) >= 16:
                error = rigid_cloud_alignment_error(target_before, target_after, data["target_pose"][index])
                if event == "comotion":
                    strata["comotion_target"].append(error); coverage["comotion_target"].add(task_camera)
                elif event == "invalidated":
                    strata["invalidated_target"].append(error); coverage["invalidated_target"].add(task_camera)
                elif event == "camera_shift":
                    strata["camera_shift_target"].append(error); coverage["camera_shift_target"].add(task_camera)
            if len(reference_before) >= 16 and len(reference_after) >= 16:
                error = rigid_cloud_alignment_error(reference_before, reference_after, data["reference_pose"][index])
                if event == "comotion":
                    strata["comotion_reference"].append(error); coverage["comotion_reference"].add(task_camera)
                elif event == "camera_shift":
                    strata["camera_shift_reference"].append(error); coverage["camera_shift_reference"].add(task_camera)
    checks["feature_nonfinite_or_wrong_shape"] = feature_invalid
    if feature_invalid:
        failures.append(f"invalid 112D PointMap feature in {feature_invalid} samples")
    checks["association_mismatches"] = association_mismatches
    if association_mismatches:
        failures.append(f"target/reference mask association mismatches: {association_mismatches}")
    stratum_report = {}
    for name, values in strata.items():
        array = np.asarray(values, dtype=np.float64)
        median = float(np.median(array)) if len(array) else None
        task_coverage = {task for task, _ in coverage[name]}
        camera_coverage = {camera for _, camera in coverage[name]}
        required_camera_count = 1 if name == "invalidated_target" else 2
        stratum_report[name] = {
            "records": len(array),
            "task_camera_pair_coverage": len(coverage[name]),
            "covered_task_camera_pairs": [list(pair) for pair in sorted(coverage[name])],
            "task_coverage": len(task_coverage),
            "camera_coverage": len(camera_coverage),
            "median_rigid_cloud_error_m": median,
        }
        if (
            not len(array)
            or len(task_coverage) != 5
            or len(camera_coverage) < required_camera_count
            or len(coverage[name]) < 5
            or median is None
            or median > args.max_rigid_cloud_error_m
        ):
            failures.append(
                f"PointMap projection stratum {name} failed: records={len(array)}, "
                f"task_camera_pairs={len(coverage[name])}, tasks={len(task_coverage)}/5, "
                f"cameras={len(camera_coverage)}/{required_camera_count}, median={median}"
            )
    checks["pointmap_projection_strata"] = stratum_report

    task_counts = {str(task): int(np.sum(data["task_index"] == task)) for task in np.unique(data["task_index"])}
    task_family_counts = {
        str(family): int(np.sum(data["task_family_index"] == family)) for family in np.unique(data["task_family_index"])
    }
    decision_counts = {str(label): int(np.sum(data["decision_label"] == label)) for label in np.unique(data["decision_label"])}
    per_task_decisions = {
        str(task): {
            str(label): int(np.sum((data["task_index"] == task) & (data["decision_label"] == label))) for label in (0, 1, 2)
        }
        for task in np.unique(data["task_index"])
    }
    rejected_attempts = int(sum(bool(item.get("rejected", False)) for item in manifest["all_attempts"]))
    checks.update(
        task_counts=task_counts,
        task_family_counts=task_family_counts,
        task_family_ids=task_family_ids,
        decision_counts=decision_counts,
        per_task_decisions=per_task_decisions,
        sample_count=sample_count,
        task_family_count=len(task_counts),
        rejected_attempts=rejected_attempts,
    )
    if set(task_counts) != {"0", "1", "2", "3", "4"} or any(count != 72 for count in task_counts.values()):
        failures.append(f"task grid is not exactly five families × 72 events: {task_counts}")
    if set(task_family_counts) != {"0", "1", "2", "3", "4"} or any(count != 72 for count in task_family_counts.values()):
        failures.append(f"explicit task-family grid is not exactly five families × 72 events: {task_family_counts}")
    if any(set(counts) != {"0", "1", "2"} or min(counts.values()) <= 0 for counts in per_task_decisions.values()):
        failures.append(f"one or more task families lack a decision class: {per_task_decisions}")
    if set(decision_counts) != {"0", "1", "2"}:
        failures.append(f"decision classes incomplete: {decision_counts}")
    if rejected_attempts:
        failures.append(f"registered grid contains {rejected_attempts} rejected cells")

    report = {
        "schema_version": 1,
        "kind": "e0_controlled_dataset_audit",
        "dataset": str(dataset_path),
        "dataset_sha256": actual_hash,
        "manifest": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "auditor_sha256": sha256_file(Path(__file__)),
        "complete": True,
        "pass": not failures,
        "failures": failures,
        "checks": checks,
        "claim_limit": "This audit validates controlled representation data only, not VLA-action or WAM causality.",
    }
    serialized = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
    output_path.write_text(serialized, encoding="utf-8")
    print(serialized)
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
