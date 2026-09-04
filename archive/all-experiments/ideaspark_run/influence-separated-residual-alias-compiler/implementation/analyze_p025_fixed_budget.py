#!/usr/bin/env python3
"""Strict fixed-step analysis for P025 continuous contact-support artifacts."""

from __future__ import annotations

import argparse
import collections
import glob
import hashlib
import json
import math
import os
from pathlib import Path
import random
import statistics
from typing import Any, Iterable


REQUIRED_SELECTORS = {
    "israc-contact-subtraction",
    "candidate-contact",
    "random-scene",
}
PROTOCOL_NOMINAL_EXECUTIONS = 2
PROTOCOL_EXECUTIONS_PER_BLOCK = 4
REGISTERED_ENDPOINTS = {
    "compliance": [0.004, 0.020, 0.100],
    "friction": [0.05, 0.30, 1.50],
}
REQUIRED_CONTROLLER_RESET_MODE = (
    "fresh_seeded_reset_set_benchmark_init_then_replay_warmup_full_prefix_candidate"
)


def reject_constant(value: str) -> None:
    raise ValueError(f"non-standard/non-finite JSON constant: {value}")


def read_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        value = json.load(handle, parse_constant=reject_constant)
    if not isinstance(value, dict):
        raise ValueError(f"top-level JSON must be an object: {path}")
    assert_finite(value)
    return value


def assert_finite(value: Any, location: str = "$.") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"non-finite number at {location}")
    if isinstance(value, dict):
        for key, item in value.items():
            assert_finite(item, f"{location}{key}.")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            assert_finite(item, f"{location}[{index}].")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def boundary_key(record: dict[str, Any]) -> str:
    return "::".join(
        (
            str(record["rollout_sha256"]),
            str(record["arrays_sha256"]),
            str(record["candidate_boundary_step"]),
            str(record["candidate_sha256"]),
        )
    )


def validate_evidence_reference(reference: dict[str, Any], allowed_root: Path) -> None:
    path = Path(str(reference["path"])).resolve()
    if path == allowed_root or allowed_root not in path.parents:
        raise ValueError(f"evidence outside allowed root: {path}")
    if not path.is_file():
        raise ValueError(f"missing evidence: {path}")
    actual = sha256_file(path)
    if actual != str(reference["sha256"]):
        raise ValueError(f"evidence hash mismatch: {path}")


def canonical_payload_sha256(payload: dict[str, Any]) -> str:
    serialized = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def validate_certificate_pair(
    pair: dict[str, Any],
    block: dict[str, Any],
    record: dict[str, Any],
) -> None:
    payload = pair.get("certificate_payload")
    if not isinstance(payload, dict):
        raise ValueError("accepted endpoint pair lacks certificate payload")
    if canonical_payload_sha256(payload) != str(pair["certificate_sha256"]):
        raise ValueError("certificate payload hash mismatch")
    if payload.get("failures") != []:
        raise ValueError("accepted endpoint pair has certificate failures")
    if payload.get("measurements") != pair.get("measurements"):
        raise ValueError("pair measurements differ from certificate payload")
    certificate = payload.get("certificate")
    if not isinstance(certificate, dict):
        raise ValueError("certificate section missing")
    expected_evidence = [
        str(pair["left_evidence"]["sha256"]),
        str(pair["right_evidence"]["sha256"]),
        str(block["repeat_evidence"]["sha256"]),
    ]
    if record.get("protocol_version") == "P026-v1":
        expected_evidence.extend([
            str(record["nominal_unedited_evidence"]["sha256"]),
            str(record["nominal_unedited_repeat_evidence"]["sha256"]),
        ])
    if certificate.get("evidence_sha256") != expected_evidence:
        raise ValueError("certificate is not bound to pair evidence")
    expected_static = [
        str(pair["left_static_contact_config_sha256"]),
        str(pair["right_static_contact_config_sha256"]),
    ]
    if certificate.get("static_config_sha256") != expected_static:
        raise ValueError("certificate is not bound to static configurations")
    bindings = {
        "snapshot_id": record["snapshot_sha256"],
        "factual_action_sha256": record["factual_action_sha256"],
        "candidate_action_sha256": record["candidate_sha256"],
        "simulator_model_sha256": record["simulator_model_contact_schema_sha256"],
        "task_asset_sha256": record["task_asset_bddl_sha256"],
        "engine_identity": record["engine_identity"],
    }
    for key, expected in bindings.items():
        if certificate.get(key) != expected:
            raise ValueError(f"certificate binding mismatch: {key}")
    metadata = block.get("parameter_metadata")
    if not isinstance(metadata, dict):
        raise ValueError("parameter metadata missing")
    if certificate.get("parameter_addresses") != [str(metadata["engine_field"])]:
        raise ValueError("certificate parameter address mismatch")
    objective = {str(term).casefold() for term in certificate.get("search_objective_terms", [])}
    if objective.intersection({"wam_score", "wam_ranking", "target_wam", "residual_sign"}):
        raise ValueError("target WAM leaked into certificate objective")


