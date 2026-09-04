"""Aggregate fold/seed E0 results and enforce the preregistered G0 gate."""

from __future__ import annotations

import argparse
import hashlib
import json
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
    parser.add_argument("--probe", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def macro_f1(labels: np.ndarray, predictions: np.ndarray) -> float:
    values = []
    for cls in range(3):
        tp = np.sum((labels == cls) & (predictions == cls))
        fp = np.sum((labels != cls) & (predictions == cls))
        fn = np.sum((labels == cls) & (predictions != cls))
        denom = 2 * tp + fp + fn
        values.append(0.0 if denom == 0 else float(2 * tp / denom))
    return float(np.mean(values))


def expected_calibration_error(probs: np.ndarray, labels: np.ndarray, bins: int = 10) -> float:
    confidence = probs.max(axis=1)
    predictions = probs.argmax(axis=1)
    value = 0.0
    for lower in np.linspace(0.0, 1.0, bins, endpoint=False):
        upper = lower + 1.0 / bins
        mask = (confidence >= lower) & (confidence < upper if upper < 1.0 else confidence <= upper)
        if np.any(mask):
            value += float(np.mean(mask)) * abs(
                float(np.mean(predictions[mask] == labels[mask])) - float(np.mean(confidence[mask]))
            )
    return float(value)


def classification_metrics(probs: np.ndarray, labels: np.ndarray) -> dict[str, float]:
    predictions = probs.argmax(axis=1)
    invalidated = labels == 1
    non_retract = labels != 1
    reobserve = labels == 2
    one_hot = np.eye(3, dtype=np.float32)[labels]
    return {
        "accuracy": float(np.mean(predictions == labels)),
        "macro_f1": macro_f1(labels, predictions),
        "invalidation_recall": float(np.mean(predictions[invalidated] == 1)),
        "false_retraction_rate": float(np.mean(predictions[non_retract] == 1)),
        "unobservable_reobserve_recall": float(np.mean(predictions[reobserve] == 2)),
        "decision_error": float(np.mean(predictions != labels)),
        "brier": float(np.mean(np.sum((probs - one_hot) ** 2, axis=1))),
        "ece": expected_calibration_error(probs, labels),
    }


def select_threshold(
    probs: np.ndarray,
    labels: np.ndarray,
    max_frr: float = 0.05,
) -> tuple[float, list[dict[str, float | bool]]]:
    score = probs[:, 1]
    no_retract = float(np.nextafter(float(np.max(score)), float("inf")))
    candidates = np.concatenate(([no_retract], np.unique(score)))
    best_threshold = no_retract
    best_recall = -1.0
    table: list[dict[str, float | bool]] = []
    for threshold in candidates:
        retracted = score >= threshold
        valid = labels != 1
        invalidated = labels == 1
        frr = float(np.mean(retracted[valid]))
        recall = float(np.mean(retracted[invalidated]))
        eligible = bool(frr <= max_frr + 1e-12)
        if eligible and recall > best_recall:
            best_threshold = float(threshold)
            best_recall = recall
        table.append(
            {
                "threshold": float(threshold),
                "false_retraction_rate": frr,
                "invalidation_recall": recall,
                "eligible": eligible,
            }
        )
    for row in table:
        row["selected"] = bool(float(row["threshold"]) == best_threshold)
    return best_threshold, table


def threshold_metrics(probs: np.ndarray, labels: np.ndarray, threshold: float) -> dict[str, float]:
    retracted = probs[:, 1] >= threshold
    valid = labels != 1
    invalidated = labels == 1
    recall = float(np.mean(retracted[invalidated]))
    return {
        "invalidation_recall_at_frr5": recall,
        "invalidation_miss_rate_at_frr5": 1.0 - recall,
        "achieved_false_retraction_rate": float(np.mean(retracted[valid])),
    }


def records_to_arrays(
    records: list[dict[str, object]],
    expected_indices: np.ndarray,
    dataset_labels: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    observed_indices = np.asarray([int(record["sample_index"]) for record in records], dtype=np.int64)
    if (
        len(observed_indices) != len(expected_indices)
        or len(np.unique(observed_indices)) != len(observed_indices)
        or set(observed_indices.tolist()) != set(expected_indices.tolist())
    ):
        raise RuntimeError("prediction trace does not cover the exact expected task-family samples")
    order = np.argsort(observed_indices)
    observed_indices = observed_indices[order]
    labels = np.asarray([int(records[idx]["label"]) for idx in order], dtype=np.int64)
    # Predictions originate from torch float32 tensors. Restore that exact
    # dtype so threshold-edge comparisons replay the training implementation
    # rather than silently changing np.nextafter/scalar coercion semantics.
    probabilities = np.asarray([records[idx]["probabilities"] for idx in order], dtype=np.float32)
    if (
        probabilities.shape != (len(expected_indices), 3)
        or not np.isfinite(probabilities).all()
        or np.any(probabilities < 0.0)
        or np.any(probabilities > 1.0)
        or not np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-6, rtol=0.0)
        or not np.array_equal(labels, dataset_labels[observed_indices])
    ):
        raise RuntimeError("invalid probabilities or labels in prediction trace")
    return probabilities, labels


def cluster_bootstrap_ci95(values: np.ndarray) -> list[float]:
    if len(values) == 1:
        return [float(values[0]), float(values[0])]
    rng = np.random.default_rng(20260830)
    sampled = values[rng.integers(0, len(values), size=(10_000, len(values)))]
    means = sampled.mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def fold_cluster_summary(rows: list[dict[str, object]], modality: str) -> dict[str, object]:
    folds = sorted({int(row["fold"]) for row in rows})
    output: dict[str, object] = {"folds": folds, "runs": len(rows), "fold_values": {}}
    for metric in METRICS:
        fold_values = [
            float(np.mean([float(row[metric]) for row in rows if int(row["fold"]) == fold])) for fold in folds
        ]
        array = np.asarray(fold_values, dtype=np.float64)
        mean = float(np.mean(array))
        output[f"{metric}_mean"] = mean
        output[f"{metric}_cluster_bootstrap_ci95"] = cluster_bootstrap_ci95(array)
        output["fold_values"][metric] = fold_values
    output["parameters"] = int(rows[0]["parameters"])
    return output


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.dataset)
    dataset_hash = sha256_file(dataset_path)
    manifest_path = Path(args.manifest)
    audit_path = Path(args.audit)
    probe_path = Path(args.probe)
    manifest_hash = sha256_file(manifest_path)
    audit_hash = sha256_file(audit_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    probe = json.loads(probe_path.read_text(encoding="utf-8"))
    sibling_trainer_hash = sha256_file(Path(__file__).with_name("train_representation_pilot.py"))
    sibling_geometry_hash = sha256_file(Path(__file__).with_name("geometry.py"))
    sibling_probe_hash = sha256_file(Path(__file__).with_name("probe_e0_invariant.py"))
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
    if (
        not bool(probe.get("complete", False))
        or probe.get("dataset_sha256") != dataset_hash
        or probe.get("manifest_sha256") != manifest_hash
        or probe.get("audit_sha256") != audit_hash
    ):
        raise RuntimeError("G0 requires a complete deterministic probe bound to the exact evidence")
    if (
        probe.get("probe_sha256") != sibling_probe_hash
        or probe.get("geometry_sha256") != sibling_geometry_hash
        or not np.isclose(float(probe.get("invalidation_threshold_m", np.nan)), 0.09, atol=0.0, rtol=0.0)
        or not np.isclose(float(probe.get("geometry_scale_m", np.nan)), 0.30, atol=0.0, rtol=0.0)
        or probe.get("pointmap_feature_shape") != [360, 38]
        or len(probe.get("predictions", [])) != 360
    ):
        raise RuntimeError("probe is not bound to the reviewed code or frozen 0.09m/0.30m constants")
    loaded = np.load(dataset_path, allow_pickle=False)
    dataset_labels = loaded["decision_label"].astype(np.int64)
    task_family_index = loaded["task_family_index"].astype(np.int64)
    if len(dataset_labels) != 360:
        raise RuntimeError(f"registered G0 requires 360 labels, got {len(dataset_labels)}")
    probe_records = sorted(probe["predictions"], key=lambda record: int(record["sample_index"]))
    probe_indices = np.asarray([int(record["sample_index"]) for record in probe_records], dtype=np.int64)
    probe_labels = np.asarray([int(record["label"]) for record in probe_records], dtype=np.int64)
    if (
        not np.array_equal(probe_indices, np.arange(360))
        or not np.array_equal(probe_labels, dataset_labels)
    ):
        raise RuntimeError("deterministic probe predictions are not aligned to dataset labels")
    for name, field in (("oracle", "oracle_prediction"), ("pointmap", "pointmap_prediction")):
        predictions = np.asarray([int(record[field]) for record in probe_records], dtype=np.int64)
        if not np.all(np.isin(predictions, [0, 1, 2])):
            raise RuntimeError(f"deterministic {name} predictions contain an invalid class")
        invalidated = dataset_labels == 1
        non_retract = dataset_labels != 1
        confusion = [
            [
                int(np.sum((dataset_labels == truth) & (predictions == predicted)))
                for predicted in range(3)
            ]
            for truth in range(3)
        ]
        recomputed = {
            "accuracy": float(np.mean(predictions == dataset_labels)),
            "macro_f1": macro_f1(dataset_labels, predictions),
            "invalidation_recall": float(np.mean(predictions[invalidated] == 1)),
            "invalidation_miss_rate": float(np.mean(predictions[invalidated] != 1)),
            "false_retraction_rate": float(np.mean(predictions[non_retract] == 1)),
            "errors": int(np.sum(predictions != dataset_labels)),
            "confusion_matrix": confusion,
        }
        recorded = probe[name]
        scalar_fields = (
            "accuracy",
            "macro_f1",
            "invalidation_recall",
            "invalidation_miss_rate",
            "false_retraction_rate",
        )
        scalar_match = all(
            np.isclose(
                float(recomputed[field]),
                float(recorded.get(field, np.nan)),
                atol=1e-12,
                rtol=0.0,
            )
            for field in scalar_fields
        )
        exact_match = (
            int(recorded.get("errors", -1)) == recomputed["errors"]
            and recorded.get("confusion_matrix") == recomputed["confusion_matrix"]
        )
        if not (scalar_match and exact_match):
            raise RuntimeError(f"deterministic {name} metrics do not match its prediction vector")
        if name == "oracle":
            recomputed_gate = {
                "accuracy_ge_0_99": bool(recomputed["accuracy"] >= 0.99),
                "macro_f1_ge_0_98": bool(recomputed["macro_f1"] >= 0.98),
            }
            recomputed_gate["pass"] = bool(
                recomputed_gate["accuracy_ge_0_99"] and recomputed_gate["macro_f1_ge_0_98"]
            )
            if probe.get("oracle_gate") != recomputed_gate or not recomputed_gate["pass"]:
                raise RuntimeError("G0 requires a recomputed passing deterministic invariant Oracle gate")
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
        expected_config = {
            "epochs": 60,
            "patience": 10,
            "min_epochs": 20,
            "batch_size": 32,
            "learning_rate": 3e-4,
            "weight_decay": 1e-4,
            "seeds": [17, 29, 43],
            "probability_calibration": "none",
            "threshold_fit_scope": "validation_task_family_only",
            "numeric_feature_scaling": "fixed_0.30m_no_family_fitted_normalization",
            "cluster_interval": {
                "method": "percentile_bootstrap",
                "resamples": 10000,
                "seed": 20260830,
            },
        }
        if any(payload_config.get(key) != value for key, value in expected_config.items()):
            raise RuntimeError(f"registered repair config mismatch in {path}: {payload_config}")
        config_hashes.add(str(payload.get("common_config_sha256")))
        payload_rows = list(payload.get("runs", []))
        payload_modalities = {str(row["modality"]) for row in payload_rows}
        feature_dimensions = payload.get("feature_dimensions", {})
        if (
            ("pointmap" in payload_modalities and feature_dimensions.get("pointmap") != 38)
            or ("oracle_pose" in payload_modalities and feature_dimensions.get("oracle_pose") != 24)
        ):
            raise RuntimeError(f"missing or wrong invariant feature dimensions in {path}: {feature_dimensions}")
        test_records = list(payload.get("predictions", []))
        validation_records = list(payload.get("validation_predictions", []))
        expected_test_records = sum(int(row["test_samples"]) for row in payload_rows)
        expected_validation_records = sum(int(row["val_samples"]) for row in payload_rows)
        if len(test_records) != expected_test_records or len(validation_records) != expected_validation_records:
            raise RuntimeError(
                f"wrong test/validation trace sizes in {path}: "
                f"{len(test_records)}/{len(validation_records)} expected "
                f"{expected_test_records}/{expected_validation_records}"
            )
        test_trace_keys = [
            (str(record["modality"]), int(record["fold"]), int(record["seed"]), int(record["sample_index"]))
            for record in test_records
        ]
        validation_trace_keys = [
            (str(record["modality"]), int(record["fold"]), int(record["seed"]), int(record["sample_index"]))
            for record in validation_records
        ]
        if len(set(test_trace_keys)) != len(test_trace_keys) or len(set(validation_trace_keys)) != len(validation_trace_keys):
            raise RuntimeError(f"duplicate prediction trace keys in {path}")

        for row in payload_rows:
            modality, fold, seed = str(row["modality"]), int(row["fold"]), int(row["seed"])
            test_family = int(row["test_task_family"])
            validation_family = int(row["val_task_family"])
            run_test = [
                record
                for record in test_records
                if str(record["modality"]) == modality
                and int(record["fold"]) == fold
                and int(record["seed"]) == seed
            ]
            run_validation = [
                record
                for record in validation_records
                if str(record["modality"]) == modality
                and int(record["fold"]) == fold
                and int(record["seed"]) == seed
            ]
            if any(int(record["test_task_family"]) != test_family for record in run_test) or any(
                int(record["validation_task_family"]) != validation_family for record in run_validation
            ):
                raise RuntimeError(f"prediction task-family metadata mismatch for {modality}/{fold}/{seed}")
            expected_test_indices = np.flatnonzero(task_family_index == test_family)
            expected_validation_indices = np.flatnonzero(task_family_index == validation_family)
            test_probs, test_labels = records_to_arrays(run_test, expected_test_indices, dataset_labels)
            validation_probs, validation_labels = records_to_arrays(
                run_validation, expected_validation_indices, dataset_labels
            )
            selected_threshold, candidate_table = select_threshold(validation_probs, validation_labels)
            if not np.isclose(
                selected_threshold,
                float(row["retract_threshold_from_validation"]),
                atol=1e-12,
                rtol=0.0,
            ):
                raise RuntimeError(f"selected validation threshold mismatch for {modality}/{fold}/{seed}")
            stored_candidates = list(row.get("validation_threshold_candidates", []))
            if len(stored_candidates) != len(candidate_table):
                raise RuntimeError(f"threshold candidate count mismatch for {modality}/{fold}/{seed}")
            for stored, recomputed in zip(stored_candidates, candidate_table):
                if (
                    not np.isclose(float(stored["threshold"]), float(recomputed["threshold"]), atol=1e-12, rtol=0.0)
                    or not np.isclose(
                        float(stored["false_retraction_rate"]),
                        float(recomputed["false_retraction_rate"]),
                        atol=1e-12,
                        rtol=0.0,
                    )
                    or not np.isclose(
                        float(stored["invalidation_recall"]),
                        float(recomputed["invalidation_recall"]),
                        atol=1e-12,
                        rtol=0.0,
                    )
                    or bool(stored["eligible"]) != bool(recomputed["eligible"])
                    or bool(stored["selected"]) != bool(recomputed["selected"])
                ):
                    raise RuntimeError(f"threshold candidate trace mismatch for {modality}/{fold}/{seed}")
            recomputed_metrics = {
                **classification_metrics(test_probs, test_labels),
                **threshold_metrics(test_probs, test_labels, selected_threshold),
            }
            validation_budget = threshold_metrics(validation_probs, validation_labels, selected_threshold)
            recomputed_metrics["validation_invalidation_recall_at_frr5"] = validation_budget[
                "invalidation_recall_at_frr5"
            ]
            recomputed_metrics["validation_achieved_false_retraction_rate"] = validation_budget[
                "achieved_false_retraction_rate"
            ]
            for metric, value in recomputed_metrics.items():
                if not np.isclose(float(row[metric]), float(value), atol=1e-7, rtol=0.0):
                    raise RuntimeError(
                        f"stored metric mismatch {metric} for {modality}/{fold}/{seed}: "
                        f"{row[metric]} vs {value}"
                    )
        source_hashes[str(path)] = sha256_file(path)
        rows.extend(payload_rows)
    if (
        trainer_hashes != {sibling_trainer_hash}
        or geometry_hashes != {sibling_geometry_hash}
        or len(config_hashes) != 1
    ):
        raise RuntimeError(
            f"unreviewed or mixed trainer/geometry/config hashes: "
            f"trainer={trainer_hashes}/{sibling_trainer_hash}, "
            f"geometry={geometry_hashes}/{sibling_geometry_hash}, config={config_hashes}"
        )
    if probe.get("geometry_sha256") != next(iter(geometry_hashes)):
        raise RuntimeError("deterministic probe and learned results use different geometry code")
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
        history = row.get("training_history", [])
        candidates = row.get("validation_threshold_candidates", [])
        if (
            len(history) != int(row["epochs"])
            or int(row.get("best_epoch", 0)) < 1
            or sum(bool(candidate.get("selected", False)) for candidate in candidates) != 1
        ):
            raise RuntimeError(f"incomplete epoch/threshold trace in row {row['modality']}/{row['fold']}/{row['seed']}")
    summaries = {
        modality: fold_cluster_summary([row for row in rows if row["modality"] == modality], modality)
        for modality in modalities
    }

    paired_deltas: dict[str, object] = {}
    for metric in ("macro_f1", "invalidation_miss_rate_at_frr5"):
        point_values = np.asarray(summaries["pointmap"]["fold_values"][metric], dtype=np.float64)
        depth_values = np.asarray(summaries["depth_addressed"]["fold_values"][metric], dtype=np.float64)
        delta = point_values - depth_values
        paired_deltas[f"pointmap_minus_depth_{metric}"] = {
            "fold_values": delta.tolist(),
            "mean": float(delta.mean()),
            "cluster_bootstrap_ci95": cluster_bootstrap_ci95(delta),
        }

    _, time_dim, camera_dim, height, width = loaded["depth"].shape
    verifier_tensor_bytes = {
        "rgb_addressed": int(time_dim * camera_dim * 5 * height * width * 4),
        "depth_addressed": int(time_dim * camera_dim * 3 * height * width * 4),
        "pointmap": int(38 * 4),
        "oracle_pose": int(24 * 4),
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
        "deterministic_probe": str(probe_path),
        "deterministic_probe_sha256": sha256_file(probe_path),
        "complete": True,
        "task_cluster_unit": True,
        "task_family_ids": task_family_ids,
        "summaries": summaries,
        "paired_deltas": paired_deltas,
        "verifier_tensor_bytes_float32": verifier_tensor_bytes,
        "efficiency_scope": "Head input tensor and head forward only; excludes RGB-D sensing, instance association, and PointMap projection.",
        "gate": {"pass": gate_pass, "conditions": conditions, "interpretation": interpretation},
        "cluster_interval": {
            "unit": "task_family_fold",
            "method": "percentile_bootstrap",
            "resamples": 10000,
            "seed": 20260830,
        },
        "claim_limit": "Even a pass establishes only simulator-depth/instance-mask PointMap headroom, not action-conditioned WAM value.",
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(output, indent=2, sort_keys=True, allow_nan=False)
    output_path.write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
