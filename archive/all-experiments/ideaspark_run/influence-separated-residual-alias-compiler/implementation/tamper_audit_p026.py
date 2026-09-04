#!/usr/bin/env python3
"""Adversarially mutate one P026 manifest and require fail-closed verification."""

from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Callable


def set_bad_sha(record: dict[str, Any], key: str) -> None:
    record[key]["sha256"] = "0" * 64


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--verifier", required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--allowed-root", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    manifest_path = Path(args.manifest).resolve()
    with manifest_path.open("r", encoding="utf-8") as handle:
        original = json.load(handle)
    output_dir = Path(args.output_dir).resolve()
    if output_dir.exists():
        raise ValueError(f"refusing to overwrite tamper audit: {output_dir}")
    output_dir.mkdir(parents=True)

    def duplicate_nominal(record: dict[str, Any]) -> None:
        record["nominal_unedited_repeat_evidence"] = copy.deepcopy(
            record["nominal_unedited_evidence"]
        )

    def swap_nominal(record: dict[str, Any]) -> None:
        record["nominal_unedited_evidence"], record["nominal_unedited_repeat_evidence"] = (
            record["nominal_unedited_repeat_evidence"],
            record["nominal_unedited_evidence"],
        )

    def tamper_witness_fields(record: dict[str, Any]) -> None:
        if not record.get("blocks"):
            raise ValueError("sanity manifest must contain a block for witness tamper audit")
        record["blocks"][0]["witness_key_fields"]["boundary_step"] += 1

    def tamper_witness_sha(record: dict[str, Any]) -> None:
        if not record.get("blocks"):
            raise ValueError("sanity manifest must contain a block for witness tamper audit")
        record["blocks"][0]["witness_key"] = "0" * 64

    def reconcile_after_block_deletion(record: dict[str, Any]) -> None:
        selected = len(record["blocks"])
        segment_steps = int(record["factual_action_steps"]) + int(
            record["candidate_action_steps"]
        )
        executions = 2 + 4 * selected
        actual_steps = executions * segment_steps
        record["selected_block_count"] = selected
        record["raw_endpoint_pair_count"] = sum(
            int(block["certified_endpoint_pairs"]) for block in record["blocks"]
        )
        record["unique_witness_count"] = sum(
            int(block["unique_witness"]) for block in record["blocks"]
        )
        record["actual_continuous_executions"] = executions
        record["actual_simulator_steps"] = actual_steps
        record["expected_actual_simulator_steps"] = actual_steps
        record["unused_simulator_step_budget"] = (
            int(record["charged_simulator_step_cap"]) - actual_steps
        )
        record["passed"] = bool(record["unique_witness_count"])

    def delete_first_block(record: dict[str, Any]) -> None:
        if not record.get("blocks"):
            raise ValueError("sanity manifest must contain a block for deletion audit")
        record["blocks"].pop(0)
        reconcile_after_block_deletion(record)

    def delete_all_blocks(record: dict[str, Any]) -> None:
        if not record.get("blocks"):
            raise ValueError("sanity manifest must contain a block for deletion audit")
        record["blocks"] = []
        reconcile_after_block_deletion(record)

    def reorder_blocks(record: dict[str, Any]) -> None:
        if len(record.get("blocks", [])) < 2:
            raise ValueError("sanity manifest needs two blocks for order audit")
        record["blocks"].reverse()

    def tamper_contact_topology(record: dict[str, Any]) -> None:
        if not record.get("contact_topology"):
            raise ValueError("sanity manifest lacks contact topology")
        record["contact_topology"][0]["geom_name"] += "_tampered"

    mutations: dict[str, Callable[[dict[str, Any]], None]] = {
        "source_admission_hash": lambda record: set_bad_sha(record, "source_admission_report"),
        "compiler_lock_hash": lambda record: set_bad_sha(record, "compiler_lock"),
        "matrix_lock_hash": lambda record: set_bad_sha(record, "matrix_run_lock"),
        "matrix_lock_path": lambda record: record["matrix_run_lock"].__setitem__(
            "path", str(output_dir / "fake-matrix-lock.json")
        ),
        "matrix_job_output": lambda record: record.__setitem__(
            "artifact_output_path", str(output_dir / "wrong-artifact.json")
        ),
        "matrix_job_selector": lambda record: record.__setitem__(
            "block_selector", "random-scene"
        ),
        "nominal_hash": lambda record: set_bad_sha(record, "nominal_unedited_evidence"),
        "duplicate_nominal_repeat": duplicate_nominal,
        "swap_nominal_kinds": swap_nominal,
        "remove_compiler_lock": lambda record: record.pop("compiler_lock"),
        "flip_boundary_eligibility": lambda record: record.__setitem__(
            "boundary_eligible", not bool(record["boundary_eligible"])
        ),
        "inflate_replay_tolerance": lambda record: record.__setitem__(
            "replay_endpoint_tolerance", float(record["replay_endpoint_tolerance"]) + 1.0
        ),
        "change_charged_budget": lambda record: record.__setitem__(
            "charged_simulator_step_cap", int(record["charged_simulator_step_cap"]) + 1
        ),
        "change_compiler_argument": lambda record: record["arguments"].__setitem__(
            "compiler_lock", str(output_dir / "fake-lock.json")
        ),
        "witness_key_fields": tamper_witness_fields,
        "witness_key_sha": tamper_witness_sha,
        "delete_first_selected_block_and_reconcile": delete_first_block,
        "delete_all_selected_blocks_and_reconcile": delete_all_blocks,
        "reorder_selected_blocks": reorder_blocks,
        "contact_topology": tamper_contact_topology,
    }

    command_base = [
        args.python,
        args.verifier,
        "--allowed-root",
        args.allowed_root,
    ]
    baseline = subprocess.run(
        [*command_base, "--manifest", str(manifest_path)],
        text=True,
        capture_output=True,
    )
    if baseline.returncode != 0:
        raise RuntimeError(f"untampered manifest failed verification: {baseline.stderr}")
    rows = []
    for name, mutate in mutations.items():
        record = copy.deepcopy(original)
        mutate(record)
        path = output_dir / f"{name}.json"
        path.write_text(
            json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [*command_base, "--manifest", str(path)],
            text=True,
            capture_output=True,
        )
        rows.append({
            "mutation": name,
            "rejected": result.returncode != 0,
            "returncode": result.returncode,
            "stderr_tail": result.stderr[-500:],
            "stdout_tail": result.stdout[-500:],
        })
    passed = all(row["rejected"] for row in rows)
    audit = {
        "kind": "p026_manifest_tamper_audit",
        "source_manifest": str(manifest_path),
        "attack_count": len(rows),
        "rejected_count": sum(row["rejected"] for row in rows),
        "passed": passed,
        "attacks": rows,
    }
    audit_path = output_dir / "AUDIT.json"
    temporary = audit_path.with_suffix(f".tmp.{os.getpid()}")
    temporary.write_text(
        json.dumps(audit, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, audit_path)
    print(json.dumps({
        "attack_count": len(rows),
        "rejected_count": audit["rejected_count"],
        "passed": passed,
        "audit": str(audit_path),
    }, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
