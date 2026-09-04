"""Calibrate a strong global residual-transport baseline before alias evaluation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def personal_path(raw: str, *, must_exist: bool = True) -> Path:
    path = Path(raw).resolve(strict=must_exist)
    if not str(path).startswith(
        ("<PERSONAL_RESEARCH_ROOT>/", "<PERSONAL_RESEARCH_ROOT_ALIAS>/")
    ):
        raise ValueError(f"path is outside liu_meng personal storage: {path}")
    return path


def canonical_sha256(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    ).hexdigest()


def load_support(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("p027c_latent_support", path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    # dataclasses resolves postponed annotations through sys.modules while the
    # support module is executing.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@torch.no_grad()
def rollout_endpoint_grid(
    support: Any,
    model: torch.nn.Module,
    trace: Any,
    residual: np.ndarray,
    configurations: list[tuple[float, float]],
    tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
    device: torch.device,
) -> np.ndarray:
    """Roll out every calibration configuration in one batched trajectory."""
    feature_mean, feature_std, target_mean, target_std = tensors
    count = len(configurations)
    state = torch.from_numpy(
        np.repeat(trace.states[0][None, :], count, axis=0).astype(np.float32)
    ).to(device)
    residual_tensor = torch.from_numpy(residual.astype(np.float32)).to(device)
    alpha = torch.tensor(
        [configuration[0] for configuration in configurations],
        dtype=torch.float32,
        device=device,
    ).unsqueeze(1)
    decay = torch.tensor(
        [configuration[1] for configuration in configurations],
        dtype=torch.float32,
        device=device,
    ).unsqueeze(1)
    for index, action in enumerate(trace.actions):
        action_tensor = torch.from_numpy(action.astype(np.float32)).to(device)
        repeated_action = action_tensor.unsqueeze(0).expand(count, -1)
        feature = torch.cat((state, repeated_action), dim=1)
        prediction = model((feature - feature_mean) / feature_std)
        prediction = prediction * target_std + target_mean
        correction = alpha * torch.pow(decay, index) * residual_tensor.unsqueeze(0)
        state = state + prediction + correction
    return state.detach().cpu().numpy().astype(np.float32)


def raw_state_rmse(
    prediction: np.ndarray, truth: np.ndarray, state_metric_mask: np.ndarray
) -> float:
    error = prediction[state_metric_mask] - truth[state_metric_mask]
    return float(np.sqrt(np.mean(np.square(error), dtype=np.float64)))


def mean_by_source(values: dict[str, list[float]]) -> float:
    if not values or any(not rows for rows in values.values()):
        raise ValueError("empty source-stratified calibration values")
    return float(np.mean([np.mean(rows) for rows in values.values()]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-lock", required=True)
    parser.add_argument("--run-lock-sha256", required=True)
    invocation = parser.parse_args()

    lock_path = personal_path(invocation.run_lock)
    if sha256_file(lock_path) != invocation.run_lock_sha256:
        raise ValueError("run-lock hash mismatch")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if (
        lock.get("kind") != "p027c_calibrated_transport_run_lock_v1"
        or lock.get("frozen") is not True
        or lock.get("frozen_before_calibration_outcomes") is not True
        or lock.get("selection_uses_downstream_heldout_outcomes") is not False
    ):
        raise ValueError("invalid calibrated-transport run lock")
    self_path = personal_path(__file__)
    if lock["evaluator"] != {
        "path": str(self_path),
        "sha256": sha256_file(self_path),
    }:
        raise ValueError("run lock is bound to another evaluator")
    support_path = personal_path(lock["support"]["path"])
    if lock["support"]["sha256"] != sha256_file(support_path):
        raise ValueError("support module hash mismatch")
    manifest_path = personal_path(lock["manifest"]["path"])
    checkpoint_path = personal_path(lock["checkpoint"]["path"])
    if sha256_file(manifest_path) != lock["manifest"]["sha256"]:
        raise ValueError("manifest hash mismatch")
    if sha256_file(checkpoint_path) != lock["checkpoint"]["sha256"]:
        raise ValueError("checkpoint hash mismatch")
    output = personal_path(lock["output"], must_exist=False)
    if output.exists() or output in {lock_path, manifest_path, checkpoint_path}:
        raise FileExistsError("invalid or occupied output path")
    # Only import executable support code after every root-of-trust artifact has
    # been authenticated by functions defined in this evaluator.
    support = load_support(support_path)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("compiler_target_wam_blind") is not True
        or manifest.get("selection_uses_downstream_wam") is not False
        or canonical_sha256(manifest["records"])
        != manifest["records_sha256"]
    ):
        raise ValueError("manifest integrity/blindness failed")
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    if checkpoint.get("manifest_sha256") != lock["manifest"]["sha256"]:
        raise ValueError("checkpoint was trained from a different manifest")
    original_args = dict(checkpoint["arguments"])
    if original_args["eval_source_sha256"] != lock["eval_source_sha256"]:
        raise ValueError("checkpoint and calibration lock use different held-out source")
    if int(original_args["residual_window"]) != int(lock["residual_window"]):
        raise ValueError("calibration residual window differs from the trained E0 protocol")
    device = torch.device(lock["device"])
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    state_dim = int(np.asarray(checkpoint["target_mean"]).shape[0])
    feature_dim = int(np.asarray(checkpoint["feature_mean"]).shape[0])
    model = support.DeltaWAM(
        input_dim=feature_dim,
        output_dim=state_dim,
        width=int(original_args["width"]),
        depth=int(original_args["depth"]),
    ).to(device)
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    model.eval()
    tensors = tuple(
        torch.from_numpy(np.asarray(checkpoint[key], dtype=np.float32)).to(device)
        for key in ("feature_mean", "feature_std", "target_mean", "target_std")
    )
    state_scale = np.asarray(checkpoint["state_scale"], dtype=np.float32)
    state_metric_mask = np.asarray(checkpoint["state_metric_mask"], dtype=bool)

    alphas = [float(value) for value in lock["alpha_grid"]]
    decays = [float(value) for value in lock["decay_grid"]]
    if (
        alphas != sorted(set(alphas))
        or not alphas
        or alphas[0] != 0.0
        or any(not math.isfinite(value) or value < 0.0 for value in alphas)
        or any(not math.isfinite(value) or not 0.0 <= value <= 1.0 for value in decays)
    ):
        raise ValueError("invalid frozen calibration grid")
    configurations = [(0.0, 0.0)] + [
        (alpha, decay) for alpha in alphas if alpha > 0.0 for decay in decays
    ]
    records = list(manifest["records"])
    eval_source = lock["eval_source_sha256"]
    eval_indices_list = [int(value) for value in lock["eval_candidate_indices"]]
    if eval_indices_list != sorted(set(eval_indices_list)) or not eval_indices_list:
        raise ValueError("held-out candidate indices are empty, duplicated, or unsorted")
    eval_boundaries: dict[int, set[int]] = defaultdict(set)
    for record in records:
        if record["rollout_sha256"] == eval_source:
            eval_boundaries[int(record["candidate_chunk_index"])].add(
                int(record["candidate_boundary_step"])
            )
    if any(
        index not in eval_boundaries or len(eval_boundaries[index]) != 1
        for index in eval_indices_list
    ):
        raise ValueError("held-out candidate index is absent or maps to multiple boundaries")
    calibration_values: dict[tuple[float, float], dict[str, list[float]]] = {
        config: defaultdict(list) for config in configurations
    }
    calibration_endpoint_count = 0
    for record in records:
        source = str(record["rollout_sha256"])
        if source == eval_source:
            continue
        for endpoint in record["endpoint_evidence"].values():
            path = support.personal_path(endpoint["path"])
            support.verify_evidence(path, str(endpoint["sha256"]))
            factual = support.load_trace(path, "factual")
            candidate = support.load_trace(path, "candidate")
            overlap = bool(np.any(factual.active[1:]) and np.any(candidate.active[1:]))
            if not overlap:
                continue
            residual = support.factual_residual(
                model,
                factual,
                int(lock["residual_window"]),
                tensors,
                device,
            )
            truth = candidate.states[-1]
            predictions = rollout_endpoint_grid(
                support,
                model,
                candidate,
                residual,
                configurations,
                tensors,
                device,
            )
            for (alpha, decay), prediction in zip(configurations, predictions):
                error = support.normalized_rmse(
                    prediction, truth, state_scale, state_metric_mask
                )
                calibration_values[(alpha, decay)][source].append(error)
            calibration_endpoint_count += 1
    objectives = {
        config: mean_by_source(source_values)
        for config, source_values in calibration_values.items()
    }
    selected = min(objectives, key=lambda item: (objectives[item], item[0], item[1]))
    base_objective = objectives[(0.0, 0.0)]
    selected_objective = objectives[selected]
    relative_improvement = (base_objective - selected_objective) / max(
        abs(base_objective), 1e-12
    )
    calibration_gate = bool(
        selected[0] > 0.0
        and relative_improvement >= float(lock["minimum_relative_control_improvement"])
    )
    calibration_summary = {
        "endpoint_count": calibration_endpoint_count,
        "source_count": len(next(iter(calibration_values.values()))),
        "base_objective": base_objective,
        "selected_alpha": selected[0],
        "selected_decay": selected[1],
        "selected_objective": selected_objective,
        "relative_control_improvement": relative_improvement,
        "minimum_relative_control_improvement": float(
            lock["minimum_relative_control_improvement"]
        ),
        "gate_passed": calibration_gate,
        "grid": [
            {"alpha": key[0], "decay": key[1], "objective": objectives[key]}
            for key in sorted(objectives)
        ],
    }
    if not calibration_gate:
        payload = {
            "kind": "p027c_calibrated_transport_control_gate_failure_e0",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "claim_limit": (
                "Global residual transport did not improve source-stratified ordinary "
                "overlap calibration controls. Held-out alias evaluation was not run."
            ),
            "run_lock": {"path": str(lock_path), "sha256": invocation.run_lock_sha256},
            "calibration": calibration_summary,
            "decision": {
                "calibration_gate_passed": False,
                "heldout_alias_evaluation_authorized": False,
                "learned_router_authorized": False,
            },
        }
        support.commit_json_no_clobber(output, payload)
        print(json.dumps(payload["decision"], sort_keys=True))
        raise SystemExit(2)

    endpoint_rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    eval_indices = set(eval_indices_list)
    for record in records:
        if (
            record["rollout_sha256"] != eval_source
            or int(record["candidate_chunk_index"]) not in eval_indices
        ):
            continue
        certified_values = {
            float(value)
            for pair in record["certified_endpoint_pairs"]
            for value in (pair["left_value"], pair["right_value"])
        }
        by_value: dict[float, dict[str, Any]] = {}
        for endpoint_value, endpoint in record["endpoint_evidence"].items():
            value = float(endpoint_value)
            path = support.personal_path(endpoint["path"])
            support.verify_evidence(path, str(endpoint["sha256"]))
            factual = support.load_trace(path, "factual")
            candidate = support.load_trace(path, "candidate")
            residual = support.factual_residual(
                model, factual, int(lock["residual_window"]), tensors, device
            )
            base = support.rollout_endpoint(model, candidate, None, 0.0, tensors, device)
            corrected = support.rollout_endpoint(
                model,
                candidate,
                residual * np.float32(selected[0]),
                selected[1],
                tensors,
                device,
            )
            overlap = bool(np.any(factual.active[1:]) and np.any(candidate.active[1:]))
            factual_active = bool(np.any(factual.active[1:]))
            candidate_active = bool(np.any(candidate.active[1:]))
            truth = candidate.states[-1]
            base_error = support.normalized_rmse(
                base, truth, state_scale, state_metric_mask
            )
            corrected_error = support.normalized_rmse(
                corrected, truth, state_scale, state_metric_mask
            )
            base_raw_error = raw_state_rmse(base, truth, state_metric_mask)
            corrected_raw_error = raw_state_rmse(
                corrected, truth, state_metric_mask
            )
            residual_normalized_magnitude = support.normalized_rmse(
                residual,
                np.zeros_like(residual),
                state_scale,
                state_metric_mask,
            )
            row = {
                "block_identity": record["block_identity"],
                "candidate_chunk_index": int(record["candidate_chunk_index"]),
                "candidate_boundary_step": int(record["candidate_boundary_step"]),
                "parameter_address": record["parameter_address"],
                "endpoint_value": value,
                "certified_pair_member": value in certified_values,
                "factual_active": factual_active,
                "candidate_active": candidate_active,
                "influence_overlap": overlap,
                "base_error": base_error,
                "global_error": corrected_error,
                "base_raw_state_rmse": base_raw_error,
                "global_raw_state_rmse": corrected_raw_error,
                "residual_normalized_magnitude": residual_normalized_magnitude,
                "oracle_error": corrected_error if overlap else base_error,
            }
            endpoint_rows.append(row)
            by_value[value] = {"row": row, "truth": truth}
        if record["certified_alias"]:
            pair_specs = [
                (
                    float(pair["left_value"]),
                    float(pair["right_value"]),
                    "alias_pair",
                    pair["certificate_sha256"],
                )
                for pair in record["certified_endpoint_pairs"]
            ]
        else:
            values = sorted(
                value for value, item in by_value.items() if item["row"]["influence_overlap"]
            )
            pair_specs = [
                (left, right, "ordinary_overlap_pair", None)
                for left_index, left in enumerate(values)
                for right in values[left_index + 1 :]
            ]
        for left_value, right_value, group, certificate in pair_specs:
            left, right = by_value[left_value], by_value[right_value]
            if group == "alias_pair" and not (
                left["row"]["certified_pair_member"]
                and right["row"]["certified_pair_member"]
                and not left["row"]["factual_active"]
                and left["row"]["candidate_active"]
                and not right["row"]["factual_active"]
                and right["row"]["candidate_active"]
            ):
                raise ValueError("certified alias activation/pair membership mismatch")
            pair_rows.append(
                {
                    "block_identity": record["block_identity"],
                    "candidate_chunk_index": int(record["candidate_chunk_index"]),
                    "candidate_boundary_step": int(record["candidate_boundary_step"]),
                    "parameter_address": record["parameter_address"],
                    "left_value": left_value,
                    "right_value": right_value,
                    "group": group,
                    "certificate_sha256": certificate,
                    "base_error": float(
                        np.mean([left["row"]["base_error"], right["row"]["base_error"]])
                    ),
                    "global_error": float(
                        np.mean([left["row"]["global_error"], right["row"]["global_error"]])
                    ),
                    "base_raw_state_rmse": float(
                        np.mean(
                            [
                                left["row"]["base_raw_state_rmse"],
                                right["row"]["base_raw_state_rmse"],
                            ]
                        )
                    ),
                    "global_raw_state_rmse": float(
                        np.mean(
                            [
                                left["row"]["global_raw_state_rmse"],
                                right["row"]["global_raw_state_rmse"],
                            ]
                        )
                    ),
                    "residual_normalized_magnitude": float(
                        np.mean(
                            [
                                left["row"]["residual_normalized_magnitude"],
                                right["row"]["residual_normalized_magnitude"],
                            ]
                        )
                    ),
                    "oracle_error": float(
                        np.mean([left["row"]["oracle_error"], right["row"]["oracle_error"]])
                    ),
                    "candidate_endpoint_separation": support.normalized_rmse(
                        left["truth"], right["truth"], state_scale, state_metric_mask
                    ),
                }
            )
    by_boundary = {}
    for index in sorted(eval_indices):
        selected_rows = [row for row in pair_rows if row["candidate_chunk_index"] == index]
        by_boundary[str(index)] = {
            group: support.aggregate(selected_rows, group)
            for group in ("alias_pair", "ordinary_overlap_pair")
        }
        if any(by_boundary[str(index)][group].get("count", 0) == 0 for group in by_boundary[str(index)]):
            raise ValueError(f"candidate boundary {index} lacks alias or ordinary controls")
    boundary_gates = {
        str(index): {
            "heldout_ordinary_control_improved": bool(
                by_boundary[str(index)]["ordinary_overlap_pair"][
                    "global_minus_base_mean"
                ]
                < 0.0
            ),
            "alias_mean_harm_descriptive": bool(
                by_boundary[str(index)]["alias_pair"]["global_minus_base_mean"]
                > 0.0
            ),
        }
        for index in sorted(eval_indices)
    }
    payload = {
        "kind": "p027c_calibrated_global_transport_heldout_alias_e0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "claim_limit": (
            "Exploratory calibrated global-transport evaluation on one held-out "
            "rollout source. No candidate ranking, learned router, or VLA claim."
        ),
        "run_lock": {"path": str(lock_path), "sha256": invocation.run_lock_sha256},
        "calibration": calibration_summary,
        "calibration_independence": {
            "calibration_sources_were_seen_during_wam_training": True,
            "heldout_source_was_not_used_for_calibration_or_wam_training": True,
            "interpretation": (
                "Training-side transport calibration only; scientific interpretation "
                "requires improvement on held-out ordinary-overlap controls."
            ),
        },
        "evaluation_by_candidate_index": by_boundary,
        "heldout_boundary_gates": boundary_gates,
        "pair_rows": pair_rows,
        "endpoint_rows": endpoint_rows,
        "decision": {
            "calibration_gate_passed": True,
            "any_exact_boundary_descriptive_pattern_observed": any(
                gate["heldout_ordinary_control_improved"]
                and gate["alias_mean_harm_descriptive"]
                for gate in boundary_gates.values()
            ),
            "candidate_action_ranking_claim_supported": False,
            "learned_router_claim_supported": False,
        },
    }
    support.commit_json_no_clobber(output, payload)
    print(json.dumps({"calibration": calibration_summary, "evaluation": by_boundary}, sort_keys=True))


if __name__ == "__main__":
    main()
