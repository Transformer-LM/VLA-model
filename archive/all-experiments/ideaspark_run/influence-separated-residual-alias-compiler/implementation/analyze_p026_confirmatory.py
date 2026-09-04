#!/usr/bin/env python3
"""Strict confirmatory analysis for the frozen P026 compiler matrix."""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import os
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from analyze_p025_fixed_budget import validate_record
from verify_p025_manifest import verify_manifest_record


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    def reject(value: str) -> None:
        raise ValueError(f"non-finite JSON constant: {value}")

    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle, parse_constant=reject)
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def confined_file(value: Any, allowed_root: Path, label: str) -> Path:
    path = Path(str(value)).resolve()
    if path == allowed_root or allowed_root not in path.parents or not path.is_file():
        raise ValueError(f"invalid {label} path: {path}")
    return path


def verify_analysis_lock(
    lock_path: Path,
    lock_sha256: str,
    plan_path: Path,
    plan_sha256: str,
    allowed_root: Path,
) -> dict[str, Any]:
    if sha256_file(lock_path) != lock_sha256:
        raise ValueError("compiler lock hash mismatch")
    lock = read_json(lock_path)
    if lock.get("kind") != "p026_compiler_code_lock" or lock.get("frozen") is not True:
        raise ValueError("compiler lock is not frozen")
    locked_plan = lock.get("boundary_plan")
    if not isinstance(locked_plan, dict) or (
        Path(str(locked_plan.get("path"))).resolve() != plan_path
        or locked_plan.get("sha256") != plan_sha256
    ):
        raise ValueError("compiler lock is bound to another boundary plan")
    required_roles = {
        "compiler", "manifest_verifier", "p025_schema_validator", "p026_analyzer",
        "matrix_runner", "matrix_lock_builder", "launch_record_builder", "selector_support", "certificate_core", "repeat_envelope",
        "observation_support",
    }
    files = lock.get("files")
    if not isinstance(files, list) or len(files) != len(required_roles) or (
        {str(row.get("role")) for row in files} != required_roles
    ):
        raise ValueError("compiler lock role set is incomplete")
    for row in files:
        path = confined_file(row.get("path"), allowed_root, f"code role {row.get('role')}")
        if sha256_file(path) != str(row.get("sha256")):
            raise ValueError(f"locked code drift: {row.get('role')}")
    for label in ("preregistration", "policy_lock"):
        reference = lock.get(label)
        if not isinstance(reference, dict):
            raise ValueError(f"compiler lock lacks {label}")
        path = confined_file(reference.get("path"), allowed_root, label)
        if sha256_file(path) != str(reference.get("sha256")):
            raise ValueError(f"locked {label} changed")
    amendments = lock.get("protocol_amendments")
    if not isinstance(amendments, list) or [row.get("version") for row in amendments] != [
        "v1", "v2"
    ]:
        raise ValueError("compiler lock lacks the exact v1/v2 amendment chain")
    amendment_paths = []
    for reference in amendments:
        path = confined_file(
            reference.get("path"), allowed_root,
            f"protocol amendment {reference.get('version')}",
        )
        if sha256_file(path) != str(reference.get("sha256")):
            raise ValueError(
                f"locked protocol amendment {reference.get('version')} changed"
            )
        amendment_paths.append(path)
    if (
        [path.name for path in amendment_paths]
        != ["P026_PROTOCOL_AMENDMENT.md", "P026_PROTOCOL_AMENDMENT_V2.md"]
        or len(set(amendment_paths)) != 2
        or len({str(row.get("sha256")) for row in amendments}) != 2
        or amendments[1].get("predecessor_sha256") != amendments[0].get("sha256")
        or str(amendments[0].get("sha256"))
        not in amendment_paths[1].read_text(encoding="utf-8")
    ):
        raise ValueError("protocol amendment chain is aliased or not predecessor-pinned")
    return lock


