"""Compare RGB, full depth, PointMap, and oracle geometry on relation decisions."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import time
from pathlib import Path

import numpy as np

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

from geometry import oracle_relative_features, relation_pointmap_features


MODALITIES = ("rgb_addressed", "depth_addressed", "pointmap", "oracle_pose")
CLASS_NAMES = ("continue", "retract", "reobserve")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--audit", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--modalities", nargs="*", default=list(MODALITIES))
    parser.add_argument("--seeds", nargs="*", type=int, default=[17, 29, 43])
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--patience", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--device", default="cuda")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


def macro_f1(y_true: np.ndarray, y_pred: np.ndarray, classes: int = 3) -> float:
    values = []
    for cls in range(classes):
        tp = np.sum((y_true == cls) & (y_pred == cls))
        fp = np.sum((y_true != cls) & (y_pred == cls))
        fn = np.sum((y_true == cls) & (y_pred != cls))
        denom = 2 * tp + fp + fn
        values.append(0.0 if denom == 0 else (2.0 * tp) / denom)
    return float(np.mean(values))


def expected_calibration_error(probs: np.ndarray, labels: np.ndarray, bins: int = 10) -> float:
    confidence = probs.max(axis=1)
    predictions = probs.argmax(axis=1)
    total = len(labels)
    ece = 0.0
    for lower in np.linspace(0.0, 1.0, bins, endpoint=False):
        upper = lower + 1.0 / bins
        mask = (confidence >= lower) & (confidence < upper if upper < 1.0 else confidence <= upper)
        if np.any(mask):
            ece += (np.sum(mask) / total) * abs(np.mean(predictions[mask] == labels[mask]) - np.mean(confidence[mask]))
    return float(ece)


def metrics(probs: np.ndarray, labels: np.ndarray) -> dict[str, float]:
    predictions = probs.argmax(axis=1)
    retract = 1
    non_retract = labels != retract
    invalid = labels == retract
    reobserve = labels == 2
    if not np.any(invalid) or not np.any(non_retract) or not np.any(reobserve):
        raise RuntimeError("every evaluation split must contain retract, non-retract, and reobserve decisions")
    one_hot = np.eye(3, dtype=np.float32)[labels]
    return {
        "accuracy": float(np.mean(predictions == labels)),
        "macro_f1": macro_f1(labels, predictions),
        "invalidation_recall": float(np.mean(predictions[invalid] == retract)),
        "false_retraction_rate": float(np.mean(predictions[non_retract] == retract)),
        "unobservable_reobserve_recall": float(np.mean(predictions[reobserve] == 2)),
        "decision_error": float(np.mean(predictions != labels)),
        "brier": float(np.mean(np.sum((probs - one_hot) ** 2, axis=1))),
        "ece": expected_calibration_error(probs, labels),
    }


def retract_threshold_at_budget(probs: np.ndarray, labels: np.ndarray, max_frr: float = 0.05) -> float:
    """Choose the highest-recall validation threshold subject to FRR <= budget."""

    score = probs[:, 1]
    no_retract = float(np.nextafter(float(np.max(score)), float("inf")))
    candidates = np.concatenate(([no_retract], np.unique(score)))
    best_threshold = no_retract
    best_recall = -1.0
    for threshold in candidates:
        retracted = score >= threshold
        valid = labels != 1
        invalid = labels == 1
        frr = float(np.mean(retracted[valid])) if np.any(valid) else 0.0
        recall = float(np.mean(retracted[invalid])) if np.any(invalid) else 0.0
        if frr <= max_frr + 1e-12 and recall > best_recall:
            best_threshold = float(threshold)
            best_recall = recall
    return best_threshold


def budget_metrics(probs: np.ndarray, labels: np.ndarray, threshold: float) -> dict[str, float]:
    retracted = probs[:, 1] >= threshold
    valid = labels != 1
    invalid = labels == 1
    if not np.any(valid) or not np.any(invalid):
        raise RuntimeError("FRR-budget metrics require valid and invalid events")
    frr = float(np.mean(retracted[valid]))
    recall = float(np.mean(retracted[invalid]))
    return {
        "retract_threshold_from_validation": threshold,
        "invalidation_recall_at_frr5": recall,
        "invalidation_miss_rate_at_frr5": 1.0 - recall,
        "achieved_false_retraction_rate": frr,
    }


def addressed_image(data: dict[str, np.ndarray], index: int, modality: str) -> np.ndarray:
    seg = data["seg"][index]
    target_mask = (seg == int(data["target_id"][index])).astype(np.float32)
    reference_mask = (seg == int(data["reference_id"][index])).astype(np.float32)
    channels: list[np.ndarray] = []
    for time_idx in range(seg.shape[0]):
        for camera_idx in range(seg.shape[1]):
            if modality == "rgb_addressed":
                base = data["rgb"][index, time_idx, camera_idx].astype(np.float32) / 255.0
                channel_last = np.concatenate(
                    (base, target_mask[time_idx, camera_idx, ..., None], reference_mask[time_idx, camera_idx, ..., None]),
                    axis=-1,
                )
            else:
                depth = data["depth"][index, time_idx, camera_idx].astype(np.float32)
                valid = np.isfinite(depth)
                # Metric inverse depth makes near-field manipulation differences numerically visible.
                inverse_depth = np.zeros_like(depth, dtype=np.float32)
                inverse_depth[valid] = np.clip(1.0 / np.clip(depth[valid], 0.2, 4.0), 0.0, 5.0) / 5.0
                channel_last = np.stack(
                    (inverse_depth, target_mask[time_idx, camera_idx], reference_mask[time_idx, camera_idx]), axis=-1
                )
            channels.append(channel_last.transpose(2, 0, 1))
    return np.concatenate(channels, axis=0).astype(np.float32)


def precompute_features(data: dict[str, np.ndarray], modality: str) -> np.ndarray | None:
    if modality in {"rgb_addressed", "depth_addressed"}:
        return None
    rows = []
    for idx in range(len(data["decision_label"])):
        if modality == "pointmap":
            row = relation_pointmap_features(
                data["depth"][idx],
                data["seg"][idx],
                data["pixel_to_world"][idx],
                int(data["target_id"][idx]),
                int(data["reference_id"][idx]),
            )
        elif modality == "oracle_pose":
            row = oracle_relative_features(
                data["target_pose"][idx],
                data["reference_pose"][idx],
                data["target_visibility"][idx],
                data["reference_visibility"][idx],
            )
        else:
            raise ValueError(modality)
        rows.append(row)
    return np.stack(rows).astype(np.float32)


class RelationDataset(Dataset):
    def __init__(
        self,
        data: dict[str, np.ndarray],
        indices: np.ndarray,
        modality: str,
        features: np.ndarray | None,
        mean: np.ndarray | None = None,
        std: np.ndarray | None = None,
    ) -> None:
        self.data = data
        self.indices = np.asarray(indices, dtype=np.int64)
        self.modality = modality
        self.features = features
        self.mean = mean
        self.std = std

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, item: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        index = int(self.indices[item])
        if self.features is None:
            value = addressed_image(self.data, index, self.modality)
        else:
            value = self.features[index]
            if self.mean is not None and self.std is not None:
                value = (value - self.mean) / self.std
        return torch.from_numpy(value), torch.tensor(int(self.data["decision_label"][index])), torch.tensor(index)


class ImageVerifier(nn.Module):
    def __init__(self, input_channels: int) -> None:
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(input_channels, 32, 5, stride=2, padding=2),
            nn.GroupNorm(4, 32),
            nn.GELU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1),
            nn.GroupNorm(8, 64),
            nn.GELU(),
            nn.Conv2d(64, 96, 3, stride=2, padding=1),
            nn.GroupNorm(8, 96),
            nn.GELU(),
        )
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(96 * 4, 128),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(128, 3),
        )

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        encoded = self.encoder(value)
        height, width = encoded.shape[-2:]
        if height % 2 or width % 2:
            raise RuntimeError(f"deterministic 2x2 pooling requires even feature shape, got {height}x{width}")
        # Exact 2x2 equal-bin average for the registered 96x96 input. Explicit
        # reductions avoid CUDA adaptive-pooling's nondeterministic backward.
        pooled = encoded.reshape(
            encoded.shape[0], encoded.shape[1], 2, height // 2, 2, width // 2
        ).mean(dim=(3, 5))
        return self.head(pooled)


class FeatureVerifier(nn.Module):
    def __init__(self, input_dim: int) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 192),
            nn.LayerNorm(192),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(192, 128),
            nn.GELU(),
            nn.Linear(128, 3),
        )

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        return self.network(value)


@torch.no_grad()
def predict(model: nn.Module, loader: DataLoader, device: torch.device) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    model.eval()
    probabilities, labels, indices = [], [], []
    for values, batch_labels, batch_indices in loader:
        logits = model(values.to(device, non_blocking=True))
        probabilities.append(torch.softmax(logits, dim=-1).cpu().numpy())
        labels.append(batch_labels.numpy())
        indices.append(batch_indices.numpy())
    return np.concatenate(probabilities), np.concatenate(labels), np.concatenate(indices)


def train_one(
    data: dict[str, np.ndarray],
    modality: str,
    features: np.ndarray | None,
    train_indices: np.ndarray,
    val_indices: np.ndarray,
    test_indices: np.ndarray,
    seed: int,
    args: argparse.Namespace,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    set_seed(seed)
    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    mean = std = None
    if features is not None:
        mean = features[train_indices].mean(axis=0)
        std = features[train_indices].std(axis=0)
        std[std < 1e-5] = 1.0
    train_ds = RelationDataset(data, train_indices, modality, features, mean, std)
    val_ds = RelationDataset(data, val_indices, modality, features, mean, std)
    test_ds = RelationDataset(data, test_indices, modality, features, mean, std)
    generator = torch.Generator().manual_seed(seed)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, generator=generator, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False, num_workers=0)
    sample, _, _ = train_ds[0]
    model: nn.Module
    if sample.ndim == 3:
        model = ImageVerifier(sample.shape[0])
    else:
        model = FeatureVerifier(sample.numel())
    model.to(device)
    # Preserve the empirical decision prevalence so probabilities and the
    # validation-only FRR operating point retain their intended semantics.
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)
    best_score = -math.inf
    best_state: dict[str, torch.Tensor] | None = None
    stale = 0
    started = time.time()
    epochs_run = 0
    for epoch in range(args.epochs):
        model.train()
        for values, labels, _ in train_loader:
            optimizer.zero_grad(set_to_none=True)
            logits = model(values.to(device, non_blocking=True))
            loss = loss_fn(logits, labels.to(device, non_blocking=True))
            loss.backward()
            optimizer.step()
        val_probs, val_labels, _ = predict(model, val_loader, device)
        score = macro_f1(val_labels, val_probs.argmax(axis=1))
        epochs_run = epoch + 1
        if score > best_score + 1e-6:
            best_score = score
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            stale = 0
        else:
            stale += 1
        if stale >= args.patience:
            break
    if best_state is None:
        raise RuntimeError("training failed to produce a checkpoint")
    model.load_state_dict(best_state)
    val_probs, val_labels, _ = predict(model, val_loader, device)
    retract_threshold = retract_threshold_at_budget(val_probs, val_labels, max_frr=0.05)
    test_probs, test_labels, sample_indices = predict(model, test_loader, device)
    if device.type == "cuda":
        torch.cuda.synchronize()
    timing_value = sample.unsqueeze(0).to(device)
    with torch.inference_mode():
        for _ in range(10):
            model(timing_value)
        if device.type == "cuda":
            torch.cuda.synchronize()
        latency_start = time.perf_counter()
        for _ in range(100):
            model(timing_value)
        if device.type == "cuda":
            torch.cuda.synchronize()
    latency_ms = (time.perf_counter() - latency_start) * 10.0
    validation_budget = budget_metrics(val_probs, val_labels, retract_threshold)
    result: dict[str, object] = {
        "modality": modality,
        "seed": seed,
        "epochs": epochs_run,
        "best_val_macro_f1": best_score,
        "parameters": int(sum(parameter.numel() for parameter in model.parameters())),
        "head_forward_latency_ms_per_sample": latency_ms,
        "train_seconds": time.time() - started,
        "train_samples": len(train_indices),
        "val_samples": len(val_indices),
        "test_samples": len(test_indices),
        **metrics(test_probs, test_labels),
        **budget_metrics(test_probs, test_labels, retract_threshold),
        "validation_invalidation_recall_at_frr5": validation_budget["invalidation_recall_at_frr5"],
        "validation_achieved_false_retraction_rate": validation_budget["achieved_false_retraction_rate"],
    }
    predictions = [
        {
            "sample_index": int(index),
            "label": int(label),
            "probabilities": [float(value) for value in probability],
        }
        for index, label, probability in zip(sample_indices, test_labels, test_probs)
    ]
    return result, predictions


def summarize(results: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    metric_names = (
        "accuracy",
        "macro_f1",
        "invalidation_recall",
        "false_retraction_rate",
        "unobservable_reobserve_recall",
        "decision_error",
        "brier",
        "ece",
        "head_forward_latency_ms_per_sample",
        "parameters",
        "invalidation_recall_at_frr5",
        "invalidation_miss_rate_at_frr5",
        "achieved_false_retraction_rate",
    )
    summary: dict[str, dict[str, float]] = {}
    for modality in sorted({str(row["modality"]) for row in results}):
        rows = [row for row in results if row["modality"] == modality]
        folds = sorted({int(row["fold"]) for row in rows})
        values: dict[str, object] = {"runs": len(rows), "task_family_clusters": len(folds), "fold_values": {}}
        for metric in metric_names:
            fold_values = [
                float(np.mean([float(row[metric]) for row in rows if int(row["fold"]) == fold])) for fold in folds
            ]
            array = np.asarray(fold_values, dtype=np.float64)
            mean = float(np.mean(array))
            std = float(np.std(array, ddof=1)) if len(array) > 1 else 0.0
            critical = 2.776 if len(array) == 5 else 1.96
            values[f"{metric}_mean"] = mean
            values[f"{metric}_task_cluster_ci95"] = float(critical * std / math.sqrt(len(array))) if len(array) > 1 else 0.0
            values["fold_values"][metric] = fold_values
        summary[modality] = values
    return summary


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.dataset)
    manifest_path = Path(args.manifest)
    audit_path = Path(args.audit)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset_hash = sha256_file(dataset_path)
    manifest_hash = sha256_file(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if not bool(audit.get("pass", False)) or audit.get("dataset_sha256") != dataset_hash:
        raise RuntimeError("training requires a passing audit bound to the exact dataset")
    if audit.get("manifest_sha256") != manifest_hash or manifest.get("output_sha256") != dataset_hash:
        raise RuntimeError("audit/manifest/dataset provenance mismatch")
    loaded = np.load(dataset_path, allow_pickle=False)
    data = {key: loaded[key] for key in loaded.files}
    task_family_indices = sorted(int(value) for value in np.unique(data["task_family_index"]))
    task_family_ids = list(manifest.get("task_family_ids", []))
    if (
        task_family_indices != [0, 1, 2, 3, 4]
        or len(task_family_ids) != 5
        or len(set(task_family_ids)) != 5
        or len(data["decision_label"]) != 360
    ):
        raise RuntimeError(
            f"registered E0 requires five explicit task families and 360 samples, "
            f"got {task_family_indices}/{task_family_ids}/{len(data['decision_label'])}"
        )
    if sorted(args.seeds) != [17, 29, 43] or len(set(args.seeds)) != 3:
        raise RuntimeError(f"registered E0 requires model seeds 17,29,43, got {args.seeds}")
    if not set(args.modalities).issubset(set(MODALITIES)) or len(set(args.modalities)) != len(args.modalities):
        raise RuntimeError(f"invalid or duplicate modalities: {args.modalities}")
    common_config = {
        "epochs": args.epochs,
        "patience": args.patience,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "seeds": args.seeds,
        "task_family_indices": task_family_indices,
        "task_family_ids": task_family_ids,
        "probability_calibration": "none",
        "threshold_fit_scope": "validation_task_family_only",
        "calibration_population": "controlled_synthetic_event_generator",
    }
    config_signature = hashlib.sha256(json.dumps(common_config, sort_keys=True).encode("utf-8")).hexdigest()
    all_results: list[dict[str, object]] = []
    all_predictions: list[dict[str, object]] = []
    feature_cache = {modality: precompute_features(data, modality) for modality in args.modalities}
    for fold_index, test_family in enumerate(task_family_indices):
        val_family = task_family_indices[(fold_index + 1) % len(task_family_indices)]
        train_families = [family for family in task_family_indices if family not in {test_family, val_family}]
        train_indices = np.flatnonzero(np.isin(data["task_family_index"], train_families))
        val_indices = np.flatnonzero(data["task_family_index"] == val_family)
        test_indices = np.flatnonzero(data["task_family_index"] == test_family)
        for modality in args.modalities:
            for seed in args.seeds:
                result, predictions = train_one(
                    data,
                    modality,
                    feature_cache[modality],
                    train_indices,
                    val_indices,
                    test_indices,
                    seed,
                    args,
                )
                result.update(
                    {
                        "fold": fold_index,
                        "test_task_family": test_family,
                        "val_task_family": val_family,
                        "train_task_families": train_families,
                    }
                )
                all_results.append(result)
                for prediction in predictions:
                    prediction.update(
                        {"modality": modality, "seed": seed, "fold": fold_index, "test_task_family": test_family}
                    )
                    all_predictions.append(prediction)
                print(json.dumps(result, sort_keys=True, allow_nan=False), flush=True)
    payload = {
        "schema_version": 1,
        "kind": "controlled_relation_event_representation_pilot",
        "claim_limit": "No action-conditioned or closed-loop claim; controlled interventions test representation headroom only.",
        "command": " ".join(os.sys.argv),
        "dataset": str(dataset_path),
        "dataset_sha256": dataset_hash,
        "manifest": str(manifest_path),
        "manifest_sha256": manifest_hash,
        "audit": str(audit_path),
        "audit_sha256": sha256_file(audit_path),
        "trainer_sha256": sha256_file(Path(__file__)),
        "geometry_sha256": sha256_file(Path(__file__).with_name("geometry.py")),
        "complete": True,
        "common_config": common_config,
        "common_config_sha256": config_signature,
        "runtime": {
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
            "deterministic_algorithms": True,
            "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
        },
        "class_names": CLASS_NAMES,
        "modalities": list(args.modalities),
        "seeds": args.seeds,
        "folds": len(task_family_indices),
        "runs": all_results,
        "summary": summarize(all_results),
        "predictions": all_predictions,
    }
    serialized = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False)
    output_path.write_text(serialized, encoding="utf-8")
    print(
        json.dumps(
            {"output": str(output_path), "runs": len(all_results), "summary": payload["summary"]},
            indent=2,
            allow_nan=False,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
