#!/usr/bin/env python3
"""Freeze one outcome-blind P027 CEM search invocation before it runs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rollout", required=True)
    parser.add_argument("--source-admission-report", required=True)
    parser.add_argument("--support-code", required=True)
    parser.add_argument("--search-script", required=True)
    parser.add_argument("--selection-output", required=True)
    parser.add_argument("--lock-output", required=True)
    parser.add_argument("--candidate-index", type=int, required=True)
    parser.add_argument("--candidate-chunks", type=int, default=4)
    parser.add_argument("--family", choices=("compliance", "friction"), required=True)
    parser.add_argument(
        "--selector", choices=("candidate-contact-cem", "scene-cem"), required=True
    )
    parser.add_argument("--search-seed", type=int, default=0)
    parser.add_argument("--generations", type=int, default=2)
    parser.add_argument("--population", type=int, default=6)
    parser.add_argument("--elite-count", type=int, default=2)
    parser.add_argument("--smoothing", type=float, default=0.20)
    parser.add_argument("--min-log-std-fraction", type=float, default=0.08)
    parser.add_argument("--max-selected-blocks", type=int, default=1)
    parser.add_argument("--height", type=int, default=64)
    parser.add_argument("--width", type=int, default=64)
    args = parser.parse_args()

    rollout = Path(args.rollout).resolve()
    admission = Path(args.source_admission_report).resolve()
    support = Path(args.support_code).resolve()
    search_script = Path(args.search_script).resolve()
    selection_output = Path(args.selection_output).resolve()
    lock_output = Path(args.lock_output).resolve()
    if not support.is_dir() or selection_output.exists() or lock_output.exists():
        raise ValueError("support/empty output contract failed")
    support_entry = support / "collect_e1_paired_rollouts.py"
    manifest = json.loads(rollout.read_text(encoding="utf-8"))
    arrays_path = Path(str(manifest["arrays"])).resolve()
    bddl_path = Path(str(manifest["bddl"])).resolve()
    implementation = search_script.parent
    invocation = {
        "rollout": str(rollout),
        "source_admission_report": str(admission),
        "support_code": str(support),
        "output": str(selection_output),
        "candidate_index": args.candidate_index,
        "candidate_chunks": args.candidate_chunks,
        "family": args.family,
        "selector": args.selector,
        "search_seed": args.search_seed,
        "generations": args.generations,
        "population": args.population,
        "elite_count": args.elite_count,
        "smoothing": args.smoothing,
        "min_log_std_fraction": args.min_log_std_fraction,
        "max_selected_blocks": args.max_selected_blocks,
        "height": args.height,
        "width": args.width,
    }
    payload = {
        "kind": "p027_search_run_lock",
        "protocol_version": "P027-search-sanity-v1",
        "frozen": True,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "compiler_target_wam_blind": True,
        "search_script": reference(search_script),
        "compiler_dependency": reference(
            implementation / "certify_continuous_contact_support.py"
        ),
        "selector_support": reference(
            implementation / "certify_policy_boundary_alias.py"
        ),
        "repeat_envelope_support": reference(implementation / "libero_m0_alias.py"),
        "certificate_core": reference(implementation / "israc" / "certificate.py"),
        "rollout": reference(rollout),
        "source_arrays": reference(arrays_path),
        "task_asset_bddl": reference(bddl_path),
        "source_admission_report": reference(admission),
        "support_entrypoint": reference(support_entry),
        "invocation": invocation,
        "precommitted_search_continuous_executions": (
            2 + 2 * args.generations * args.population
        ),
    }
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    lock_output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(lock_output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o664)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        lock_output.unlink(missing_ok=True)
        raise
    print(json.dumps({"lock": str(lock_output), "sha256": sha256_file(lock_output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
