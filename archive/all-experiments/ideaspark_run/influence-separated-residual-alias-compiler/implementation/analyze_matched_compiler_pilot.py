#!/usr/bin/env python3
"""Aggregate ISRAC and matched-call compiler baselines.

The script intentionally uses only JSON artifacts and the Python standard
library. It never treats a missing run as a zero-result run: completeness is
reported explicitly and an incomplete selector cannot pass the decision gate.
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import math
import random
import statistics
from pathlib import Path
from typing import Any, Iterable


def boundary_key(record: dict[str, Any]) -> str:
    rollout = Path(record["rollout"]).name
    index = int(record["candidate_chunk_index"])
    return f"{rollout}::c{index:02d}"


def load_records(pattern: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(glob.glob(pattern)):
        with open(path, "r", encoding="utf-8") as handle:
            record = json.load(handle)
        record["_path"] = path
        records.append(record)
    return records


def rollout_calls(record: dict[str, Any]) -> int:
    if "total_rollouts_including_selection" in record:
        return int(record["total_rollouts_including_selection"])
    selected = int(record.get("selected_block_count", len(record.get("blocks", []))))
    selection = int(record.get("selection_contact_rollouts", 2))
    per_block = int(record.get("physics_rollouts_per_selected_block", 8))
    return selection + selected * per_block


def unique_witnesses(record: dict[str, Any]) -> int:
    """Count at most one primary witness per boundary/parameter block.

    The current E0 uses one task-independent pose-effect vector, so every
    passing block has one effect signature. Endpoint pairs for the same block
    are strength variants and are deliberately not independent discoveries.
    """

    return sum(int(block.get("certified_pairs", 0) > 0) for block in record.get("blocks", []))


def summarize(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    records = list(records)
    pairs = sum(int(item.get("compiled_pair_count", 0)) for item in records)
    calls = sum(rollout_calls(item) for item in records)
    blocks = sum(len(item.get("blocks", [])) for item in records)
    passing_blocks = sum(
        int(block.get("certified_pairs", 0) > 0)
        for item in records
        for block in item.get("blocks", [])
    )
    failures: collections.Counter[str] = collections.Counter()
    certificates: set[str] = set()
    equality_violations = 0
    aligned = 0
    measured_pairs = 0
    max_effect = 0.0
    for item in records:
        for block in item.get("blocks", []):
            failures.update(block.get("failure_reason_counts", {}))
        for pair in item.get("best_pairs", []):
            certificate = pair.get("certificate_sha256")
            if certificate:
                certificates.add(str(certificate))
            measurements = pair.get("measurements", {})
            measured_pairs += 1
            max_effect = max(
                max_effect,
                float(measurements.get("candidate_task_effect_max_abs", 0.0)),
            )
            equality_fields = (
                "factual_rgb_max_abs",
                "factual_depth_max_abs",
                "factual_proprio_max_abs",
                "factual_physical_effect_probe_max_abs",
                # Legacy P022/P024 name for the same simulator-native proxy.
                "factual_residual_max_abs",
                "factual_state_max_abs",
            )
            if any(float(measurements.get(field, 0.0)) != 0.0 for field in equality_fields):
                equality_violations += 1
            if measurements.get("parameter_first_activation_frame") == measurements.get(
                "candidate_first_divergence_frame"
            ):
                aligned += 1
    return {
        "run_count": len(records),
        "boundary_count": len({boundary_key(item) for item in records}),
        "certified_pairs": pairs,
        "unique_witnesses": passing_blocks,
        "unique_certificates": len(certificates),
        "simulator_rollouts": calls,
        "yield_per_1k_rollouts": 1000.0 * pairs / calls if calls else None,
        "selected_blocks": blocks,
        "passing_blocks": passing_blocks,
        "passing_block_rate": passing_blocks / blocks if blocks else None,
        "measured_pairs": measured_pairs,
        "factual_equality_violations": equality_violations,
        "activation_divergence_alignment_rate": aligned / measured_pairs if measured_pairs else None,
        "max_task_effect_component": max_effect,
        "failure_reason_counts": dict(sorted(failures.items())),
    }


def group_baselines(records: Iterable[dict[str, Any]]) -> dict[str, dict[int, list[dict[str, Any]]]]:
    grouped: dict[str, dict[int, list[dict[str, Any]]]] = collections.defaultdict(
        lambda: collections.defaultdict(list)
    )
    for item in records:
        selector = str(item["block_selector"])
        seed = int(item["selector_seed"])
        grouped[selector][seed].append(item)
    return {selector: dict(seeds) for selector, seeds in grouped.items()}


def paired_bootstrap_ratio(
    israc: list[dict[str, Any]],
    baseline_by_seed: dict[int, list[dict[str, Any]]],
    *,
    samples: int,
    seed: int,
    metric: str,
) -> dict[str, Any]:
    israc_by_boundary = {boundary_key(item): item for item in israc}
    baseline_lookup = {
        compiler_seed: {boundary_key(item): item for item in items}
        for compiler_seed, items in baseline_by_seed.items()
    }
    complete_seeds = [
        compiler_seed
        for compiler_seed, items in baseline_lookup.items()
        if set(items) == set(israc_by_boundary)
    ]
    keys = sorted(israc_by_boundary)
    if not keys or not complete_seeds:
        return {
            "complete": False,
            "reason": "no baseline seed covers every ISRAC boundary",
            "complete_seeds": complete_seeds,
        }

    rng = random.Random(seed)
    ratios: list[float] = []
    infinite = 0
    for _ in range(samples):
        sampled_keys = [rng.choice(keys) for _ in keys]
        method_pairs = method_calls = baseline_pairs = baseline_calls = 0
        for key in sampled_keys:
            compiler_seed = rng.choice(complete_seeds)
            method = israc_by_boundary[key]
            baseline = baseline_lookup[compiler_seed][key]
            if metric == "unique_witnesses":
                method_pairs += unique_witnesses(method)
                baseline_pairs += unique_witnesses(baseline)
            elif metric == "raw_pairs":
                method_pairs += int(method.get("compiled_pair_count", 0))
                baseline_pairs += int(baseline.get("compiled_pair_count", 0))
            else:
                raise ValueError(metric)
            method_calls += rollout_calls(method)
            baseline_calls += rollout_calls(baseline)
        method_yield = method_pairs / method_calls if method_calls else 0.0
        baseline_yield = baseline_pairs / baseline_calls if baseline_calls else 0.0
        if baseline_yield == 0.0:
            infinite += 1
        else:
            ratios.append(method_yield / baseline_yield)

    ratios.sort()

    def quantile(q: float) -> float | None:
        if not ratios:
            return None
        position = q * (len(ratios) - 1)
        lo = math.floor(position)
        hi = math.ceil(position)
        if lo == hi:
            return ratios[lo]
        weight = position - lo
        return ratios[lo] * (1.0 - weight) + ratios[hi] * weight

    return {
        "complete": True,
        "bootstrap_samples": samples,
        "finite_samples": len(ratios),
        "infinite_ratio_samples": infinite,
        "complete_seeds": complete_seeds,
        "median": quantile(0.5),
        "ci95": [quantile(0.025), quantile(0.975)],
        "probability_ratio_ge_2": (
            (sum(value >= 2.0 for value in ratios) + infinite) / samples
        ),
        "probability_ratio_gt_1": (
            (sum(value > 1.0 for value in ratios) + infinite) / samples
        ),
    }


def analyze(
    israc_records: list[dict[str, Any]],
    baseline_records: list[dict[str, Any]],
    *,
    bootstrap_samples: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    expected_boundaries = sorted({boundary_key(item) for item in israc_records})
    grouped = group_baselines(baseline_records)
    baselines: dict[str, Any] = {}
    selector_point_yields: dict[str, float] = {}
    all_selectors_have_three_complete_seeds = bool(grouped)
    for selector, seeds in grouped.items():
        seed_summaries: dict[str, Any] = {}
        for seed, items in sorted(seeds.items()):
            summary = summarize(items)
            present = sorted({boundary_key(item) for item in items})
            summary["complete"] = present == expected_boundaries
            summary["missing_boundaries"] = sorted(set(expected_boundaries) - set(present))
            seed_summaries[str(seed)] = summary
        complete_seed_summaries = [
            value for value in seed_summaries.values() if value["complete"]
        ]
        if len(complete_seed_summaries) < 3:
            all_selectors_have_three_complete_seeds = False
        unique_yields = [
            1000.0 * value["unique_witnesses"] / value["simulator_rollouts"]
            for value in complete_seed_summaries
            if value["simulator_rollouts"]
        ]
        if unique_yields:
            selector_point_yields[selector] = statistics.mean(unique_yields)
        baselines[selector] = {
            "seeds": seed_summaries,
            "complete_seed_count": len(complete_seed_summaries),
            "mean_unique_witness_yield_per_1k_rollouts": (
                statistics.mean(unique_yields) if unique_yields else None
            ),
            "std_unique_witness_yield_per_1k_rollouts": (
                statistics.stdev(unique_yields) if len(unique_yields) > 1 else 0.0
            ) if unique_yields else None,
            "paired_bootstrap_unique_witness_yield_ratio_israc_over_baseline": paired_bootstrap_ratio(
                israc_records,
                seeds,
                samples=bootstrap_samples,
                seed=bootstrap_seed,
                metric="unique_witnesses",
            ),
            "paired_bootstrap_raw_pair_yield_ratio_israc_over_baseline": paired_bootstrap_ratio(
                israc_records,
                seeds,
                samples=bootstrap_samples,
                seed=bootstrap_seed,
                metric="raw_pairs",
            ),
        }
    israc_summary = summarize(israc_records)
    israc_unique_yield = (
        1000.0 * israc_summary["unique_witnesses"] / israc_summary["simulator_rollouts"]
        if israc_summary["simulator_rollouts"]
        else None
    )
    strongest_selector = (
        max(selector_point_yields, key=selector_point_yields.get)
        if selector_point_yields
        else None
    )
    strongest_yield = selector_point_yields.get(strongest_selector) if strongest_selector else None
    point_ratio = (
        israc_unique_yield / strongest_yield
        if israc_unique_yield is not None and strongest_yield not in (None, 0.0)
        else None
    )
    pilot_complete = (
        all_selectors_have_three_complete_seeds
        and israc_summary["boundary_count"] > 0
        and israc_summary["boundary_count"] == len(expected_boundaries)
    )
    pilot_pass = bool(pilot_complete and point_ratio is not None and point_ratio >= 2.0)
    return {
        "expected_boundaries": expected_boundaries,
        "israc": israc_summary,
        "baselines": baselines,
        "pilot_decision": {
            "complete": pilot_complete,
            "passed_simple_baseline_point_gate": pilot_pass,
            "strongest_simple_baseline": strongest_selector,
            "israc_unique_witness_yield_per_1k_rollouts": israc_unique_yield,
            "strongest_baseline_mean_unique_witness_yield_per_1k_rollouts": strongest_yield,
            "point_yield_ratio": point_ratio,
            "full_novelty_gate_passed": False,
            "full_gate_blockers": [
                "strong matched-call CMA-ES/BO baseline not yet run",
                "second physical mechanism family not yet demonstrated",
                "second simulator not yet demonstrated",
                "held-out feedback-WAM harm is untested",
            ],
        },
        "decision_rule": {
            "pilot_pass": "Every baseline selector has >=3 complete seeds; strongest matched-call baseline has point unique-witness yield ratio >=2; full novelty gate additionally requires CI lower bound >1, a stronger BO/CMA baseline, >=2 mechanisms, and a second simulator.",
            "incomplete_runs_are_not_zero": True,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--israc-glob", required=True)
    parser.add_argument("--baseline-glob", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=20_000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260831)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = analyze(
        load_records(args.israc_glob),
        load_records(args.baseline_glob),
        bootstrap_samples=args.bootstrap_samples,
        bootstrap_seed=args.bootstrap_seed,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
