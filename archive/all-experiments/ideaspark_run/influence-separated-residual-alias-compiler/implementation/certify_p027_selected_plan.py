#!/usr/bin/env python3
"""Strictly certify one P027 CEM-selected continuous parameter pair.

The search plan selects at most one physical parameter block and two continuous
values. This adapter binds the plan to the admitted P026 source, independently
reconstructs the selection, and invokes the frozen raw-unedited P026 protocol
with those endpoints plus their deterministic geometric midpoint. The midpoint
preserves the frozen P026 three-endpoint accounting; the adapter separately
checks that the originally selected endpoint pair itself passed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np

import certify_continuous_contact_support as base
from search_p027_blackbox_cem import choose_distinct_blocks


SELECTOR_MAPPING = {
    "candidate-contact-cem": "candidate-contact",
    "scene-cem": "random-scene",
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json_once(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8")), sha256_bytes(raw)


def locked_reference(lock: dict[str, Any], role: str) -> dict[str, str]:
    matches = [row for row in lock.get("files", []) if row.get("role") == role]
    if len(matches) != 1:
        raise ValueError(f"compiler lock must contain one {role!r} reference")
    return {"path": str(matches[0]["path"]), "sha256": str(matches[0]["sha256"])}


def reconstruct_selected(plan: dict[str, Any]) -> list[dict[str, Any]]:
    evaluations = plan.get("evaluations")
    if not isinstance(evaluations, list):
        raise ValueError("plan evaluations must be a list")
    for index, row in enumerate(evaluations):
        if not isinstance(row, dict) or int(row.get("evaluation_index", -1)) != index:
            raise ValueError("evaluation indices are not canonical")
        pair = row.get("parameter_values")
        if (
            not isinstance(pair, list)
            or len(pair) != 2
            or not all(np.isfinite(float(value)) for value in pair)
            or not float(pair[0]) < float(pair[1])
        ):
            raise ValueError("evaluation parameter pair is invalid")
    rebuilt = choose_distinct_blocks(evaluations, 1)
    return [
        {
            "parameter_address": row["parameter_address"],
            "geom_ids": row["geom_ids"],
            "parameter_values": row["parameter_values"],
            "search_score": row["score"],
            "source_evaluation_index": row["evaluation_index"],
        }
        for row in rebuilt
    ]


def certification_grid(
    selected: list[dict[str, Any]], parameter_values: tuple[float, ...]
) -> tuple[float, ...]:
    """Preserve the frozen three-endpoint/four-execution P026 accounting."""

    if not selected:
        return parameter_values
    left, right = parameter_values
    return (left, math.sqrt(left * right), right)


def invoke_base_main(entrypoint: Any) -> None:
    """Treat the frozen base's SystemExit(0) as normal completion."""

    try:
        entrypoint()
    except SystemExit as exc:
        if int(exc.code or 0) != 0:
            raise


