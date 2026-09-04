#!/usr/bin/env python3
"""Freeze the exact P026 compiler, verifier, runner, and analysis code bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reference(path: Path, role: str) -> dict[str, str]:
    path = path.resolve()
    if not path.is_file():
        raise ValueError(f"missing locked file: {path}")
    return {"role": role, "path": str(path), "sha256": sha256_file(path)}


def plain_reference(path: Path) -> dict[str, str]:
    path = path.resolve()
    return {"path": str(path), "sha256": sha256_file(path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--implementation-root", required=True)
    parser.add_argument("--support-code", required=True)
    parser.add_argument("--boundary-plan", required=True)
    parser.add_argument("--preregistration", required=True)
    parser.add_argument("--policy-lock", required=True)
    parser.add_argument("--protocol-amendment-v1", required=True)
    parser.add_argument("--protocol-amendment-v2", required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    implementation = Path(args.implementation_root).resolve()
    support = Path(args.support_code).resolve()
    plan = Path(args.boundary_plan).resolve()
    preregistration = Path(args.preregistration).resolve()
    policy_lock = Path(args.policy_lock).resolve()
    protocol_amendment_v1 = Path(args.protocol_amendment_v1).resolve()
    protocol_amendment_v2 = Path(args.protocol_amendment_v2).resolve()
    python = Path(args.python)
    output = Path(args.output).resolve()
    if output.exists():
        raise ValueError(f"refusing to overwrite compiler lock: {output}")
    amendment_v1 = plain_reference(protocol_amendment_v1)
    amendment_v2 = plain_reference(protocol_amendment_v2)
    if (
        protocol_amendment_v1.name != "P026_PROTOCOL_AMENDMENT.md"
        or protocol_amendment_v2.name != "P026_PROTOCOL_AMENDMENT_V2.md"
        or protocol_amendment_v1 == protocol_amendment_v2
        or amendment_v1["sha256"] == amendment_v2["sha256"]
    ):
        raise ValueError("protocol amendments must be distinct exact v1/v2 files")
    if amendment_v1["sha256"] not in protocol_amendment_v2.read_text(encoding="utf-8"):
        raise ValueError("protocol amendment v2 does not pin the exact v1 SHA-256")

    with plan.open("r", encoding="utf-8") as handle:
        plan_payload = json.load(handle)
    if (
        plan_payload.get("kind") != "p026_outcome_blind_boundary_plan"
        or plan_payload.get("protocol_version") != "P026-v1"
        or plan_payload.get("frozen_before_compiler_execution") is not True
    ):
        raise ValueError("boundary plan is not a frozen P026 plan")
    if plan_payload.get("preregistration") != plain_reference(preregistration):
        raise ValueError("compiler preregistration differs from boundary plan")
    if plan_payload.get("policy_lock") != plain_reference(policy_lock):
        raise ValueError("compiler policy lock differs from boundary plan")

    files = [
        reference(implementation / "certify_continuous_contact_support.py", "compiler"),
        reference(implementation / "verify_p025_manifest.py", "manifest_verifier"),
        reference(implementation / "analyze_p025_fixed_budget.py", "p025_schema_validator"),
        reference(implementation / "analyze_p026_confirmatory.py", "p026_analyzer"),
        reference(implementation / "run_p026_compiler_matrix.py", "matrix_runner"),
        reference(implementation / "freeze_p026_matrix_run.py", "matrix_lock_builder"),
        reference(implementation / "freeze_p026_launch_record.py", "launch_record_builder"),
        reference(implementation / "certify_policy_boundary_alias.py", "selector_support"),
        reference(implementation / "israc" / "certificate.py", "certificate_core"),
        reference(implementation / "libero_m0_alias.py", "repeat_envelope"),
        reference(support / "collect_e1_paired_rollouts.py", "observation_support"),
    ]
    payload = {
        "kind": "p026_compiler_code_lock",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "frozen": True,
        "boundary_plan": plain_reference(plan),
        "preregistration": plain_reference(preregistration),
        "policy_lock": plain_reference(policy_lock),
        "protocol_amendments": [
            {
                "version": "v1",
                **amendment_v1,
            },
            {
                "version": "v2",
                "predecessor_sha256": amendment_v1["sha256"],
                **amendment_v2,
            },
        ],
        "python_entrypoint": str(python),
        "files": files,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + f".tmp.{os.getpid()}")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, output)
    print(json.dumps({
        "output": str(output),
        "sha256": sha256_file(output),
        "file_count": len(files),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
