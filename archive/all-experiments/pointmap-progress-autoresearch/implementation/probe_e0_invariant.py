"""Deterministic invariant Oracle and PointMap probes for E0 repair."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from geometry import (
    GEOMETRY_SCALE_M,
    INVALIDATION_THRESHOLD_M,
    invariant_oracle_decision,
    invariant_pointmap_decision,
    relation_pointmap_features,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
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


def macro_f1(labels: np.ndarray, predictions: np.ndarray) -> float:
    values = []
    for cls in range(3):
        tp = np.sum((labels == cls) & (predictions == cls))
        fp = np.sum((labels != cls) & (predictions == cls))
        fn = np.sum((labels == cls) & (predictions != cls))
        denom = 2 * tp + fp + fn
        values.append(0.0 if denom == 0 else float(2 * tp / denom))
    return float(np.mean(values))


def evaluate(labels: np.ndarray, predictions: np.ndarray) -> dict[str, object]:
    confusion = [
        [int(np.sum((labels == truth) & (predictions == predicted))) for predicted in range(3)]
        for truth in range(3)
    ]
    non_retract = labels != 1
    invalidated = labels == 1
    return {
        "accuracy": float(np.mean(predictions == labels)),
        "macro_f1": macro_f1(labels, predictions),
        "invalidation_recall": float(np.mean(predictions[invalidated] == 1)),
        "invalidation_miss_rate": float(np.mean(predictions[invalidated] != 1)),
        "false_retraction_rate": float(np.mean(predictions[non_retract] == 1)),
        "confusion_matrix": confusion,
        "errors": int(np.sum(predictions != labels)),
    }


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.dataset)
    manifest_path = Path(args.manifest)
    audit_path = Path(args.audit)
    output_path = Path(args.output)
    dataset_hash = sha256_file(dataset_path)
    manifest_hash = sha256_file(manifest_path)
    audit_hash = sha256_file(audit_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if (
        not bool(audit.get("pass", False))
        or audit.get("dataset_sha256") != dataset_hash
        or audit.get("manifest_sha256") != manifest_hash
        or manifest.get("output_sha256") != dataset_hash
    ):
        raise RuntimeError("probe requires exact matching dataset/manifest/passing audit")
    loaded = np.load(dataset_path, allow_pickle=False)
    data = {key: loaded[key] for key in loaded.files}
    labels = data["decision_label"].astype(np.int64)
    if len(labels) != 360:
        raise RuntimeError(f"registered E0 probe requires 360 samples, got {len(labels)}")

    oracle_predictions = np.asarray(
        [
            invariant_oracle_decision(
                data["target_pose"][idx],
                data["reference_pose"][idx],
                data["target_visibility"][idx],
            )
            for idx in range(len(labels))
        ],
        dtype=np.int64,
    )
    pointmap_features = np.stack(
        [
            relation_pointmap_features(
                data["depth"][idx],
                data["seg"][idx],
                data["pixel_to_world"][idx],
                int(data["target_id"][idx]),
                int(data["reference_id"][idx]),
            )
            for idx in range(len(labels))
        ]
    ).astype(np.float32)
    if pointmap_features.shape != (360, 38) or not np.isfinite(pointmap_features).all():
        raise RuntimeError(f"invalid invariant PointMap matrix {pointmap_features.shape}")
    pointmap_predictions = np.asarray(
        [invariant_pointmap_decision(row) for row in pointmap_features],
        dtype=np.int64,
    )
    predictions = [
        {
            "sample_index": int(idx),
            "label": int(labels[idx]),
            "oracle_prediction": int(oracle_predictions[idx]),
            "pointmap_prediction": int(pointmap_predictions[idx]),
        }
        for idx in range(len(labels))
    ]

    failures = []
    for idx in np.flatnonzero((oracle_predictions != labels) | (pointmap_predictions != labels)):
        relative = data["target_pose"][idx, :, :3] - data["reference_pose"][idx, :, :3]
        failures.append(
            {
                "sample_index": int(idx),
                "task_family_index": int(data["task_family_index"][idx]),
                "event_id": int(data["event_id"][idx]),
                "label": int(labels[idx]),
                "oracle_prediction": int(oracle_predictions[idx]),
                "pointmap_prediction": int(pointmap_predictions[idx]),
                "oracle_relative_change_m": float(np.linalg.norm(relative[1] - relative[0])),
                "target_visibility": data["target_visibility"][idx].astype(int).tolist(),
            }
        )

    oracle_metrics = evaluate(labels, oracle_predictions)
    pointmap_metrics = evaluate(labels, pointmap_predictions)
    oracle_gate = bool(oracle_metrics["accuracy"] >= 0.99 and oracle_metrics["macro_f1"] >= 0.98)
    output = {
        "schema_version": 1,
        "kind": "e0_invariant_deterministic_probe",
        "claim_limit": "Pipeline and information-sufficiency diagnostic only; not a learned model or action-conditioned result.",
        "complete": True,
        "dataset": str(dataset_path),
        "dataset_sha256": dataset_hash,
        "manifest_sha256": manifest_hash,
        "audit_sha256": audit_hash,
        "probe_sha256": sha256_file(Path(__file__)),
        "geometry_sha256": sha256_file(Path(__file__).with_name("geometry.py")),
        "threshold_source": "fixed before implementation at half the generator minimum invalidation translation, 0.18m / 2",
        "invalidation_threshold_m": INVALIDATION_THRESHOLD_M,
        "geometry_scale_m": GEOMETRY_SCALE_M,
        "pointmap_feature_shape": list(pointmap_features.shape),
        "oracle": oracle_metrics,
        "pointmap": pointmap_metrics,
        "oracle_gate": {
            "accuracy_ge_0_99": bool(oracle_metrics["accuracy"] >= 0.99),
            "macro_f1_ge_0_98": bool(oracle_metrics["macro_f1"] >= 0.98),
            "pass": oracle_gate,
        },
        "predictions": predictions,
        "failures": failures,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(output, indent=2, sort_keys=True, allow_nan=False)
    output_path.write_text(serialized, encoding="utf-8")
    print(serialized)
    if not oracle_gate:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