def validate_plan_contract(plan: dict[str, Any]) -> None:
    if (
        plan.get("kind") != "p026_outcome_blind_boundary_plan"
        or plan.get("protocol_version") != "P026-v1"
        or plan.get("frozen_before_compiler_execution") is not True
    ):
        raise ValueError("plan is not a frozen P026 outcome-blind plan")
    if plan.get("selectors") != [
        "israc-contact-subtraction", "candidate-contact", "random-scene"
    ]:
        raise ValueError("plan selector contract changed")
    if plan.get("selector_seeds") != [0, 1, 2]:
        raise ValueError("plan selector seeds changed")
    scalar_contract = {
        "physical_family": "compliance",
        "candidate_chunks": 4,
        "max_selected_blocks": 3,
        "invalid_boundary_treatment": "zero_witness_full_cap_charge",
        "source_count": 7,
        "boundary_count": 21,
    }
    for key, expected in scalar_contract.items():
        if plan.get(key) != expected:
            raise ValueError(f"plan contract changed: {key}")
    sources = plan.get("sources")
    boundaries = plan.get("boundaries")
    if not isinstance(sources, list) or len(sources) != 7 or (
        not isinstance(boundaries, list) or len(boundaries) != 21
    ):
        raise ValueError("plan source/boundary cardinality changed")
    source_hashes = [str(row.get("source_rollout_sha256")) for row in sources]
    if len(source_hashes) != len(set(source_hashes)):
        raise ValueError("plan contains duplicate sources")
    for source in sources:
        selected = source.get("selected_candidate_indices")
        if not isinstance(selected, list) or len(selected) != 3 or len(set(selected)) != 3:
            raise ValueError("plan source does not freeze exactly three boundaries")
        source_rows = [
            row for row in boundaries
            if row.get("source_rollout_sha256") == source.get("source_rollout_sha256")
        ]
        if len(source_rows) != 3 or {
            int(row["candidate_index"]) for row in source_rows
        } != {int(value) for value in selected}:
            raise ValueError("plan source/boundary membership is inconsistent")


def evidence_semantic_sha256(reference: dict[str, Any]) -> str:
    """Hash NPZ semantics while ignoring only metadata_json/path bookkeeping."""

    digest = hashlib.sha256()
    path = Path(str(reference["path"])).resolve()
    with np.load(path, allow_pickle=False) as archive:
        for key in sorted(name for name in archive.files if name != "metadata_json"):
            array = np.ascontiguousarray(archive[key])
            digest.update(key.encode("utf-8"))
            digest.update(str(array.dtype).encode("ascii"))
            digest.update(str(tuple(array.shape)).encode("ascii"))
            digest.update(array.tobytes())
    return digest.hexdigest()


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = q * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def extended_empirical_quantile(values: list[float], q: float) -> float | str:
    """Nearest-rank percentile over finite values and positive infinity."""

    if not values:
        raise ValueError("extended percentile requires observations")
    ordered = sorted(values)
    index = max(0, math.ceil(q * len(ordered)) - 1)
    value = ordered[index]
    return "infinite" if math.isinf(value) else value


def successful_witness_keys(record: dict[str, Any]) -> set[str]:
    keys = [
        str(block["witness_key"])
        for block in record["blocks"]
        if int(block["unique_witness"]) == 1
    ]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate successful witness_key inside one matrix cell")
    if len(keys) != int(record["unique_witness_count"]):
        raise ValueError("successful witness_key set disagrees with cell aggregate")
    return set(keys)


def distinct_witness_count(records: list[dict[str, Any]]) -> int:
    return len(set().union(*(successful_witness_keys(record) for record in records)))


def assert_equal_fields(
    cells: list[dict[str, Any]], fields: tuple[str, ...], label: Any
) -> None:
    reference = cells[0]
    for cell in cells[1:]:
        for field in fields:
            if cell.get(field) != reference.get(field):
                raise ValueError(
                    f"cross-cell boundary invariant mismatch: {label}, field={field}"
                )


def validate_locked_path_set(
    paths: list[Path], expected_count: int, *, require_exists: bool = True
) -> None:
    if len(paths) != expected_count or len(paths) != len(set(paths)):
        raise ValueError("locked artifact path set is missing, duplicated, or extra")
    if require_exists and any(not path.is_file() for path in paths):
        raise ValueError("formal matrix artifact is missing")


def boundary_id(record: dict[str, Any]) -> tuple[str, int]:
    return str(record["rollout_sha256"]), int(record["candidate_chunk_index"])