def validate_plan(
    plan: dict[str, Any],
    *,
    plan_path: Path,
    plan_sha256: str,
    rollout_path: Path,
    admission_path: Path,
    compiler_lock_path: Path,
    matrix_lock_path: Path,
    support_path: Path,
    output_path: Path,
) -> tuple[list[dict[str, Any]], tuple[float, ...]]:
    selector = str(plan.get("selector"))
    if (
        plan.get("kind") != "p027_blackbox_mixed_cem_selection_plan"
        or plan.get("protocol_version") != "P027-search-sanity-v1"
        or plan.get("compiler_target_wam_blind") is not True
        or plan.get("target_wam_used_in_search") is not False
        or selector not in SELECTOR_MAPPING
        or plan.get("certifier_selector") != SELECTOR_MAPPING[selector]
        or int(plan.get("arguments", {}).get("max_selected_blocks", -1)) != 1
    ):
        raise ValueError("invalid P027 CEM selection plan header")

    compiler_lock, _ = load_json_once(compiler_lock_path)
    if compiler_lock.get("kind") != "p026_compiler_code_lock" or compiler_lock.get(
        "frozen"
    ) is not True:
        raise ValueError("compiler lock is not frozen")
    plan_reference = locked_reference(compiler_lock, "p027_selection_plan")
    if (
        str(Path(plan_reference["path"]).resolve()) != str(plan_path)
        or plan_reference["sha256"] != plan_sha256
    ):
        raise ValueError("compiler lock is not bound to the exact selection-plan bytes")
    support_reference = locked_reference(compiler_lock, "observation_support")
    support_entrypoint = support_path / "collect_e1_paired_rollouts.py"
    if support_reference != {
        "path": str(support_entrypoint),
        "sha256": sha256_file(support_entrypoint),
    }:
        raise ValueError("certification support code differs from the compiler lock")

    matrix_lock, _ = load_json_once(matrix_lock_path)
    matching_jobs = [
        row
        for row in matrix_lock.get("jobs", [])
        if str(Path(str(row.get("output"))).resolve()) == str(output_path)
        and str(row.get("selector")) == str(plan["certifier_selector"])
        and int(row.get("candidate_index", -1))
        == int(plan["candidate_chunk_index"])
    ]
    if len(matching_jobs) != 1:
        raise ValueError("matrix lock does not bind the P027 certification output")

    rollout_sha256 = sha256_file(rollout_path)
    if plan.get("rollout_sha256") != rollout_sha256:
        raise ValueError("rollout bytes changed after search")
    manifest = json.loads(rollout_path.read_text(encoding="utf-8"))
    arrays_path = Path(str(manifest["arrays"])).resolve()
    if not arrays_path.is_file() or plan.get("arrays_sha256") != sha256_file(arrays_path):
        raise ValueError("source arrays changed after search")
    admission, admission_sha256 = load_json_once(admission_path)
    bddl_path = Path(str(manifest["bddl"])).resolve()
    if (
        plan.get("source_admission_report")
        != {"path": str(admission_path), "sha256": admission_sha256}
        or admission.get("passed") is not True
        or admission.get("source_rollout_sha256") != rollout_sha256
        or admission.get("source_arrays_sha256") != plan["arrays_sha256"]
        or admission.get("task_asset_bddl_sha256") != sha256_file(bddl_path)
    ):
        raise ValueError("source admission is invalid or changed")

    search_lock_reference = plan.get("search_run_lock")
    if not isinstance(search_lock_reference, dict):
        raise ValueError("selection plan has no search run lock")
    search_lock_path = Path(str(search_lock_reference.get("path"))).resolve()
    search_lock, search_lock_sha256 = load_json_once(search_lock_path)
    if search_lock_reference != {
        "path": str(search_lock_path),
        "sha256": search_lock_sha256,
    }:
        raise ValueError("search run lock changed after search")
    implementation = Path(__file__).resolve().parent
    locked_search_inputs = {
        "search_script": implementation / "search_p027_blackbox_cem.py",
        "compiler_dependency": implementation / "certify_continuous_contact_support.py",
        "selector_support": implementation / "certify_policy_boundary_alias.py",
        "repeat_envelope_support": implementation / "libero_m0_alias.py",
        "certificate_core": implementation / "israc" / "certificate.py",
        "source_arrays": arrays_path,
        "task_asset_bddl": bddl_path,
        "rollout": rollout_path,
        "source_admission_report": admission_path,
        "support_entrypoint": support_entrypoint,
    }
    for key, path in locked_search_inputs.items():
        if search_lock.get(key) != {"path": str(path), "sha256": sha256_file(path)}:
            raise ValueError(f"search dependency or asset drift: {key}")
    expected_search_invocation = {
        key: value
        for key, value in plan["arguments"].items()
        if key != "search_run_lock"
    }
    expected_search_invocation.update(
        {
            "rollout": str(rollout_path),
            "source_admission_report": str(admission_path),
            "support_code": str(support_path),
            "output": str(plan_path),
        }
    )
    expected_search_executions = 2 + 2 * int(plan["arguments"]["generations"]) * int(
        plan["arguments"]["population"]
    )
    if (
        search_lock.get("kind") != "p027_search_run_lock"
        or search_lock.get("protocol_version") != "P027-search-sanity-v1"
        or search_lock.get("frozen") is not True
        or search_lock.get("invocation") != expected_search_invocation
        or int(search_lock.get("precommitted_search_continuous_executions", -1))
        != expected_search_executions
    ):
        raise ValueError("search run lock does not reconstruct the search invocation")

    with np.load(arrays_path) as archive:
        chunks = np.asarray(archive["action_chunks"], dtype=np.float32)
    index = int(plan["candidate_chunk_index"])
    candidate_chunks = int(plan["arguments"]["candidate_chunks"])
    suffix_end = min(index + candidate_chunks, len(chunks))
    candidate_actions = np.concatenate(chunks[index:suffix_end], axis=0)
    wait_steps = int(manifest.get("num_steps_wait", 0))
    wait_action = np.asarray([0.0] * 6 + [-1.0], dtype=np.float32)
    warmup = np.repeat(wait_action[None, :], wait_steps, axis=0)
    factual_actions = np.concatenate((warmup, *chunks[:index]), axis=0)
    if (
        plan.get("candidate_suffix_end_index") != suffix_end - 1
        or plan.get("candidate_sha256") != base.canonical_array_sha256(candidate_actions)
        or plan.get("factual_action_sha256") != base.canonical_array_sha256(factual_actions)
    ):
        raise ValueError("candidate/factual action bundle differs from the plan")

    family = str(plan["parameter_family"])
    if family not in base.FAMILY_VALUES:
        raise ValueError("unknown parameter family")
    original_domain = tuple(float(value) for value in base.FAMILY_VALUES[family])
    lower, upper = (float(value) for value in plan["legal_domain"])
    if (lower, upper) != (min(original_domain), max(original_domain)):
        raise ValueError("selection plan changed the original legal parameter domain")
    evaluations = plan["evaluations"]
    should_search = bool(plan.get("boundary_eligible")) and int(
        plan.get("visible_pool_count", 0)
    ) > 0
    expected_evaluation_count = (
        int(plan["arguments"]["generations"]) * int(plan["arguments"]["population"])
        if should_search
        else 0
    )
    if len(evaluations) != expected_evaluation_count:
        raise ValueError("search stopped before its precommitted population count")
    for row in evaluations:
        pair = tuple(float(value) for value in row["parameter_values"])
        if not lower <= pair[0] < pair[1] <= upper:
            raise ValueError("evaluation pair escapes the original legal domain")
        feasible = bool(row["feasible"])
        activated = bool(row["candidate_activated"])
        state_effect = float(row["candidate_state_max_abs_between_values"])
        state_noise = float(row["candidate_repeat_state_envelope"])
        task_effect = float(row["candidate_task_effect_max_abs_between_values"])
        task_noise = float(row["candidate_repeat_task_effect_envelope"])
        expected_score = (
            max(0.0, state_effect - state_noise)
            if feasible and activated and math.isfinite(state_effect)
            else -1.0
        )
        expected_proxy = expected_score > 0.0 and task_effect > task_noise
        if not math.isclose(
            float(row["score"]), expected_score, rel_tol=0.0, abs_tol=1e-15
        ) or bool(row["certifiable_proxy"]) != expected_proxy:
            raise ValueError("evaluation score/proxy is not reconstructible")
    segment_steps = len(factual_actions) + len(candidate_actions)
    expected_executions = 2 + 2 * len(evaluations)
    expected_steps = expected_executions * segment_steps
    charged_steps = expected_search_executions * segment_steps
    if (
        int(plan.get("actual_search_continuous_executions", -1)) != expected_executions
        or int(plan.get("expected_search_simulator_steps", -1)) != expected_steps
        or int(plan.get("actual_search_simulator_steps", -1)) != expected_steps
        or int(plan.get("charged_search_simulator_step_cap", -1)) != charged_steps
    ):
        raise ValueError("search step accounting is not reconstructible")

    selected = reconstruct_selected(plan)
    if plan.get("selected_blocks") != selected:
        raise ValueError("selected block is not reproducible from evaluations")
    if not selected:
        return selected, tuple(
            float(value) for value in base.FAMILY_VALUES[str(plan["parameter_family"])]
        )
    pair = tuple(float(value) for value in selected[0]["parameter_values"])
    if not lower <= pair[0] < pair[1] <= upper:
        raise ValueError("selected continuous pair escapes the legal domain")
    return selected, pair


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection-plan", required=True)
    parser.add_argument("--rollout", required=True)
    parser.add_argument("--source-admission-report", required=True)
    parser.add_argument("--compiler-lock", required=True)
    parser.add_argument("--matrix-run-lock", required=True)
    parser.add_argument("--support-code", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    plan_path = Path(args.selection_plan).resolve()
    rollout_path = Path(args.rollout).resolve()
    admission_path = Path(args.source_admission_report).resolve()
    compiler_lock_path = Path(args.compiler_lock).resolve()
    matrix_lock_path = Path(args.matrix_run_lock).resolve()
    support_path = Path(args.support_code).resolve()
    output_path = Path(args.output).resolve()
    for path in (
        plan_path,
        rollout_path,
        admission_path,
        compiler_lock_path,
        matrix_lock_path,
    ):
        if not path.is_file():
            raise ValueError(f"missing required artifact: {path}")
    if not support_path.is_dir() or output_path.exists():
        raise ValueError("support/output path contract failed")

    plan, plan_sha256 = load_json_once(plan_path)
    selected, parameter_values = validate_plan(
        plan,
        plan_path=plan_path,
        plan_sha256=plan_sha256,
        rollout_path=rollout_path,
        admission_path=admission_path,
        compiler_lock_path=compiler_lock_path,
        matrix_lock_path=matrix_lock_path,
        support_path=support_path,
        output_path=output_path,
    )
    selected_pairs = [
        (str(row["parameter_address"]), tuple(int(v) for v in row["geom_ids"]))
        for row in selected
    ]

    original_select_blocks = base.select_blocks
    original_certificate = base.AliasCertificate
    family = str(plan["parameter_family"])
    original_values = tuple(base.FAMILY_VALUES[family])
    original_argv = sys.argv

    def select_from_plan(
        pool: dict[str, tuple[int, ...]],
        *,
        selector: str,
        max_blocks: int,
        seed: int,
    ) -> list[tuple[str, tuple[int, ...]]]:
        del seed
        if selector != plan["certifier_selector"] or max_blocks != 1:
            raise ValueError("certifier selector/cap differs from the frozen plan")
        for address, geom_ids in selected_pairs:
            if address not in pool or tuple(pool[address]) != geom_ids:
                raise ValueError(f"selected address escapes reconstructed pool: {address}")
        return selected_pairs

    def certificate_with_cem_objective(*certificate_args: Any, **kwargs: Any) -> Any:
        kwargs["search_objective_terms"] = (
            f"block_selector:{plan['selector']}",
            "mixed_categorical_continuous_cem",
            "factual_transcript_constraint",
            "candidate_state_divergence_above_repeat_noise",
            "fixed_pair_independent_raw_unedited_certification",
        )
        return original_certificate(*certificate_args, **kwargs)

    base.select_blocks = select_from_plan
    base.AliasCertificate = certificate_with_cem_objective
    certification_values = certification_grid(selected, parameter_values)
    base.FAMILY_VALUES[family] = certification_values
    sys.argv = [
        str(Path(base.__file__).resolve()),
        "--rollout", str(rollout_path),
        "--source-admission-report", str(admission_path),
        "--compiler-lock", str(compiler_lock_path),
        "--matrix-run-lock", str(matrix_lock_path),
        "--support-code", str(support_path),
        "--output", str(output_path),
        "--candidate-index", str(plan["candidate_chunk_index"]),
        "--candidate-chunks", str(plan["arguments"]["candidate_chunks"]),
        "--family", family,
        "--block-selector", str(plan["certifier_selector"]),
        "--selector-seed", str(plan["search_seed"]),
        "--max-selected-blocks", "1",
        "--height", str(plan["arguments"]["height"]),
        "--width", str(plan["arguments"]["width"]),
    ]
    try:
        invoke_base_main(base.main)
    finally:
        sys.argv = original_argv
        base.select_blocks = original_select_blocks
        base.AliasCertificate = original_certificate
        base.FAMILY_VALUES[family] = original_values

    if sha256_file(plan_path) != plan_sha256:
        raise RuntimeError("selection plan changed during certification")
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    if payload.get("protocol_version") != "P026-v1":
        raise RuntimeError("underlying certifier did not enter strict raw-unedited mode")
    selected_pair_passed = not selected
    if selected:
        left, right = parameter_values
        selected_pair_passed = any(
            math.isclose(float(row.get("left_value")), left, rel_tol=0.0, abs_tol=1e-15)
            and math.isclose(float(row.get("right_value")), right, rel_tol=0.0, abs_tol=1e-15)
            for block in payload.get("blocks", [])
            for row in block.get("endpoint_strength_curve", [])
        )
    print(
        json.dumps(
            {
                "protocol_version": payload["protocol_version"],
                "selected_block_count": payload["selected_block_count"],
                "unique_witness_count": payload["unique_witness_count"],
                "actual_certification_steps": payload["actual_simulator_steps"],
                "verified_search_steps": plan["actual_search_simulator_steps"],
                "charged_search_step_cap": plan[
                    "charged_search_simulator_step_cap"
                ],
                "selected_continuous_pair_passed": selected_pair_passed,
            },
            sort_keys=True,
        )
    )
    if selected and not selected_pair_passed:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
