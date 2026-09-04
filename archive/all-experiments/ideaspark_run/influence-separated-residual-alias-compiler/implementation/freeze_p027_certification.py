#!/usr/bin/env python3
"""Freeze P027 selection, code, and one strict certification job."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reference(path: Path) -> dict[str, str]:
    resolved = path.resolve()
    if not resolved.is_file():
        raise ValueError(f"missing lock input: {resolved}")
    return {"path": str(resolved), "sha256": sha256_file(resolved)}


def write_exclusive(path: Path, payload: dict[str, Any]) -> None:
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o664)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection-plan", required=True)
    parser.add_argument("--base-compiler-lock", required=True)
    parser.add_argument("--search-script", required=True)
    parser.add_argument("--search-lock-builder", required=True)
    parser.add_argument("--certifier-adapter", required=True)
    parser.add_argument("--certification-lock-builder", required=True)
    parser.add_argument("--source-admission-report", required=True)
    parser.add_argument("--certification-output", required=True)
    parser.add_argument("--compiler-lock-output", required=True)
    parser.add_argument("--matrix-lock-output", required=True)
    args = parser.parse_args()

    plan_path = Path(args.selection_plan).resolve()
    base_lock_path = Path(args.base_compiler_lock).resolve()
    admission_path = Path(args.source_admission_report).resolve()
    certification_output = Path(args.certification_output).resolve()
    compiler_output = Path(args.compiler_lock_output).resolve()
    matrix_output = Path(args.matrix_lock_output).resolve()
    if any(path.exists() for path in (certification_output, compiler_output, matrix_output)):
        raise ValueError("certification/lock outputs must be absent")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if (
        plan.get("protocol_version") != "P027-search-sanity-v1"
        or plan.get("compiler_target_wam_blind") is not True
        or plan.get("target_wam_used_in_search") is not False
    ):
        raise ValueError("selection plan header is invalid")
    search_lock_reference = plan.get("search_run_lock")
    search_lock_path = Path(str(search_lock_reference.get("path"))).resolve()
    if search_lock_reference != reference(search_lock_path):
        raise ValueError("selection plan is not bound to its search run lock")

    base_lock = json.loads(base_lock_path.read_text(encoding="utf-8"))
    if base_lock.get("kind") != "p026_compiler_code_lock" or base_lock.get(
        "frozen"
    ) is not True:
        raise ValueError("base P026 compiler lock is invalid")
    files = list(base_lock["files"])
    additions = [
        ("p027_selection_plan", plan_path),
        ("p027_search_run_lock", search_lock_path),
        ("p027_search", Path(args.search_script)),
        ("p027_search_lock_builder", Path(args.search_lock_builder)),
        ("p027_certifier_adapter", Path(args.certifier_adapter)),
        ("p027_certification_lock_builder", Path(args.certification_lock_builder)),
    ]
    for role, path in additions:
        item = reference(path)
        item["role"] = role
        files.append(item)
    compiler_payload = dict(base_lock)
    compiler_payload.update(
        {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "files": files,
            "p027_parent_compiler_lock": reference(base_lock_path),
            "p027_protocol_version": "P027-search-sanity-v1",
        }
    )
    write_exclusive(compiler_output, compiler_payload)
    compiler_reference = reference(compiler_output)

    rollout_path = Path(str(plan["rollout"])).resolve()
    admission_reference = reference(admission_path)
    matrix_payload = {
        "kind": "p026_matrix_run_lock",
        "frozen": True,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "boundary_plan": compiler_payload["boundary_plan"],
        "compiler_lock": compiler_reference,
        "p027_protocol_version": "P027-search-sanity-v1",
        "jobs": [
            {
                "output": str(certification_output),
                "source_rollout": str(rollout_path),
                "source_rollout_sha256": sha256_file(rollout_path),
                "source_admission": str(admission_path),
                "source_admission_sha256": admission_reference["sha256"],
                "candidate_index": int(plan["candidate_chunk_index"]),
                "selector": str(plan["certifier_selector"]),
                "selector_seed": int(plan["search_seed"]),
            }
        ],
    }
    try:
        write_exclusive(matrix_output, matrix_payload)
    except BaseException:
        compiler_output.unlink(missing_ok=True)
        raise
    print(
        json.dumps(
            {
                "compiler_lock": reference(compiler_output),
                "matrix_lock": reference(matrix_output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
