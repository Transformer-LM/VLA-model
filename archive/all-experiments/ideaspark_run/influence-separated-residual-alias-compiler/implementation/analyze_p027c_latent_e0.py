"""Block-level and severity-matched analysis for the locked P027-C E0 result."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def block_rows(
    rows: list[dict[str, Any]],
    group: str,
    metadata: dict[str, dict[str, Any]],
    candidate_index: int | None,
) -> list[dict[str, Any]]:
    by_block: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        record = metadata[row["block_identity"]]
        if row["group"] == group and (
            candidate_index is None
            or int(record["candidate_chunk_index"]) == candidate_index
        ):
            by_block.setdefault(row["block_identity"], []).append(row)
    output = []
    for identity, values in sorted(by_block.items()):
        delta = np.asarray(
            [row["global_error"] - row["base_error"] for row in values],
            dtype=np.float64,
        )
        output.append(
            {
                "block_identity": identity,
                "parameter_address": values[0]["parameter_address"],
                "candidate_chunk_index": int(metadata[identity]["candidate_chunk_index"]),
                "candidate_boundary_step": int(metadata[identity]["candidate_boundary_step"]),
                "geom_ids": list(metadata[identity]["geom_ids"]),
                "pair_count": len(values),
                "severity": float(
                    np.mean([row["candidate_endpoint_separation"] for row in values])
                ),
                "global_minus_base_mean": float(delta.mean()),
                "correction_harm_rate": float(np.mean(delta > 1e-12)),
                "rollback_regret_mean": float(np.maximum(delta, 0).mean()),
            }
        )
    return output


def ordered_subset_match(
    aliases: list[dict[str, Any]], controls: list[dict[str, Any]]
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    aliases = sorted(aliases, key=lambda row: row["severity"])
    controls = sorted(controls, key=lambda row: row["severity"])
    n, m = len(aliases), len(controls)
    if n > m:
        raise ValueError("fewer control than alias blocks")
    infinity = float("inf")
    cost = np.full((n + 1, m + 1), infinity, dtype=np.float64)
    take = np.zeros((n + 1, m + 1), dtype=bool)
    cost[0, :] = 0.0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            skip_cost = cost[i, j - 1]
            pair_cost = cost[i - 1, j - 1] + abs(
                math.log(max(aliases[i - 1]["severity"], 1e-12))
                - math.log(max(controls[j - 1]["severity"], 1e-12))
            )
            if pair_cost < skip_cost:
                cost[i, j] = pair_cost
                take[i, j] = True
            else:
                cost[i, j] = skip_cost
    matches = []
    i, j = n, m
    while i > 0:
        if j <= 0:
            raise RuntimeError("matching reconstruction failed")
        if take[i, j]:
            matches.append((aliases[i - 1], controls[j - 1]))
            i -= 1
            j -= 1
        else:
            j -= 1
    matches.reverse()
    return matches


def bootstrap_ci(values: np.ndarray, seed: int, draws: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(values), size=(draws, len(values)))
    estimates = values[indices].mean(axis=1)
    return {
        "mean": float(values.mean()),
        "ci95_lower": float(np.quantile(estimates, 0.025)),
        "ci95_upper": float(np.quantile(estimates, 0.975)),
        "bootstrap_probability_gt_zero": float(np.mean(estimates > 0.0)),
    }


def sign_flip_pvalue(values: np.ndarray) -> float:
    observed = abs(float(values.mean()))
    count = 0
    total = 0
    for signs in itertools.product((-1.0, 1.0), repeat=len(values)):
        estimate = abs(float(np.mean(values * np.asarray(signs))))
        count += int(estimate >= observed - 1e-15)
        total += 1
    return count / total


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--candidate-index", type=int)
    parser.add_argument("--seed", type=int, default=20260902)
    parser.add_argument("--bootstrap-draws", type=int, default=50000)
    args = parser.parse_args()
    source = Path(args.input).resolve(strict=True)
    output = Path(args.output).resolve()
    if output.exists():
        raise FileExistsError(output)
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("kind") != "p027c_leave_source_out_latent_residual_harm_e0":
        raise ValueError("unexpected E0 result kind")
    manifest_path = Path(args.manifest).resolve(strict=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    metadata = {record["block_identity"]: record for record in manifest["records"]}
    aliases = block_rows(
        payload["pair_rows"], "alias_pair", metadata, args.candidate_index
    )
    controls = block_rows(
        payload["pair_rows"], "ordinary_overlap_pair", metadata, args.candidate_index
    )
    matches = ordered_subset_match(aliases, controls)

    matched_rows = []
    for alias, control in matches:
        matched_rows.append(
            {
                "alias_block": alias["block_identity"],
                "control_block": control["block_identity"],
                "alias_severity": alias["severity"],
                "control_severity": control["severity"],
                "log_severity_distance": abs(
                    math.log(max(alias["severity"], 1e-12))
                    - math.log(max(control["severity"], 1e-12))
                ),
                "delta_harm_difference": (
                    alias["global_minus_base_mean"]
                    - control["global_minus_base_mean"]
                ),
                "harm_rate_difference": (
                    alias["correction_harm_rate"]
                    - control["correction_harm_rate"]
                ),
                "rollback_regret_difference": (
                    alias["rollback_regret_mean"]
                    - control["rollback_regret_mean"]
                ),
            }
        )
    metrics = {}
    for key in (
        "delta_harm_difference",
        "harm_rate_difference",
        "rollback_regret_difference",
    ):
        values = np.asarray([row[key] for row in matched_rows], dtype=np.float64)
        metrics[key] = {
            **bootstrap_ci(values, args.seed, args.bootstrap_draws),
            "exact_sign_flip_two_sided_p": sign_flip_pvalue(values),
            "positive_pair_count": int(np.sum(values > 0)),
            "negative_pair_count": int(np.sum(values < 0)),
            "zero_pair_count": int(np.sum(values == 0)),
        }
    analysis = {
        "kind": "p027c_latent_e0_exact_boundary_block_matched_analysis_v2",
        "claim_limit": (
            "Exploratory one-seed, one-held-out-source, exact-candidate-boundary "
            "block-level analysis. "
            "Blocks are the resampling unit; this is not a candidate-action ranking "
            "or closed-loop policy result."
        ),
        "input": str(source),
        "input_sha256": sha256_file(source),
        "manifest": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "candidate_index_filter": args.candidate_index,
        "alias_block_count": len(aliases),
        "control_block_count": len(controls),
        "matched_block_pair_count": len(matches),
        "matching": "optimal ordered 1:1 subset matching on absolute log severity distance",
        "mean_log_severity_distance": float(
            np.mean([row["log_severity_distance"] for row in matched_rows])
        ),
        "metrics": metrics,
        "alias_blocks": aliases,
        "control_blocks": controls,
        "matched_rows": matched_rows,
        "seed": args.seed,
        "bootstrap_draws": args.bootstrap_draws,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp.{os.getpid()}")
    temporary.write_text(
        json.dumps(analysis, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.link(temporary, output)
    temporary.unlink()
    print(json.dumps(metrics, sort_keys=True))


if __name__ == "__main__":
    main()
