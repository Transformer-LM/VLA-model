"""Train a small action-conditioned state WAM and test residual transport harm.

This is a P027-C pilot, not a closed-loop VLA result.  It uses a leave-source-
out split and evaluates already frozen P026 physical evidence.  The oracle
influence mask is an upper-bound diagnostic; no learned router is claimed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import itertools
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


VERIFIED_EVIDENCE: dict[Path, str] = {}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def personal_path(raw: str, *, must_exist: bool = True) -> Path:
    path = Path(raw).resolve(strict=must_exist)
    text = str(path)
    if not text.startswith(("<PERSONAL_RESEARCH_ROOT>/", "<PERSONAL_RESEARCH_ROOT_ALIAS>/")):
        raise ValueError(f"path is outside liu_meng personal storage: {path}")
    return path


def verify_evidence(path: Path, expected_sha256: str) -> None:
    prior = VERIFIED_EVIDENCE.get(path)
    if prior is not None:
        if prior != expected_sha256:
            raise ValueError(f"conflicting expected hashes for {path}")
        return
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise ValueError(f"evidence hash mismatch: {path}: {actual} != {expected_sha256}")
    VERIFIED_EVIDENCE[path] = actual


def commit_json_no_clobber(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    try:
        with temporary.open("xb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


def commit_checkpoint_no_clobber(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    try:
        with temporary.open("xb") as handle:
            torch.save(payload, handle)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


def array_sha256(*arrays: np.ndarray) -> str:
    digest = hashlib.sha256()
    for array in arrays:
        contiguous = np.ascontiguousarray(array)
        digest.update(str(contiguous.dtype).encode("ascii"))
        digest.update(np.asarray(contiguous.shape, dtype=np.int64).tobytes())
        digest.update(contiguous.tobytes())
    return digest.hexdigest()


def canonical_sha256(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class Trace:
    states: np.ndarray
    actions: np.ndarray
    active: np.ndarray


def load_trace(path: Path, prefix: str) -> Trace:
    with np.load(path, allow_pickle=False) as evidence:
        states = np.asarray(evidence[f"{prefix}_state"], dtype=np.float32)
        actions = np.asarray(evidence[f"{prefix}_actions"], dtype=np.float32)
        active = np.asarray(evidence[f"{prefix}_active"], dtype=bool)
    if states.ndim != 2 or actions.ndim != 2:
        raise ValueError(f"invalid trace rank in {path}")
    if len(states) != len(actions) + 1 or len(active) != len(states):
        raise ValueError(f"state/action/active length mismatch in {path}")
    if not np.isfinite(states).all() or not np.isfinite(actions).all():
        raise ValueError(f"non-finite trace in {path}")
    return Trace(states=states, actions=actions, active=active)


class DeltaWAM(nn.Module):
    def __init__(self, input_dim: int, output_dim: int, width: int, depth: int) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        current = input_dim
        for _ in range(depth):
            layers.extend((nn.Linear(current, width), nn.SiLU()))
            current = width
        layers.append(nn.Linear(current, output_dim))
        self.network = nn.Sequential(*layers)

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        return self.network(value)


def unique_transitions(
    records: Iterable[dict[str, Any]], excluded_source: str
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    rows: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    sources: set[str] = set()
    traces_seen = 0
    for record in records:
        if record["rollout_sha256"] == excluded_source:
            continue
        sources.add(str(record["rollout_sha256"]))
        for endpoint in record["endpoint_evidence"].values():
            path = personal_path(endpoint["path"])
            verify_evidence(path, str(endpoint["sha256"]))
            for prefix in ("factual", "candidate"):
                trace = load_trace(path, prefix)
                traces_seen += 1
                for index, action in enumerate(trace.actions):
                    state = trace.states[index]
                    next_state = trace.states[index + 1]
                    feature = np.concatenate((state, action), axis=0).astype(np.float32)
                    target = (next_state - state).astype(np.float32)
                    key = array_sha256(feature, target)
                    rows.setdefault(key, (feature, target))
    if not rows:
        raise ValueError("no training transitions after leave-source-out filtering")
    features = np.stack([value[0] for value in rows.values()], axis=0)
    targets = np.stack([value[1] for value in rows.values()], axis=0)
    return features, targets, {
        "train_source_count": len(sources),
        "raw_trace_count": traces_seen,
        "unique_transition_count": len(rows),
    }


def transition_arrays(records: Iterable[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
    rows: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for record in records:
        for endpoint in record["endpoint_evidence"].values():
            path = personal_path(endpoint["path"])
            verify_evidence(path, str(endpoint["sha256"]))
            for prefix in ("factual", "candidate"):
                trace = load_trace(path, prefix)
                for index, action in enumerate(trace.actions):
                    state = trace.states[index]
                    feature = np.concatenate((state, action), axis=0).astype(np.float32)
                    target = (trace.states[index + 1] - state).astype(np.float32)
                    rows.setdefault(array_sha256(feature, target), (feature, target))
    if not rows:
        raise ValueError("no evaluation transitions")
    return (
        np.stack([value[0] for value in rows.values()], axis=0),
        np.stack([value[1] for value in rows.values()], axis=0),
    )


def mean_std(array: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = array.mean(axis=0, dtype=np.float64).astype(np.float32)
    std = array.std(axis=0, dtype=np.float64).astype(np.float32)
    std = np.maximum(std, np.float32(1e-6))
    return mean, std


@torch.no_grad()
def predict_delta(
    model: nn.Module,
    state: np.ndarray,
    action: np.ndarray,
    feature_mean: torch.Tensor,
    feature_std: torch.Tensor,
    target_mean: torch.Tensor,
    target_std: torch.Tensor,
    device: torch.device,
) -> np.ndarray:
    feature = torch.from_numpy(
        np.concatenate((state, action), axis=0).astype(np.float32)
    ).to(device)
    normalized = (feature - feature_mean) / feature_std
    prediction = model(normalized.unsqueeze(0)).squeeze(0)
    prediction = prediction * target_std + target_mean
    return prediction.detach().cpu().numpy().astype(np.float32)


@torch.no_grad()
def factual_residual(
    model: nn.Module,
    trace: Trace,
    window: int,
    tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
    device: torch.device,
) -> np.ndarray:
    feature_mean, feature_std, target_mean, target_std = tensors
    residuals = []
    start = max(0, len(trace.actions) - window)
    for index in range(start, len(trace.actions)):
        prediction = predict_delta(
            model,
            trace.states[index],
            trace.actions[index],
            feature_mean,
            feature_std,
            target_mean,
            target_std,
            device,
        )
        truth = trace.states[index + 1] - trace.states[index]
        residuals.append(truth - prediction)
    return np.mean(np.stack(residuals, axis=0), axis=0).astype(np.float32)


@torch.no_grad()
def rollout_endpoint(
    model: nn.Module,
    trace: Trace,
    residual: np.ndarray | None,
    decay: float,
    tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
    device: torch.device,
) -> np.ndarray:
    feature_mean, feature_std, target_mean, target_std = tensors
    state = trace.states[0].copy()
    for index, action in enumerate(trace.actions):
        delta = predict_delta(
            model,
            state,
            action,
            feature_mean,
            feature_std,
            target_mean,
            target_std,
            device,
        )
        if residual is not None:
            delta = delta + np.float32(decay**index) * residual
        state = state + delta
    return state


def normalized_rmse(
    prediction: np.ndarray,
    truth: np.ndarray,
    state_scale: np.ndarray,
    state_metric_mask: np.ndarray,
) -> float:
    # Exclude the simulator clock at index zero; it is deterministic and can
    # dominate neither manipulation state nor residual routing.
    normalized = (
        prediction[state_metric_mask] - truth[state_metric_mask]
    ) / state_scale[state_metric_mask]
    return float(np.sqrt(np.mean(np.square(normalized), dtype=np.float64)))


@torch.no_grad()
def action_conditioning_eval(
    model: nn.Module,
    records: list[dict[str, Any]],
    state_dim: int,
    feature_mean: torch.Tensor,
    feature_std: torch.Tensor,
    target_mean: torch.Tensor,
    target_std: torch.Tensor,
    device: torch.device,
    seed: int,
) -> dict[str, Any]:
    features, targets = transition_arrays(records)
    if features.shape[1] <= state_dim:
        raise ValueError("evaluation features contain no action dimensions")
    rng = np.random.default_rng(seed + 1701)
    permutation = rng.permutation(len(features))
    swapped = features.copy()
    swapped[:, state_dim:] = features[permutation, state_dim:]
    normalized_targets = (targets - target_mean.cpu().numpy()) / target_std.cpu().numpy()

    def mse(array: np.ndarray) -> tuple[float, np.ndarray]:
        tensor = torch.from_numpy(array.astype(np.float32)).to(device)
        prediction = model((tensor - feature_mean) / feature_std)
        prediction_np = prediction.detach().cpu().numpy()
        error = float(np.mean(np.square(prediction_np - normalized_targets), dtype=np.float64))
        return error, prediction_np

    matched_mse, matched_prediction = mse(features)
    swapped_mse, swapped_prediction = mse(swapped)
    prediction_shift = np.sqrt(
        np.mean(np.square(matched_prediction - swapped_prediction), axis=1, dtype=np.float64)
    )
    return {
        "transition_count": len(features),
        "matched_normalized_one_step_mse": matched_mse,
        "action_swapped_normalized_one_step_mse": swapped_mse,
        "action_swap_margin": swapped_mse - matched_mse,
        "positive_margin": bool(swapped_mse > matched_mse),
        "prediction_shift_mean": float(prediction_shift.mean()),
        "permutation_fixed_point_count": int(np.sum(permutation == np.arange(len(features)))),
    }


def aggregate(rows: list[dict[str, Any]], group: str) -> dict[str, Any]:
    selected = [row for row in rows if row["group"] == group]
    if not selected:
        return {"count": 0}
    base = np.asarray([row["base_error"] for row in selected], dtype=np.float64)
    global_error = np.asarray(
        [row["global_error"] for row in selected], dtype=np.float64
    )
    oracle = np.asarray([row["oracle_error"] for row in selected], dtype=np.float64)
    harm = global_error > base + 1e-12
    oracle_harm = oracle > base + 1e-12
    return {
        "count": len(selected),
        "block_count": len({row["block_identity"] for row in selected}),
        "base_error_mean": float(base.mean()),
        "global_error_mean": float(global_error.mean()),
        "oracle_error_mean": float(oracle.mean()),
        "global_minus_base_mean": float((global_error - base).mean()),
        "oracle_minus_base_mean": float((oracle - base).mean()),
        "global_correction_harm_rate": float(harm.mean()),
        "oracle_correction_harm_rate": float(oracle_harm.mean()),
        "global_rollback_regret_mean": float(np.maximum(global_error - base, 0).mean()),
        "oracle_rollback_regret_mean": float(np.maximum(oracle - base, 0).mean()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-lock", required=True)
    parser.add_argument("--run-lock-sha256", required=True)
    invocation = parser.parse_args()

    run_lock_path = personal_path(invocation.run_lock)
    if sha256_file(run_lock_path) != invocation.run_lock_sha256:
        raise ValueError("run-lock hash mismatch")
    run_lock = json.loads(run_lock_path.read_text(encoding="utf-8"))
    if (
        run_lock.get("kind") != "p027c_latent_wam_run_lock_v1"
        or run_lock.get("frozen") is not True
        or run_lock.get("frozen_before_target_wam_load") is not True
        or run_lock.get("selection_uses_downstream_wam") is not False
    ):
        raise ValueError("invalid or non-blind P027-C run lock")
    self_path = personal_path(__file__)
    if run_lock.get("runner") != {
        "path": str(self_path),
        "sha256": sha256_file(self_path),
    }:
        raise ValueError("run lock is bound to another runner")
    config = dict(run_lock["config"])
    expected_config_keys = {
        "seed",
        "epochs",
        "batch_size",
        "learning_rate",
        "width",
        "depth",
        "residual_window",
        "residual_decay",
        "device",
    }
    if set(config) != expected_config_keys:
        raise ValueError("run-lock config key set mismatch")
    artifacts = dict(run_lock["artifacts"])
    args = argparse.Namespace(
        manifest=run_lock["manifest"]["path"],
        output=artifacts["result"],
        checkpoint=artifacts["checkpoint"],
        eval_source_sha256=run_lock["eval_source_sha256"],
        **config,
    )

    if (
        args.epochs < 1
        or args.batch_size < 1
        or args.residual_window < 1
        or args.width < 1
        or args.depth < 1
        or not math.isfinite(float(args.learning_rate))
        or float(args.learning_rate) <= 0.0
    ):
        raise ValueError("training counts and learning-rate must be positive")
    if not math.isfinite(float(args.residual_decay)) or not 0.0 <= args.residual_decay <= 1.0:
        raise ValueError("residual-decay must be in [0, 1]")
    manifest_path = personal_path(args.manifest)
    output = personal_path(args.output, must_exist=False)
    checkpoint = personal_path(args.checkpoint, must_exist=False)
    if output == checkpoint or output == run_lock_path or checkpoint == run_lock_path:
        raise ValueError("run lock, output, and checkpoint paths must be distinct")
    if output.exists() or checkpoint.exists():
        raise FileExistsError("output/checkpoint already exists")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("kind") != "p027c_locked_latent_wam_manifest_v1":
        raise ValueError("unexpected manifest kind")
    if not manifest.get("compiler_target_wam_blind"):
        raise ValueError("manifest lacks target-WAM-blindness lock")
    if manifest.get("selection_uses_downstream_wam") is not False:
        raise ValueError("manifest does not forbid downstream-WAM selection")
    if sha256_file(manifest_path) != run_lock["manifest"]["sha256"]:
        raise ValueError("manifest differs from the frozen run lock")
    if canonical_sha256(manifest.get("records")) != manifest.get("records_sha256"):
        raise ValueError("manifest records hash mismatch")
    records = list(manifest["records"])
    eval_records = [
        record
        for record in records
        if record["rollout_sha256"] == args.eval_source_sha256
    ]
    if not eval_records:
        raise ValueError("eval source is absent from manifest")

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is unavailable")

    features, targets, train_meta = unique_transitions(
        records, args.eval_source_sha256
    )
    state_dim = targets.shape[1]
    action_dim = features.shape[1] - state_dim
    if state_dim <= 1 or action_dim <= 0:
        raise ValueError("invalid inferred state/action dimensions")
    feature_mean_np, feature_std_np = mean_std(features)
    target_mean_np, target_std_np = mean_std(targets)
    state_mean_np = features[:, :state_dim].mean(axis=0, dtype=np.float64).astype(np.float32)
    state_std_raw = features[:, :state_dim].std(axis=0, dtype=np.float64).astype(np.float32)
    state_scale_np = np.maximum(state_std_raw, np.float32(1e-3))
    state_metric_mask_np = state_std_raw > np.float32(1e-6)
    state_metric_mask_np[0] = False
    if not np.any(state_metric_mask_np):
        raise ValueError("no varying non-clock state dimensions for endpoint metric")
    normalized_features = (features - feature_mean_np) / feature_std_np
    normalized_targets = (targets - target_mean_np) / target_std_np

    dataset = TensorDataset(
        torch.from_numpy(normalized_features.astype(np.float32)),
        torch.from_numpy(normalized_targets.astype(np.float32)),
    )
    generator = torch.Generator().manual_seed(args.seed)
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        generator=generator,
        num_workers=0,
        drop_last=False,
    )
    model = DeltaWAM(
        input_dim=features.shape[1],
        output_dim=targets.shape[1],
        width=args.width,
        depth=args.depth,
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    loss_function = nn.MSELoss()
    history = []
    for epoch in range(args.epochs):
        model.train()
        losses = []
        for batch_features, batch_targets in loader:
            batch_features = batch_features.to(device)
            batch_targets = batch_targets.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = loss_function(model(batch_features), batch_targets)
            if not torch.isfinite(loss):
                raise RuntimeError(f"non-finite loss at epoch {epoch}")
            loss.backward()
            optimizer.step()
            losses.append(float(loss.detach().cpu()))
        history.append(float(np.mean(losses)))
    if not math.isfinite(history[-1]):
        raise RuntimeError("non-finite final training loss")

    tensors = (
        torch.from_numpy(feature_mean_np).to(device),
        torch.from_numpy(feature_std_np).to(device),
        torch.from_numpy(target_mean_np).to(device),
        torch.from_numpy(target_std_np).to(device),
    )
    model.eval()
    action_conditioning = action_conditioning_eval(
        model,
        eval_records,
        state_dim,
        tensors[0],
        tensors[1],
        tensors[2],
        tensors[3],
        device,
        args.seed,
    )
    action_gate_passed = bool(
        action_conditioning["positive_margin"]
        and action_conditioning["prediction_shift_mean"] > 1e-6
        and action_conditioning["permutation_fixed_point_count"]
        < action_conditioning["transition_count"]
    )
    if not action_gate_passed:
        failure_payload = {
            "kind": "p027c_latent_wam_action_conditioning_gate_failure_e0",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "claim_limit": (
                "The held-out action-conditioning gate failed. No residual-harm "
                "evaluation or checkpoint is authorized."
            ),
            "manifest_path": str(manifest_path),
            "manifest_sha256": sha256_file(manifest_path),
            "records_sha256": manifest["records_sha256"],
            "run_lock": {
                "path": str(run_lock_path),
                "sha256": invocation.run_lock_sha256,
            },
            "eval_source_sha256": args.eval_source_sha256,
            "train_eval_source_disjoint": True,
            "train": {
                **train_meta,
                "state_dim": state_dim,
                "action_dim": action_dim,
                "parameter_count": sum(
                    parameter.numel() for parameter in model.parameters()
                ),
                "initial_loss": history[0],
                "final_loss": history[-1],
                "epochs": args.epochs,
            },
            "action_conditioning": action_conditioning,
            "decision": {"action_conditioning_gate_passed": False},
            "checkpoint_written": False,
            "arguments": vars(args),
        }
        commit_json_no_clobber(output, failure_payload)
        print(json.dumps(failure_payload["decision"], sort_keys=True))
        raise SystemExit(2)
    endpoint_rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    for record in eval_records:
        certified_endpoint_values = {
            float(value)
            for pair in record["certified_endpoint_pairs"]
            for value in (pair["left_value"], pair["right_value"])
        }
        endpoint_by_value: dict[float, dict[str, Any]] = {}
        for endpoint_value, endpoint in sorted(
            record["endpoint_evidence"].items(), key=lambda item: float(item[0])
        ):
            path = personal_path(endpoint["path"])
            verify_evidence(path, str(endpoint["sha256"]))
            factual = load_trace(path, "factual")
            candidate = load_trace(path, "candidate")
            if factual.states.shape[1] != state_dim or candidate.states.shape[1] != state_dim:
                raise ValueError(f"state dimension mismatch in {path}")
            residual = factual_residual(
                model, factual, args.residual_window, tensors, device
            )
            base_endpoint = rollout_endpoint(
                model, candidate, None, args.residual_decay, tensors, device
            )
            global_endpoint = rollout_endpoint(
                model,
                candidate,
                residual,
                args.residual_decay,
                tensors,
                device,
            )
            factual_active = bool(np.any(factual.active[1:]))
            candidate_active = bool(np.any(candidate.active[1:]))
            overlap = factual_active and candidate_active
            oracle_endpoint = global_endpoint if overlap else base_endpoint
            truth = candidate.states[-1]
            group = "ordinary_overlap_endpoint" if overlap else "other_endpoint"
            if (
                float(endpoint_value) in certified_endpoint_values
                and not factual_active
                and candidate_active
            ):
                group = "certified_alias_pair_member"
            row = {
                "block_identity": record["block_identity"],
                "parameter_address": record["parameter_address"],
                "endpoint_value": float(endpoint_value),
                "group": group,
                "certified_alias": bool(record["certified_alias"]),
                "factual_active": factual_active,
                "candidate_active": candidate_active,
                "influence_overlap": overlap,
                "residual_l2": float(np.linalg.norm(residual[1:])),
                "base_error": normalized_rmse(
                    base_endpoint, truth, state_scale_np, state_metric_mask_np
                ),
                "global_error": normalized_rmse(
                    global_endpoint, truth, state_scale_np, state_metric_mask_np
                ),
                "oracle_error": normalized_rmse(
                    oracle_endpoint, truth, state_scale_np, state_metric_mask_np
                ),
                "evidence_path": str(path),
                "evidence_sha256": str(endpoint["sha256"]),
            }
            endpoint_rows.append(row)
            endpoint_by_value[float(endpoint_value)] = {
                "row": row,
                "truth": truth.copy(),
            }

        pair_specs: list[tuple[float, float, str, str | None]] = []
        if record["certified_alias"]:
            for pair in record["certified_endpoint_pairs"]:
                pair_specs.append(
                    (
                        float(pair["left_value"]),
                        float(pair["right_value"]),
                        "alias_pair",
                        str(pair["certificate_sha256"]),
                    )
                )
        else:
            overlap_values = sorted(
                value
                for value, endpoint_row in endpoint_by_value.items()
                if endpoint_row["row"]["influence_overlap"]
            )
            pair_specs.extend(
                (left, right, "ordinary_overlap_pair", None)
                for left, right in itertools.combinations(overlap_values, 2)
            )
        for left_value, right_value, group, certificate_sha256 in pair_specs:
            if left_value not in endpoint_by_value or right_value not in endpoint_by_value:
                raise ValueError("pair references an endpoint absent from the manifest record")
            left = endpoint_by_value[left_value]
            right = endpoint_by_value[right_value]
            if group == "alias_pair" and (
                left["row"]["group"] != "certified_alias_pair_member"
                or right["row"]["group"] != "certified_alias_pair_member"
            ):
                raise ValueError("certified pair activation evidence is inconsistent")
            pair_rows.append(
                {
                    "block_identity": record["block_identity"],
                    "parameter_address": record["parameter_address"],
                    "left_value": left_value,
                    "right_value": right_value,
                    "group": group,
                    "certificate_sha256": certificate_sha256,
                    "base_error": float(
                        np.mean([left["row"]["base_error"], right["row"]["base_error"]])
                    ),
                    "global_error": float(
                        np.mean(
                            [left["row"]["global_error"], right["row"]["global_error"]]
                        )
                    ),
                    "oracle_error": float(
                        np.mean(
                            [left["row"]["oracle_error"], right["row"]["oracle_error"]]
                        )
                    ),
                    "left_global_harmed": bool(
                        left["row"]["global_error"] > left["row"]["base_error"] + 1e-12
                    ),
                    "right_global_harmed": bool(
                        right["row"]["global_error"] > right["row"]["base_error"] + 1e-12
                    ),
                    "candidate_endpoint_separation": normalized_rmse(
                        left["truth"],
                        right["truth"],
                        state_scale_np,
                        state_metric_mask_np,
                    ),
                }
            )

    state = {
        "model_state_dict": model.state_dict(),
        "feature_mean": feature_mean_np,
        "feature_std": feature_std_np,
        "target_mean": target_mean_np,
        "target_std": target_std_np,
        "state_mean": state_mean_np,
        "state_scale": state_scale_np,
        "state_metric_mask": state_metric_mask_np,
        "arguments": vars(args),
        "manifest_sha256": sha256_file(manifest_path),
    }
    commit_checkpoint_no_clobber(checkpoint, state)
    checkpoint_sha256 = sha256_file(checkpoint)

    payload = {
        "kind": "p027c_leave_source_out_latent_residual_harm_e0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "claim_limit": (
            "Offline endpoint-prediction harm pilot on locked P026 evidence. "
            "The influence mask is oracle, no learned router or candidate-action "
            "ranking/closed-loop VLA improvement is claimed."
        ),
        "manifest_path": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "records_sha256": manifest["records_sha256"],
        "eval_source_sha256": args.eval_source_sha256,
        "train_eval_source_disjoint": True,
        "train": {
            **train_meta,
            "state_dim": state_dim,
            "action_dim": action_dim,
            "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
            "initial_loss": history[0],
            "final_loss": history[-1],
            "epochs": args.epochs,
        },
        "action_conditioning": action_conditioning,
        "endpoint_metric": {
            "name": "train-varying-dimension endpoint normalized RMSE",
            "state_scale_floor": 1e-3,
            "clock_excluded": True,
            "varying_dimension_count": int(np.sum(state_metric_mask_np)),
            "included_state_indices": np.flatnonzero(state_metric_mask_np).tolist(),
        },
        "correction": {
            "residual_source": "mean teacher-forced one-step state residual over factual tail",
            "transport": "global residual added to candidate transition with exponential decay",
            "residual_window": args.residual_window,
            "residual_decay": args.residual_decay,
            "oracle_rule": "transport iff selected physical interface is active in factual and candidate",
        },
        "aggregates": {
            group: aggregate(pair_rows, group)
            for group in ("alias_pair", "ordinary_overlap_pair")
        },
        "pair_rows": pair_rows,
        "endpoint_rows": endpoint_rows,
        "checkpoint": str(checkpoint),
        "checkpoint_sha256": checkpoint_sha256,
        "arguments": vars(args),
        "run_lock": {"path": str(run_lock_path), "sha256": invocation.run_lock_sha256},
        "run_commit_protocol": run_lock["failure_recovery"],
    }
    alias_summary = payload["aggregates"]["alias_pair"]
    payload["decision"] = {
        "action_conditioning_gate_passed": action_gate_passed,
        "alias_evidence_present": int(alias_summary.get("count", 0)) > 0,
        "global_residual_harm_observed": bool(
            alias_summary.get("global_correction_harm_rate", 0.0) > 0.0
        ),
        "followup_ranking_experiment_gate_passed": bool(
            action_conditioning["positive_margin"]
            and int(alias_summary.get("count", 0)) > 0
            and alias_summary.get("global_correction_harm_rate", 0.0) > 0.0
        ),
        "candidate_action_ranking_claim_supported": False,
    }
    commit_json_no_clobber(output, payload)
    print(
        json.dumps(
            {
                "output": str(output),
                "checkpoint_sha256": checkpoint_sha256,
                "train": payload["train"],
                "aggregates": payload["aggregates"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
