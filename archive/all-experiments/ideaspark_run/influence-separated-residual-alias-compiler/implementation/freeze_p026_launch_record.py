#!/usr/bin/env python3
"""Create a one-shot launch record before any locked P026 matrix cell starts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--boundary-plan", required=True)
    parser.add_argument("--boundary-plan-sha256", required=True)
    parser.add_argument("--compiler-lock", required=True)
    parser.add_argument("--compiler-lock-sha256", required=True)
    parser.add_argument("--matrix-run-lock", required=True)
    parser.add_argument("--matrix-run-lock-sha256", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    plan = Path(args.boundary_plan).resolve()
    compiler = Path(args.compiler_lock).resolve()
    matrix = Path(args.matrix_run_lock).resolve()
    output = Path(args.output).resolve()
    if output.exists():
        raise ValueError(f"refusing to overwrite launch record: {output}")
    references = (
        (plan, args.boundary_plan_sha256, "boundary plan"),
        (compiler, args.compiler_lock_sha256, "compiler lock"),
        (matrix, args.matrix_run_lock_sha256, "matrix-run lock"),
    )
    for path, expected, label in references:
        if sha256_file(path) != expected:
            raise ValueError(f"{label} hash mismatch")
    matrix_payload = read_json(matrix)
    plan_reference = {"path": str(plan), "sha256": args.boundary_plan_sha256}
    compiler_reference = {"path": str(compiler), "sha256": args.compiler_lock_sha256}
    matrix_reference = {"path": str(matrix), "sha256": args.matrix_run_lock_sha256}
    if (
        matrix_payload.get("kind") != "p026_matrix_run_lock"
        or matrix_payload.get("frozen") is not True
        or matrix_payload.get("boundary_plan") != plan_reference
        or matrix_payload.get("compiler_lock") != compiler_reference
    ):
        raise ValueError("matrix-run lock chain is invalid")
    output_dir = Path(str(matrix_payload["output_directory"])).resolve()
    if not output_dir.is_dir() or any(output_dir.iterdir()):
        raise ValueError("matrix output directory is not empty immediately before launch")
    payload = {
        "kind": "p026_immutable_launch_record",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": matrix_payload["purpose"],
        "confirmatory_label": matrix_payload["confirmatory_label"],
        "boundary_plan": plan_reference,
        "compiler_lock": compiler_reference,
        "matrix_run_lock": matrix_reference,
        "matrix_job_count": int(matrix_payload["job_count"]),
        "output_directory": str(output_dir),
        "output_directory_entries_at_launch": [],
        "no_formal_cell_started_before_record": True,
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
        "purpose": payload["purpose"],
        "matrix_job_count": payload["matrix_job_count"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
