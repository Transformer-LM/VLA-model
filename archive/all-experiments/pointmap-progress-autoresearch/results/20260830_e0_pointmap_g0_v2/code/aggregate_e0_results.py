"""Aggregate fold/seed E0 results and enforce the preregistered G0 gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np


METRICS = (
    "macro_f1", "invalidation_miss_rate_at_frr5", "invalidation_recall_at_frr5",
    "achieved_false_retraction_rate", "decision_error", "brier", "ece", "head_forward_latency_ms_per_sample",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--audit", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fold_cluster_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    folds = sorted({int(row["fold"]) for row in rows})
    output: dict[str, object] = {"folds": folds, "runs": len(rows), "fold_values": {}}
    for metric in METRICS:
        fold_values = [
            float(np.mean([float(row[metric]) for row in rows if int(row["fold"]) == fold])) for fold in folds
        ]
        array = np.asarray(fold_values, dtype=np.float64)
        mean = float(np.mean(array))
        std = float(np.std(array, ddof=1)) if len(array) > 1 else 0.0
        critical = 2.776 if len(array) == 5 else 1.96
        output[f"{metric}_mean"] = mean
        output[f"{metric}_ci95"] = float(critical * std / math.sqrt(len(array))) if len(array) > 1 else 0.0
        output["fold_values"][metric] = fold_values
    output["parameters"] = int(rows[0]["parameters"])
    return output


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.dataset)
    dataset_hash = sha256_file(dataset_path)
    manifest_path = Path(args.manifest)
    audit_path = Path(args.audit)
    manifest_hash = sha256_file(manifest_path)
    audit_hash = sha256_file(audit_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    task_family_ids = list(manifest.get("task_family_ids", []))
    if (
        not bool(audit.get("pass", False))
        or audit.get("dataset_sha256") != dataset_hash
        or audit.get("manifest_sha256") != manifest_hash
        or manifest.get("output_sha256") != dataset_hash
    ):
        raise RuntimeError("G0 aggregation requires an exact matching passing B0 audit and manifest")
    if len(task_family_ids) != 5 or len(set(task_family_ids)) != 5:
        raise RuntimeError(f"G0 requires five explicit unique task families, got {task_family_ids}")
    rows: list[dict[str, object]] = []
    source_hashes: dict[str, str] = {}
    trainer_hashes: set[str] = set()
    geometry_hashes: set[str] = set()
    config_hashes: set[str] = set()
    for path_string in args.inputs:
        path = Path(path_string)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if (
            not bool(payload.get("complete", False))
            or payload.get("dataset_sha256") != dataset_hash
            or payload.get("manifest_sha256") != manifest_hash
            or payload.get("audit_sha256") != audit_hash
        ):
            raise RuntimeError(f"dataset/audit/manifest/completion mismatch in {path}")
        trainer_hashes.add(str(payload.get("trainer_sha256")))
        geometry_hashes.add(str(payload.get("geometry_sha256")))
        payload_config = payload.get("common_config", {})
        payload_config_hash = hashlib.sha256(json.dumps(payload_config, sort_keys=True).encode("utf-8")).hexdigest()
        if (
            payload_config_hash != payload.get("common_config_sha256")
            or payload_config.get("task_family_ids") != task_family_ids
            or payload_config.get("task_family_indices") != [0, 1, 2, 3, 4]
        ):
            raise RuntimeError(f"task-family or common-config provenance mismatch in {path}")
        config_hashes.add(str(payload.get("common_config_sha256")))
        source_hashes[str(path)] = sha256_file(path)
        rows.extend(payload["runs"])
    if len(trainer_hashes) != 1 or len(geometry_hashes) != 1 or len(config_hashes) != 1:
        raise RuntimeError(
            f"mixed trainer/geometry/config hashes: trainer={trainer_hashes}, geometry={geometry_hashes}, config={config_hashes}"
        )
    modalities = sorted({str(row["modality"]) for row in rows})
    required = {"rgb_addressed", "depth_addressed", "pointmap", "oracle_pose"}
    if set(modalities) != required:
        raise RuntimeError(f"modalities mismatch: {modalities}")
    expected_keys = {(modality, fold, seed) for modality in required for fold in range(5) for seed in (17, 29, 43)}
    observed_keys = [(str(row["modality"]), int(row["fold"]), int(row["seed"])) for row in rows]
    if len(observed_keys) != 60 or len(set(observed_keys)) != 60 or set(observed_keys) != expected_keys:
        raise RuntimeError(
            f"result grid must contain exactly 60 unique modality/fold/seed rows; got rows={len(observed_keys)}, unique={len(set(observed_keys))}"
        )
    for row in rows:
        fold = int(row["fold"])
        expected_test = fold
        expected_val = (fold + 1) % 5
        expected_train = sorted(set(range(5)) - {expected_test, expected_val})
        if (
            int(row["test_task_family"]) != expected_test
            or int(row["val_task_family"]) != expected_val
            or sorted(int(value) for value in row["train_task_families"]) != expected_train
            or int(row["train_samples"]) != 216
            or int(row["val_samples"]) != 72
            or int(row["test_samples"]) != 72
        ):
            raise RuntimeError(f"invalid task rotation or split size in row {row}")
        for metric in METRICS:
            if not np.isfinite(float(row[metric])):
                raise RuntimeError(f"nonfinite metric {metric} in row {row}")
    summaries = {
        modality: fold_cluster_summary([row for row in rows if row["modality"] == modality]) for modality in modalities
    }

    loaded = np.load(dataset_path, allow_pickle=False)
    _, time_dim, camera_dim, height, width = loaded["depth"].shape
    verifier_tensor_bytes = {
        "rgb_addressed": int(time_dim * camera_dim * 5 * height * width * 4),
        "depth_addressed": int(time_dim * camera_dim * 3 * height * width * 4),
        "pointmap": int(112 * 4),
        "oracle_pose": int(48 * 4),
    }
    point = summaries["pointmap"]
    depth = summaries["depth_addressed"]
    oracle = summaries["oracle_pose"]
    conditions = {
        "oracle_macro_f1_ge_0_75": oracle["macro_f1_mean"] >= 0.75,
        "oracle_frr_le_0_05": oracle["achieved_false_retraction_rate_mean"] <= 0.05 + 1e-12,
        "pointmap_imr_within_depth_plus_0_05": point["invalidation_miss_rate_at_frr5_mean"] <= depth["invalidation_miss_rate_at_frr5_mean"] + 0.05,
        "pointmap_macro_f1_within_depth_minus_0_03": point["macro_f1_mean"] >= depth["macro_f1_mean"] - 0.03,
        "pointmap_input_at_least_10x_smaller": verifier_tensor_bytes["pointmap"] * 10 <= verifier_tensor_bytes["depth_addressed"],
    }
    gate_pass = all(conditions.values())
    if not conditions["oracle_macro_f1_ge_0_75"] or not conditions["oracle_frr_le_0_05"]:
        interpretation = "PIPELINE_OR_TASK_DESIGN_FAILURE"
    elif gate_pass:
        interpretation = "POINTMAP_HEADROOM_PASS_ORACLE_MASKS_ONLY"
    else:
        interpretation = "STOP_POINTMAP_DOES_NOT_MATCH_COMPLETE_DEPTH"
    output = {
        "schema_version": 1,
        "kind": "e0_representation_gate",
        "dataset": str(dataset_path),
        "dataset_sha256": dataset_hash,
        "manifest_sha256": manifest_hash,
        "audit_sha256": audit_hash,
        "aggregator_sha256": sha256_file(Path(__file__)),
        "trainer_sha256": next(iter(trainer_hashes)),
        "geometry_sha256": next(iter(geometry_hashes)),
        "common_config_sha256": next(iter(config_hashes)),
        "source_result_sha256": source_hashes,
        "complete": True,
        "task_cluster_unit": True,
        "task_family_ids": task_family_ids,
        "summaries": summaries,
        "verifier_tensor_bytes_float32": verifier_tensor_bytes,
        "efficiency_scope": "Head input tensor and head forward only; excludes RGB-D sensing, instance association, and PointMap projection.",
        "gate": {"pass": gate_pass, "conditions": conditions, "interpretation": interpretation},
        "claim_limit": "Even a pass establishes only simulator-depth/instance-mask PointMap headroom, not action-conditioned WAM value.",
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(output, indent=2, sort_keys=True, allow_nan=False)
    output_path.write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
