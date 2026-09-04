#!/usr/bin/env python3
"""Freeze unique absolute paths for a P026 sanity or formal matrix run."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SHORT = {
    "israc-contact-subtraction": "israc",
    "candidate-contact": "candidate",
    "random-scene": "random",
}


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
    parser.add_argument("--purpose", choices=("sanity", "formal"), required=True)
    parser.add_argument("--boundary-plan", required=True)
    parser.add_argument("--boundary-plan-sha256", required=True)
    parser.add_argument("--compiler-lock", required=True)
    parser.add_argument("--compiler-lock-sha256", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    plan_path = Path(args.boundary_plan).resolve()
    compiler_path = Path(args.compiler_lock).resolve()
    output_dir = Path(args.output_dir).resolve()
    output = Path(args.output).resolve()
    if output.exists():
        raise ValueError(f"refusing to overwrite matrix-run lock: {output}")
    if sha256_file(plan_path) != args.boundary_plan_sha256:
        raise ValueError("boundary plan hash mismatch")
    if sha256_file(compiler_path) != args.compiler_lock_sha256:
        raise ValueError("compiler lock hash mismatch")
    plan = read_json(plan_path)
    compiler = read_json(compiler_path)
    if compiler.get("boundary_plan", {}).get("sha256") != args.boundary_plan_sha256:
        raise ValueError("compiler lock is bound to another boundary plan")
    if output_dir.exists():
        if not output_dir.is_dir() or any(output_dir.iterdir()):
            raise ValueError("matrix output directory must be new or empty at freeze time")
    else:
        output_dir.mkdir(parents=False)

    if args.purpose == "formal":
        boundaries = list(plan["boundaries"])
        selectors = list(plan["selectors"])
        seeds = [int(value) for value in plan["selector_seeds"]]
    else:
        boundaries = list(plan["boundaries"][:1])
        selectors = ["candidate-contact"]
        seeds = [0]
    jobs = []
    for selector in selectors:
        for seed in seeds:
            for boundary in boundaries:
                tag = (
                    f"t{int(boundary['task_id'])}_e{int(boundary['episode_index'])}_"
                    f"c{int(boundary['candidate_index']):02d}_{SHORT[selector]}_seed{seed}"
                )
                jobs.append({
                    "source_rollout": str(Path(str(boundary["source_rollout"])).resolve()),
                    "source_rollout_sha256": str(boundary["source_rollout_sha256"]),
                    "source_admission": str(Path(str(boundary["source_admission"])).resolve()),
                    "source_admission_sha256": str(boundary["source_admission_sha256"]),
                    "candidate_index": int(boundary["candidate_index"]),
                    "selector": selector,
                    "selector_seed": seed,
                    "output": str(output_dir / f"{args.prefix}_{tag}.json"),
                    "log": str(output_dir / f"{args.prefix}_{tag}.log"),
                })
    expected_count = 189 if args.purpose == "formal" else 1
    if len(jobs) != expected_count or len({row["output"] for row in jobs}) != len(jobs):
        raise ValueError("matrix-run job construction is incomplete or non-unique")
    payload = {
        "kind": "p026_matrix_run_lock",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "frozen": True,
        "run_id": f"p026-{args.purpose}-v1",
        "purpose": args.purpose,
        "confirmatory_label": (
            "amended_confirmatory_with_disclosed_three_cell_pre_formal_contamination"
            if args.purpose == "formal" else "code_lock_sanity_only"
        ),
        "boundary_plan": {"path": str(plan_path), "sha256": args.boundary_plan_sha256},
        "compiler_lock": {"path": str(compiler_path), "sha256": args.compiler_lock_sha256},
        "output_directory": str(output_dir),
        "output_directory_empty_at_freeze": True,
        "prefix": args.prefix,
        "job_count": len(jobs),
        "failure_retry_policy": (
            "No replacement path or alternate artifact. A completed artifact may only be reused "
            "after full semantic verification under this exact lock. A cell interrupted before "
            "manifest commit makes the matrix incomplete; partial evidence is preserved."
        ),
        "jobs": jobs,
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
        "job_count": len(jobs),
        "output_directory": str(output_dir),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
