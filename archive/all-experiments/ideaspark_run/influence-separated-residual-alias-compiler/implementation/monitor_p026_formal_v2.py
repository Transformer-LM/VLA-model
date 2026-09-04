#!/usr/bin/env python3
"""Read-only progress summary for the locked P026 V2 formal matrix."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import glob
import json
import os
from pathlib import Path


RESULTS = Path("<PERSONAL_RESEARCH_ROOT>/results/israc/P026_FORMAL_V2")
LOCK = Path("<PERSONAL_RESEARCH_ROOT>/results/israc/P026_FORMAL_MATRIX_LOCK_V2.json")
RUNNER_LOG = Path("<PERSONAL_RESEARCH_ROOT>/results/israc/P026_FORMAL_V2_RUNNER.log")


def main() -> int:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    manifests = sorted(
        path for path in RESULTS.glob("P026_FORMAL_V2_*.json")
        if path.name != "MATRIX_RUN_STARTED.json"
    )
    selectors: Counter[str] = Counter()
    selector_seeds: Counter[str] = Counter()
    unique_by_selector_seed: Counter[str] = Counter()
    pairs_by_selector_seed: Counter[str] = Counter()
    verified_rows: dict[tuple[str, int, str, int], dict] = {}
    unique = raw_pairs = 0
    malformed = []
    log_paths = sorted(RESULTS.glob("P026_FORMAL_V2_*.log"))
    verified_stems = set()
    failure_logs = []
    for path in log_paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        verifier_section = text.split("VERIFIER_STDOUT\n", 1)
        if (
            len(verifier_section) == 2
            and '"passed": true' in verifier_section[1]
            and "Traceback" not in verifier_section[1]
        ):
            verified_stems.add(path.stem)
        if "compiler failed" in text or "verifier failed" in text or "Traceback" in text:
            failure_logs.append(str(path))
    for path in manifests:
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
            if row.get("kind") != "israc_continuous_geom_contact_support_e0":
                raise ValueError("kind")
            if path.stem in verified_stems:
                selector = str(row["block_selector"])
                selector_seed = f"{selector}|seed{int(row['selector_seed'])}"
                row_unique = int(row["unique_witness_count"])
                row_pairs = int(row["raw_endpoint_pair_count"])
                selectors[selector] += 1
                selector_seeds[selector_seed] += 1
                unique_by_selector_seed[selector_seed] += row_unique
                pairs_by_selector_seed[selector_seed] += row_pairs
                verified_rows[
                    (
                        selector,
                        int(row["selector_seed"]),
                        str(row["rollout_sha256"]),
                        int(row["candidate_chunk_index"]),
                    )
                ] = row
                unique += row_unique
                raw_pairs += row_pairs
        except Exception as error:
            malformed.append({"path": str(path), "error": repr(error)})
    bytes_total = 0
    for root, _, names in os.walk(RESULTS):
        for name in names:
            try:
                bytes_total += (Path(root) / name).stat().st_size
            except FileNotFoundError:
                pass
    runner_tail = []
    if RUNNER_LOG.is_file():
        runner_tail = RUNNER_LOG.read_text(
            encoding="utf-8", errors="replace"
        ).splitlines()[-8:]
    matched = {}
    method = "israc-contact-subtraction"
    for selector_seed in sorted(selector_seeds):
        selector, seed_text = selector_seed.rsplit("|seed", 1)
        if selector == method:
            continue
        seed = int(seed_text)
        baseline_rows = [
            (key, row)
            for key, row in verified_rows.items()
            if key[0] == selector and key[1] == seed
        ]
        method_sum = baseline_sum = 0
        matched_cells = 0
        for key, baseline_row in baseline_rows:
            method_key = (method, seed, key[2], key[3])
            method_row = verified_rows.get(method_key)
            if method_row is None:
                continue
            matched_cells += 1
            method_sum += int(method_row["unique_witness_count"])
            baseline_sum += int(baseline_row["unique_witness_count"])
        matched[selector_seed] = {
            "matched_verified_cells": matched_cells,
            "israc_witness_sum": method_sum,
            "baseline_witness_sum": baseline_sum,
            "provisional_ratio": (
                method_sum / baseline_sum
                if baseline_sum > 0
                else ("infinite" if method_sum > 0 else 1.0)
            ),
        }
    payload = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "expected_jobs": int(lock["job_count"]),
        "committed_manifests": len(manifests),
        "verifier_completed_cells": len(verified_stems),
        "completed_logs": len(log_paths),
        "temporary_evidence_directories": len(list(RESULTS.glob("*.evidence.tmp.*"))),
        "completed_by_selector": dict(sorted(selectors.items())),
        "completed_by_selector_seed": dict(sorted(selector_seeds.items())),
        "witnesses_by_selector_seed_not_cross_seed_deduplicated": dict(
            sorted(unique_by_selector_seed.items())
        ),
        "pairs_by_selector_seed": dict(sorted(pairs_by_selector_seed.items())),
        "matched_comparison_to_israc_by_selector_seed": matched,
        "provisional_unique_witness_sum_not_deduplicated": unique,
        "provisional_raw_pair_sum": raw_pairs,
        "failure_log_count": len(failure_logs),
        "failure_logs": failure_logs[:8],
        "malformed_manifest_count": len(malformed),
        "malformed_manifests": malformed[:8],
        "result_bytes": bytes_total,
        "runner_log_tail": runner_tail,
        "matrix_started_marker": (RESULTS / "MATRIX_RUN_STARTED.json").is_file(),
    }
    print(json.dumps(payload, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