def hierarchical_ratio_bootstrap(
    index: dict[str, dict[int, dict[tuple[str, int], dict[str, Any]]]],
    method: str,
    baseline: str,
    sources: dict[str, list[tuple[str, int]]],
    seeds: list[int],
    samples: int,
    rng_seed: int,
) -> dict[str, Any]:
    rng = random.Random(rng_seed)
    source_keys = sorted(sources)
    finite: list[float] = []
    infinite = 0
    zero_zero = 0
    for _ in range(samples):
        sampled_sources = [rng.choice(source_keys) for _ in source_keys]
        numerators: dict[str, int] = {method: 0, baseline: 0}
        denominators: dict[str, int] = {method: 0, baseline: 0}
        for source in sampled_sources:
            source_boundaries = sources[source]
            sampled_boundaries = [
                rng.choice(source_boundaries) for _ in source_boundaries
            ]
            for key in sampled_boundaries:
                sampled_seeds = [rng.choice(seeds) for _ in seeds]
                local_keys: dict[str, set[str]] = {method: set(), baseline: set()}
                for seed in sampled_seeds:
                    for selector in (method, baseline):
                        row = index[selector][seed][key]
                        local_keys[selector].update(successful_witness_keys(row))
                        denominators[selector] += int(row["charged_simulator_step_cap"])
                for selector in (method, baseline):
                    numerators[selector] += len(local_keys[selector])
        method_yield = numerators[method] / denominators[method]
        baseline_yield = numerators[baseline] / denominators[baseline]
        if method_yield == 0 and baseline_yield == 0:
            zero_zero += 1
            finite.append(1.0)
        elif baseline_yield == 0:
            infinite += 1
            finite.append(math.inf)
        else:
            finite.append(method_yield / baseline_yield)
    lower = extended_empirical_quantile(finite, 0.025)
    upper = extended_empirical_quantile(finite, 0.975)
    finite_only = [value for value in finite if math.isfinite(value)]
    return {
        "samples": samples,
        "finite_samples": len(finite_only),
        "infinite_samples": infinite,
        "undefined_zero_over_zero_samples": zero_zero,
        "zero_over_zero_convention": "ratio_equals_1",
        "positive_over_zero_convention": "positive_infinity",
        "median_finite_ratio": quantile(finite_only, 0.5),
        "ci95": [lower, upper],
        "ci_lower_gt_1": bool(lower == "infinite" or float(lower) > 1.0),
        "probability_ratio_gt_1": (
            sum(value > 1.0 for value in finite)
        ) / samples,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    parser.add_argument("--plan-sha256", required=True)
    parser.add_argument("--compiler-lock", required=True)
    parser.add_argument("--compiler-lock-sha256", required=True)
    parser.add_argument("--matrix-run-lock", required=True)
    parser.add_argument("--matrix-run-lock-sha256", required=True)
    parser.add_argument("--launch-record", required=True)
    parser.add_argument("--launch-record-sha256", required=True)
    parser.add_argument("--allowed-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=50_000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260901)
    args = parser.parse_args()
    if args.bootstrap_samples < 1000:
        raise ValueError("confirmatory bootstrap requires at least 1000 samples")

    allowed_root = Path(args.allowed_root).resolve()
    plan_path = Path(args.plan).resolve()
    if sha256_file(plan_path) != args.plan_sha256:
        raise ValueError("frozen plan hash mismatch")
    plan = read_json(plan_path)
    validate_plan_contract(plan)
    compiler_lock_path = Path(args.compiler_lock).resolve()
    verify_analysis_lock(
        compiler_lock_path,
        args.compiler_lock_sha256,
        plan_path,
        args.plan_sha256,
        allowed_root,
    )
    compiler_lock_reference = {
        "path": str(compiler_lock_path),
        "sha256": args.compiler_lock_sha256,
    }
    matrix_lock_path = Path(args.matrix_run_lock).resolve()
    if sha256_file(matrix_lock_path) != args.matrix_run_lock_sha256:
        raise ValueError("matrix-run lock hash mismatch")
    matrix_lock = read_json(matrix_lock_path)
    matrix_lock_reference = {
        "path": str(matrix_lock_path), "sha256": args.matrix_run_lock_sha256
    }
    if (
        matrix_lock.get("kind") != "p026_matrix_run_lock"
        or matrix_lock.get("frozen") is not True
        or matrix_lock.get("purpose") != "formal"
        or matrix_lock.get("compiler_lock") != compiler_lock_reference
        or matrix_lock.get("boundary_plan") != {
            "path": str(plan_path), "sha256": args.plan_sha256
        }
        or int(matrix_lock.get("job_count", -1)) != 189
    ):
        raise ValueError("formal matrix-run lock contract is invalid")
    launch_path = Path(args.launch_record).resolve()
    if sha256_file(launch_path) != args.launch_record_sha256:
        raise ValueError("formal launch record hash mismatch")
    launch_record = read_json(launch_path)
    launch_reference = {
        "path": str(launch_path), "sha256": args.launch_record_sha256
    }
    if (
        launch_record.get("kind") != "p026_immutable_launch_record"
        or launch_record.get("purpose") != "formal"
        or launch_record.get("boundary_plan") != matrix_lock.get("boundary_plan")
        or launch_record.get("compiler_lock") != compiler_lock_reference
        or launch_record.get("matrix_run_lock") != matrix_lock_reference
        or launch_record.get("output_directory_entries_at_launch") != []
        or launch_record.get("no_formal_cell_started_before_record") is not True
    ):
        raise ValueError("formal launch record chain is invalid")
    selectors = [str(value) for value in plan["selectors"]]
    seeds = [int(value) for value in plan["selector_seeds"]]
    planned = {
        (str(row["source_rollout_sha256"]), int(row["candidate_index"])): row
        for row in plan["boundaries"]
    }
    if len(planned) != int(plan["boundary_count"]):
        raise ValueError("frozen plan contains duplicate boundaries")

    locked_jobs = matrix_lock.get("jobs")
    if not isinstance(locked_jobs, list) or len(locked_jobs) != 189:
        raise ValueError("formal matrix-run lock lacks 189 jobs")
    paths = [Path(str(job["output"])).resolve() for job in locked_jobs]
    validate_locked_path_set(paths, 189)
    job_by_path = {
        Path(str(job["output"])).resolve(): job for job in locked_jobs
    }
    expected_count = len(planned) * len(selectors) * len(seeds)
    if len(paths) != expected_count:
        raise ValueError(f"matrix file count mismatch: {len(paths)} != {expected_count}")
    index: dict[str, dict[int, dict[tuple[str, int], dict[str, Any]]]] = {
        selector: {seed: {} for seed in seeds} for selector in selectors
    }
    for path in paths:
        record = read_json(path)
        validate_record(
            record,
            allowed_root,
            verify_evidence=True,
            expected_protocol="P026-v1",
        )
        verify_manifest_record(record, allowed_root)
        selector = str(record["block_selector"])
        seed = int(record["selector_seed"])
        key = boundary_id(record)
        locked_job = job_by_path[path]
        if (
            locked_job.get("selector") != selector
            or int(locked_job.get("selector_seed", -1)) != seed
            or str(locked_job.get("source_rollout_sha256")) != key[0]
            or int(locked_job.get("candidate_index", -1)) != key[1]
        ):
            raise ValueError("artifact content differs from its frozen matrix-run job")
        if selector not in index or seed not in index[selector] or key not in planned:
            raise ValueError(f"artifact escapes frozen matrix: {path}")
        if key in index[selector][seed]:
            raise ValueError(f"duplicate matrix cell: {selector}, {seed}, {key}")
        frozen = planned[key]
        expected_admission = {
            "path": str(Path(str(frozen["source_admission"])).resolve()),
            "sha256": str(frozen["source_admission_sha256"]),
        }
        actual_admission = dict(record["source_admission_report"])
        actual_admission["path"] = str(Path(str(actual_admission["path"])).resolve())
        if actual_admission != expected_admission:
            raise ValueError("artifact source admission differs from frozen plan")
        actual_compiler_lock = dict(record["compiler_lock"])
        actual_compiler_lock["path"] = str(
            Path(str(actual_compiler_lock["path"])).resolve()
        )
        if actual_compiler_lock != compiler_lock_reference:
            raise ValueError("artifact compiler lock differs from confirmatory analysis lock")
        actual_matrix_lock = dict(record["matrix_run_lock"])
        actual_matrix_lock["path"] = str(Path(str(actual_matrix_lock["path"])).resolve())
        if actual_matrix_lock != matrix_lock_reference or Path(
            str(record["artifact_output_path"])
        ).resolve() != path:
            raise ValueError("artifact path/lock differs from frozen matrix-run cell")
        if int(record["candidate_boundary_step"]) != int(
            frozen["candidate_boundary_step"]
        ):
            raise ValueError("artifact boundary step differs from frozen plan")
        if record["arguments"]["family"] != plan["physical_family"] or int(
            record["max_selected_blocks"]
        ) != int(plan["max_selected_blocks"]) or int(
            record["arguments"]["candidate_chunks"]
        ) != int(plan["candidate_chunks"]) or (
            record["arguments"]["block_selector"] != selector
        ) or int(record["arguments"]["selector_seed"]) != seed:
            raise ValueError("artifact compiler budget differs from frozen plan")
        index[selector][seed][key] = record

    expected_keys = set(planned)
    for selector in selectors:
        for seed in seeds:
            if set(index[selector][seed]) != expected_keys:
                raise ValueError(f"incomplete matrix cell coverage: {selector}, seed {seed}")
            seed_keys = [
                witness
                for key in expected_keys
                for witness in successful_witness_keys(index[selector][seed][key])
            ]
            if len(seed_keys) != len(set(seed_keys)):
                raise ValueError(f"duplicate witness_key across boundaries: {selector}, seed {seed}")

    invariant_fields = (
        "protocol_version", "rollout_sha256", "arrays_sha256", "environment_seed",
        "snapshot_sha256", "factual_action_sha256", "candidate_sha256",
        "factual_action_id", "candidate_action_id", "candidate_boundary_step",
        "candidate_chunk_index", "candidate_suffix_end_index", "factual_action_steps",
        "candidate_action_steps", "warmup_action_steps", "task_asset_bddl_sha256",
        "simulator_model_contact_schema_sha256", "static_physics_schema_version",
        "baseline_static_physics_sha256", "baseline_static_field_sha256",
        "engine_identity", "controller_reset_mode", "boundary_eligible",
        "invalid_boundary_reasons", "replay_endpoint_vs_saved_boundary_max_abs",
        "nominal_endpoint_repeat_max_abs", "replay_endpoint_tolerance",
        "endpoint_repeat_absolute_cap", "saved_endpoint_absolute_cap",
        "charged_simulator_step_cap", "charged_continuous_execution_cap",
        "max_selected_blocks", "dynamic_state_schema", "source_admission_report",
        "compiler_lock",
        "matrix_run_lock",
    )
    for key in expected_keys:
        cells = [index[selector][seed][key] for selector in selectors for seed in seeds]
        assert_equal_fields(cells, invariant_fields, key)
        nominal_hashes = {
            evidence_semantic_sha256(cell["nominal_unedited_evidence"])
            for cell in cells
        }
        repeat_hashes = {
            evidence_semantic_sha256(cell["nominal_unedited_repeat_evidence"])
            for cell in cells
        }
        if len(nominal_hashes) != 1 or len(repeat_hashes) != 1:
            raise ValueError(f"cross-cell raw nominal replay mismatch: {key}")

    summaries: dict[str, Any] = {}
    for selector in selectors:
        rows = [
            index[selector][seed][key]
            for seed in seeds for key in sorted(expected_keys)
        ]
        successful_trials = sum(int(row["unique_witness_count"]) for row in rows)
        unique = distinct_witness_count(rows)
        charged = sum(int(row["charged_simulator_step_cap"]) for row in rows)
        summaries[selector] = {
            "artifact_count": len(rows),
            "eligible_boundary_count": sum(bool(row["boundary_eligible"]) for row in rows),
            "invalid_boundary_count": sum(not bool(row["boundary_eligible"]) for row in rows),
            "unique_witness_count": unique,
            "successful_block_trial_count_before_cross_seed_dedup": successful_trials,
            "raw_endpoint_pair_count": sum(int(row["raw_endpoint_pair_count"]) for row in rows),
            "charged_simulator_steps": charged,
            "actual_simulator_steps": sum(int(row["actual_simulator_steps"]) for row in rows),
            "unique_witness_yield_per_1m_charged_steps": 1_000_000 * unique / charged,
            "per_seed": {
                str(seed): {
                    "unique_witness_count": distinct_witness_count([
                        index[selector][seed][key] for key in expected_keys
                    ]),
                    "charged_simulator_steps": sum(
                        int(index[selector][seed][key]["charged_simulator_step_cap"])
                        for key in expected_keys
                    ),
                }
                for seed in seeds
            },
        }

    method = "israc-contact-subtraction"
    baselines = [selector for selector in selectors if selector != method]
    method_yield = summaries[method]["unique_witness_yield_per_1m_charged_steps"]
    strongest = max(
        baselines,
        key=lambda selector: summaries[selector]["unique_witness_yield_per_1m_charged_steps"],
    )
    point_ratios = {
        baseline: (
            method_yield / summaries[baseline]["unique_witness_yield_per_1m_charged_steps"]
            if summaries[baseline]["unique_witness_yield_per_1m_charged_steps"] > 0
            else ("infinite" if method_yield > 0 else 1.0)
        )
        for baseline in baselines
    }
    source_groups: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for key in sorted(expected_keys):
        source_groups[key[0]].append(key)
    bootstrap = {
        baseline: hierarchical_ratio_bootstrap(
            index,
            method,
            baseline,
            dict(source_groups),
            seeds,
            args.bootstrap_samples,
            args.bootstrap_seed + offset,
        )
        for offset, baseline in enumerate(baselines)
    }
    strongest_ratio = point_ratios[strongest]
    point_gate = strongest_ratio == "infinite" or (
        isinstance(strongest_ratio, float) and strongest_ratio >= 2.0
    )
    uncertainty_gate = all(value["ci_lower_gt_1"] for value in bootstrap.values())
    passed = bool(point_gate and uncertainty_gate)
    payload = {
        "kind": "p026_confirmatory_simple_baseline_analysis",
        "protocol_version": "P026-v1",
        "plan": {"path": str(plan_path), "sha256": args.plan_sha256},
        "compiler_lock": compiler_lock_reference,
        "matrix_run_lock": matrix_lock_reference,
        "launch_record": launch_reference,
        "artifact_sha256": {
            str(path): sha256_file(path) for path in paths
        },
        "matrix_complete": True,
        "semantic_evidence_reverified": True,
        "cross_cell_nominal_semantics_equal": True,
        "primary_estimand": (
            "distinct successful witness_key union across the three selector seeds per selector, "
            "divided by all charged simulator steps; repeated discovery is not recounted"
        ),
        "confirmatory_label": "amended_confirmatory_with_disclosed_three_cell_pre_formal_contamination",
        "source_count": int(plan["source_count"]),
        "boundary_count": int(plan["boundary_count"]),
        "selector_seed_count": len(seeds),
        "summaries": summaries,
        "point_yield_ratios": point_ratios,
        "strongest_simple_baseline": strongest,
        "bootstrap": bootstrap,
        "decision": {
            "point_ratio_at_least_2x_strongest": point_gate,
            "all_paired_hierarchical_ci95_lower_above_1": uncertainty_gate,
            "simple_baseline_gate_passed": passed,
            "next_step": (
                "authorize strong optimizer, second physical mechanism, and WAM harm gates"
                if passed else "redesign or kill ISRAC; do not cherry-pick replacement boundaries"
            ),
        },
        "claim_limit": (
            "Amended held-out matched-budget compiler comparison: two ISRAC debug cells and one "
            "candidate-contact lock-sanity cell were generated pre-formal, disclosed, preserved, "
            "and rerun without "
            "changing the frozen 21-boundary matrix or decision rules. This is not a pristine "
            "outcome-locked experiment. No WAM harm, strong optimizer, second physical mechanism, "
            "or second simulator claim is established here."
        ),
    }
    output = Path(args.output).resolve()
    if output.exists():
        raise ValueError(f"refusing to overwrite confirmatory analysis: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + f".tmp.{os.getpid()}")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, output)
    print(json.dumps(payload["decision"], sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