def validate_record(
    record: dict[str, Any],
    allowed_root: Path,
    *,
    verify_evidence: bool,
    expected_protocol: str = "P025-v5",
) -> None:
    if record.get("kind") != "israc_continuous_geom_contact_support_e0":
        raise ValueError("unexpected artifact kind")
    if expected_protocol not in {"P025-v5", "P026-v1"} or (
        record.get("protocol_version") != expected_protocol
    ):
        raise ValueError(f"unexpected protocol version: {record.get('protocol_version')}")
    if record.get("controller_reset_mode") != REQUIRED_CONTROLLER_RESET_MODE:
        raise ValueError("unexpected or unverifiable controller reset mode")
    selector = str(record.get("block_selector"))
    if selector not in REQUIRED_SELECTORS:
        raise ValueError(f"unexpected selector: {selector}")
    blocks = record.get("blocks")
    if not isinstance(blocks, list):
        raise ValueError("blocks must be a list")
    if int(record["selected_block_count"]) != len(blocks):
        raise ValueError("selected_block_count does not match block detail")
    if not isinstance(record.get("baseline_static_evidence"), dict):
        raise ValueError("baseline static evidence is missing")
    if verify_evidence:
        validate_evidence_reference(record["baseline_static_evidence"], allowed_root)
    if expected_protocol == "P026-v1":
        for key in (
            "source_admission_report",
            "compiler_lock",
            "matrix_run_lock",
            "nominal_unedited_evidence",
            "nominal_unedited_repeat_evidence",
        ):
            if not isinstance(record.get(key), dict):
                raise ValueError(f"P026 required evidence reference is missing: {key}")
            if verify_evidence:
                validate_evidence_reference(record[key], allowed_root)
        if not isinstance(record.get("contact_topology"), list) or not record[
            "contact_topology"
        ]:
            raise ValueError("P026 authenticated contact topology is missing")

    raw_pairs = 0
    unique = 0
    witness_keys: set[str] = set()
    for block in blocks:
        pairs = int(block["certified_endpoint_pairs"])
        strength = block["endpoint_strength_curve"]
        if pairs != len(strength):
            raise ValueError("endpoint pair count does not match strength curve")
        is_unique = int(block["unique_witness"])
        if is_unique not in (0, 1) or is_unique != int(pairs > 0):
            raise ValueError("unique_witness must be exactly the passing-block indicator")
        raw_pairs += pairs
        unique += is_unique
        witness_key = str(block["witness_key"])
        expected_witness_fields = {
            "source_trajectory_sha256": record["rollout_sha256"],
            "arrays_sha256": record["arrays_sha256"],
            "snapshot_sha256": record["snapshot_sha256"],
            "factual_action_sha256": record["factual_action_sha256"],
            "boundary_step": int(record["candidate_boundary_step"]),
            "candidate_sha256": record["candidate_sha256"],
            "geom_ids": [int(value) for value in block["geom_ids"]],
            "parameter_family": str(record["arguments"]["family"]),
        }
        if block.get("witness_key_fields") != expected_witness_fields:
            raise ValueError("witness_key_fields differ from authenticated manifest fields")
        recomputed_witness_key = hashlib.sha256(
            json.dumps(
                expected_witness_fields, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
        if witness_key != recomputed_witness_key:
            raise ValueError("witness_key is not the canonical hash of its fields")
        if witness_key in witness_keys:
            raise ValueError("duplicate witness key inside artifact")
        witness_keys.add(witness_key)
        endpoint_evidence = block.get("endpoint_evidence")
        if not isinstance(endpoint_evidence, dict) or not endpoint_evidence:
            raise ValueError("block lacks complete endpoint evidence map")
        legal_endpoints = block.get("static_diff_schema", {}).get("legal_endpoints")
        family = str(record.get("arguments", {}).get("family"))
        if family not in REGISTERED_ENDPOINTS or legal_endpoints != REGISTERED_ENDPOINTS[family]:
            raise ValueError("endpoint sweep differs from registered family protocol")
        if not isinstance(legal_endpoints, list) or {
            str(value) for value in legal_endpoints
        } != set(endpoint_evidence):
            raise ValueError("endpoint evidence map does not cover exact legal sweep")
        expected_attempts = len(legal_endpoints) * (len(legal_endpoints) - 1) // 2
        if int(block.get("attempted_endpoint_pairs", -1)) != expected_attempts:
            raise ValueError("endpoint sweep is not the complete pairwise protocol")
        endpoint_order = {float(value): index for index, value in enumerate(legal_endpoints)}
        seen_pairs: set[tuple[float, float]] = set()
        endpoint_hashes = {
            str(reference["sha256"]) for reference in endpoint_evidence.values()
        }
        if len(endpoint_hashes) != len(endpoint_evidence):
            raise ValueError("endpoint evidence hashes are not one-to-one")
        for pair in strength:
            pair_key = (float(pair["left_value"]), float(pair["right_value"]))
            if (
                pair_key in seen_pairs
                or pair_key[0] not in endpoint_order
                or pair_key[1] not in endpoint_order
                or endpoint_order[pair_key[0]] >= endpoint_order[pair_key[1]]
            ):
                raise ValueError("invalid or duplicate passing endpoint pair")
            seen_pairs.add(pair_key)
            left_key = str(pair["left_value"])
            right_key = str(pair["right_value"])
            if pair["left_evidence"] != endpoint_evidence.get(left_key):
                raise ValueError("left evidence is not the declared endpoint evidence")
            if pair["right_evidence"] != endpoint_evidence.get(right_key):
                raise ValueError("right evidence is not the declared endpoint evidence")
            validate_certificate_pair(pair, block, record)
        if verify_evidence:
            validate_evidence_reference(block["repeat_evidence"], allowed_root)
            for reference in endpoint_evidence.values():
                validate_evidence_reference(reference, allowed_root)
    if raw_pairs != int(record["raw_endpoint_pair_count"]):
        raise ValueError("raw endpoint pair aggregate mismatch")
    if unique != int(record["unique_witness_count"]):
        raise ValueError("unique witness aggregate mismatch")

    selected = len(blocks)
    if int(record["nominal_continuous_executions"]) != PROTOCOL_NOMINAL_EXECUTIONS:
        raise ValueError("nominal execution constant differs from registered protocol")
    if int(record["continuous_executions_per_selected_block"]) != PROTOCOL_EXECUTIONS_PER_BLOCK:
        raise ValueError("block execution constant differs from registered protocol")
    expected_actual_executions = PROTOCOL_NOMINAL_EXECUTIONS + (
        PROTOCOL_EXECUTIONS_PER_BLOCK * selected
    )
    if expected_actual_executions != int(record["actual_continuous_executions"]):
        raise ValueError("actual continuous execution count mismatch")
    segment_steps = int(record["factual_action_steps"]) + int(record["candidate_action_steps"])
    if segment_steps <= 0:
        raise ValueError("invalid action step count")
    expected_actual_steps = expected_actual_executions * segment_steps
    if int(record["actual_simulator_steps"]) != expected_actual_steps:
        raise ValueError("measured simulator-step count differs from evidence schedule")
    if int(record["expected_actual_simulator_steps"]) != expected_actual_steps:
        raise ValueError("declared expected simulator-step count mismatch")
    eligible = bool(record["boundary_eligible"])
    if eligible:
        charged = int(record["charged_simulator_step_cap"])
        actual = int(record["actual_simulator_steps"])
        unused = int(record["unused_simulator_step_budget"])
        if actual > charged or unused != charged - actual:
            raise ValueError("fixed step accounting mismatch")
        if charged <= 0:
            raise ValueError("eligible boundary has no charged budget")
        expected_charged = (
            PROTOCOL_NOMINAL_EXECUTIONS
            + PROTOCOL_EXECUTIONS_PER_BLOCK * int(record["max_selected_blocks"])
        ) * segment_steps
        if charged != expected_charged:
            raise ValueError("charged cap differs from preregistered fixed budget")
    else:
        if selected or unique or raw_pairs:
            raise ValueError("invalid boundary entered the compiler witness set")
        if not record.get("invalid_boundary_reasons"):
            raise ValueError("invalid boundary has no reason")
        if expected_protocol == "P025-v5":
            if int(record["charged_simulator_step_cap"]) != 0:
                raise ValueError("P025 invalid boundary entered budget denominator")
        else:
            expected_charged = (
                PROTOCOL_NOMINAL_EXECUTIONS
                + PROTOCOL_EXECUTIONS_PER_BLOCK * int(record["max_selected_blocks"])
            ) * segment_steps
            charged = int(record["charged_simulator_step_cap"])
            unused = int(record["unused_simulator_step_budget"])
            actual = int(record["actual_simulator_steps"])
            if charged != expected_charged or unused != charged - actual:
                raise ValueError("P026 invalid boundary was not charged as zero-yield")


def load_records(pattern: str, allowed_root: Path, *, verify_evidence: bool) -> list[dict[str, Any]]:
    paths = sorted(glob.glob(pattern))
    if not paths:
        raise ValueError(f"input glob matched no files: {pattern}")
    records: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str]] = set()
    for path in paths:
        record = read_json(path)
        validate_record(record, allowed_root, verify_evidence=verify_evidence)
        if verify_evidence:
            from verify_p025_manifest import verify_manifest_record

            verify_manifest_record(record, allowed_root)
        key = (
            str(record["block_selector"]),
            int(record["selector_seed"]),
            boundary_key(record),
        )
        if key in seen:
            raise ValueError(f"duplicate selector/seed/boundary: {key}")
        seen.add(key)
        record["_path"] = path
        records.append(record)
    return records


def index_records(
    records: Iterable[dict[str, Any]],
) -> dict[str, dict[int, dict[str, dict[str, Any]]]]:
    result: dict[str, dict[int, dict[str, dict[str, Any]]]] = collections.defaultdict(
        lambda: collections.defaultdict(dict)
    )
    for record in records:
        result[str(record["block_selector"])][int(record["selector_seed"])][
            boundary_key(record)
        ] = record
    return {selector: dict(seeds) for selector, seeds in result.items()}


def summarize_seed(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(records)
    eligible = [row for row in rows if row["boundary_eligible"]]
    unique = sum(int(row["unique_witness_count"]) for row in eligible)
    raw = sum(int(row["raw_endpoint_pair_count"]) for row in eligible)
    charged = sum(int(row["charged_simulator_step_cap"]) for row in eligible)
    actual = sum(int(row["actual_simulator_steps"]) for row in rows)
    return {
        "boundary_count": len(rows),
        "eligible_boundary_count": len(eligible),
        "invalid_boundary_count": len(rows) - len(eligible),
        "unique_witnesses": unique,
        "raw_endpoint_pairs": raw,
        "charged_simulator_steps": charged,
        "actual_simulator_steps": actual,
        "unique_witness_yield_per_1m_charged_steps": (
            1_000_000.0 * unique / charged if charged else None
        ),
    }


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = q * (len(ordered) - 1)
    lo, hi = math.floor(position), math.ceil(position)
    if lo == hi:
        return ordered[lo]
    weight = position - lo
    return ordered[lo] * (1.0 - weight) + ordered[hi] * weight


def cluster_bootstrap_ratio(
    method: dict[int, dict[str, dict[str, Any]]],
    baseline: dict[int, dict[str, dict[str, Any]]],
    seeds: list[int],
    eligible_boundaries: list[str],
    *,
    samples: int,
    rng_seed: int,
) -> dict[str, Any]:
    if samples <= 0:
        raise ValueError("bootstrap_samples must be positive")
    rng = random.Random(rng_seed)
    finite: list[float] = []
    infinite = undefined = 0
    for _ in range(samples):
        seed = rng.choice(seeds)
        sampled = [rng.choice(eligible_boundaries) for _ in eligible_boundaries]
        method_unique = sum(int(method[seed][key]["unique_witness_count"]) for key in sampled)
        baseline_unique = sum(int(baseline[seed][key]["unique_witness_count"]) for key in sampled)
        method_steps = sum(int(method[seed][key]["charged_simulator_step_cap"]) for key in sampled)
        baseline_steps = sum(int(baseline[seed][key]["charged_simulator_step_cap"]) for key in sampled)
        method_yield = method_unique / method_steps if method_steps else 0.0
        baseline_yield = baseline_unique / baseline_steps if baseline_steps else 0.0
        if method_yield == 0.0 and baseline_yield == 0.0:
            undefined += 1
        elif baseline_yield == 0.0:
            infinite += 1
        else:
            finite.append(method_yield / baseline_yield)
    lower = quantile(finite, 0.025)
    upper: float | str | None
    if infinite / samples >= 0.025:
        upper = "infinite"
    else:
        upper = quantile(finite, 0.975)
    return {
        "samples": samples,
        "finite_samples": len(finite),
        "infinite_samples": infinite,
        "undefined_zero_over_zero_samples": undefined,
        "median_finite_ratio": quantile(finite, 0.5),
        "ci95": [lower, upper],
        "probability_ratio_gt_1_among_all_samples": (
            sum(value > 1.0 for value in finite) + infinite
        ) / samples,
        "ci_lower_gt_1": bool(lower is not None and lower > 1.0),
    }


def analyze(
    records: list[dict[str, Any]],
    expected_seeds: list[int],
    *,
    bootstrap_samples: int,
    bootstrap_seed: int,
    evidence_semantically_reverified: bool = False,
) -> dict[str, Any]:
    grouped = index_records(records)
    missing_selectors = sorted(REQUIRED_SELECTORS - set(grouped))
    if missing_selectors:
        raise ValueError(f"missing required selectors: {missing_selectors}")
    reference = grouped["israc-contact-subtraction"]
    for selector in sorted(REQUIRED_SELECTORS):
        if sorted(grouped[selector]) != sorted(expected_seeds):
            raise ValueError(f"selector {selector} does not have exact expected seeds")
    reference_keys = set(reference[expected_seeds[0]])
    if not reference_keys:
        raise ValueError("no boundaries")
    for selector in sorted(REQUIRED_SELECTORS):
        for seed in expected_seeds:
            if set(grouped[selector][seed]) != reference_keys:
                raise ValueError(f"boundary coverage mismatch: {selector} seed {seed}")

    for key in reference_keys:
        eligibility = {
            bool(grouped[selector][seed][key]["boundary_eligible"])
            for selector in REQUIRED_SELECTORS
            for seed in expected_seeds
        }
        if len(eligibility) != 1:
            raise ValueError(f"boundary eligibility changed across selector/seed: {key}")
        charged_caps = {
            int(grouped[selector][seed][key]["charged_simulator_step_cap"])
            for selector in REQUIRED_SELECTORS
            for seed in expected_seeds
        }
        if len(charged_caps) != 1:
            raise ValueError(f"charged step cap changed across selector/seed: {key}")
    for selector in sorted(REQUIRED_SELECTORS):
        for seed in expected_seeds:
            witness_keys: set[str] = set()
            for record in grouped[selector][seed].values():
                for block in record["blocks"]:
                    key = str(block["witness_key"])
                    if key in witness_keys:
                        raise ValueError(
                            f"duplicate witness across boundaries: {selector} seed {seed}"
                        )
                    witness_keys.add(key)
    eligible_keys = sorted(
        key for key in reference_keys if reference[expected_seeds[0]][key]["boundary_eligible"]
    )
    if not eligible_keys:
        raise ValueError("no eligible boundaries after endpoint fidelity gate")

    summaries: dict[str, Any] = {}
    mean_yields: dict[str, float] = {}
    for selector in sorted(REQUIRED_SELECTORS):
        seed_rows: dict[str, Any] = {}
        yields: list[float] = []
        for seed in expected_seeds:
            summary = summarize_seed(grouped[selector][seed].values())
            seed_rows[str(seed)] = summary
            value = summary["unique_witness_yield_per_1m_charged_steps"]
            if value is not None:
                yields.append(float(value))
        mean_yields[selector] = statistics.mean(yields)
        summaries[selector] = {
            "seeds": seed_rows,
            "mean_unique_witness_yield_per_1m_charged_steps": statistics.mean(yields),
            "std_unique_witness_yield_per_1m_charged_steps": (
                statistics.stdev(yields) if len(yields) > 1 else 0.0
            ),
        }

    method_yield = mean_yields["israc-contact-subtraction"]
    baseline_names = sorted(REQUIRED_SELECTORS - {"israc-contact-subtraction"})
    strongest = max(baseline_names, key=lambda name: mean_yields[name])
    strongest_yield = mean_yields[strongest]
    if method_yield == 0.0 and strongest_yield == 0.0:
        point_ratio: float | str | None = None
    elif strongest_yield == 0.0:
        point_ratio = "infinite"
    else:
        point_ratio = method_yield / strongest_yield

    comparisons = {}
    for name in baseline_names:
        comparisons[name] = cluster_bootstrap_ratio(
            grouped["israc-contact-subtraction"],
            grouped[name],
            expected_seeds,
            eligible_keys,
            samples=bootstrap_samples,
            rng_seed=bootstrap_seed,
        )
    strongest_ci_pass = comparisons[strongest]["ci_lower_gt_1"]
    point_gate = point_ratio == "infinite" or (
        isinstance(point_ratio, float) and point_ratio >= 2.0
    )
    return {
        "protocol": "P025-v5",
        "evidence_semantically_reverified": evidence_semantically_reverified,
        "selectors": summaries,
        "eligible_boundary_count": len(eligible_keys),
        "ineligible_boundary_count": len(reference_keys) - len(eligible_keys),
        "comparisons": comparisons,
        "pilot_decision": {
            "strongest_simple_baseline": strongest,
            "method_mean_yield": method_yield,
            "strongest_baseline_mean_yield": strongest_yield,
            "point_yield_ratio": point_ratio,
            "point_ratio_ge_2": point_gate,
            "strongest_baseline_ci_lower_gt_1": strongest_ci_pass,
            "simple_baseline_gate_passed": bool(
                evidence_semantically_reverified and point_gate and strongest_ci_pass
            ),
            "full_novelty_gate_passed": False,
            "scope": "protocol pilot; strong optimizer, second mechanism, second simulator, and WAM audit remain absent",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-glob", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--allowed-root", required=True)
    parser.add_argument("--expected-seeds", default="0,1,2")
    parser.add_argument("--bootstrap-samples", type=int, default=20_000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260901)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    allowed_root = Path(args.allowed_root).resolve()
    configured_root = Path("<PERSONAL_RESEARCH_ROOT>").resolve()
    if allowed_root != configured_root or not allowed_root.is_dir():
        raise ValueError("allowed root must be the configured personal data root")
    output = Path(args.output).resolve()
    if output == allowed_root or allowed_root not in output.parents or output.exists():
        raise ValueError("unsafe or existing output path")
    seeds = [int(value) for value in args.expected_seeds.split(",") if value]
    if not seeds or len(seeds) != len(set(seeds)):
        raise ValueError("expected seeds must be a non-empty unique list")
    result = analyze(
        load_records(
            args.input_glob,
            allowed_root,
            verify_evidence=True,
        ),
        seeds,
        bootstrap_samples=args.bootstrap_samples,
        bootstrap_seed=args.bootstrap_seed,
        evidence_semantically_reverified=True,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + f".tmp.{os.getpid()}")
    temporary.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, output)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
