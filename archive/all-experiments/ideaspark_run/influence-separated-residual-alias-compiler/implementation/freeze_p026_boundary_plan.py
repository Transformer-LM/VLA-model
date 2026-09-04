#!/usr/bin/env python3
"""Freeze the P026 outcome-blind boundary roster before compiler execution."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


ROSTER = (
    (3, 1, 47),
    (4, 1, 53),
    (5, 1, 59),
    (6, 1, 61),
    (7, 1, 67),
    (8, 1, 71),
    (9, 1, 73),
)


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
        payload = json.load(handle, parse_constant=reject)
    if not isinstance(payload, dict):
        raise ValueError(f"JSON object required: {path}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-root", required=True)
    parser.add_argument("--policy-lock", required=True)
    parser.add_argument("--preregistration", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    root = Path(args.results_root).resolve()
    policy_lock = Path(args.policy_lock).resolve()
    preregistration = Path(args.preregistration).resolve()
    output = Path(args.output).resolve()
    if output.exists():
        raise ValueError(f"refusing to overwrite frozen plan: {output}")

    entries: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    for task_id, episode_index, seed in ROSTER:
        suffix = f"libero_goal_task{task_id}_ep{episode_index}_seed{seed}"
        source_path = root / f"P026_CONFIRM_SOURCE_{suffix}.json"
        admission_path = root / f"P026_CONFIRM_ADMISSION_{suffix}.json"
        source = read_json(source_path)
        admission = read_json(admission_path)
        source_sha = sha256_file(source_path)
        admission_sha = sha256_file(admission_path)
        initialization = source.get("initialization", {})
        if (
            source.get("source_schema_version") != "P026-source-v1"
            or int(source.get("seed", -1)) != seed
            or initialization.get("suite_name") != "libero_goal"
            or int(initialization.get("task_id", -1)) != task_id
            or int(initialization.get("episode_index", -1)) != episode_index
        ):
            raise ValueError(f"source roster mismatch: {source_path}")
        if (
            admission.get("passed") is not True
            or admission.get("policy_identity_verified") is not True
            or admission.get("policy_lock_verified") is not True
            or admission.get("source_rollout_sha256") != source_sha
            or Path(str(admission.get("source_rollout"))).resolve() != source_path
        ):
            raise ValueError(f"source admission mismatch: {admission_path}")
        arrays_path = Path(str(source["arrays"])).resolve()
        arrays_sha = sha256_file(arrays_path)
        if admission.get("source_arrays_sha256") != arrays_sha:
            raise ValueError(f"source array admission mismatch: {arrays_path}")
        with np.load(arrays_path, allow_pickle=False) as archive:
            chunk_count = len(np.asarray(archive["action_chunks"]))
            boundary_steps = np.asarray(archive["boundary_steps"], dtype=np.int64)
        if chunk_count != int(source["chunk_count"]) or len(boundary_steps) != chunk_count:
            raise ValueError(f"source chunk schema mismatch: {source_path}")
        ranked = sorted(
            range(1, chunk_count),
            key=lambda index: hashlib.sha256(
                f"{source_sha}|{index}".encode("utf-8")
            ).hexdigest(),
        )
        selected = ranked[:3]
        if not selected:
            raise ValueError(f"source has no eligible candidate index: {source_path}")
        source_rows.append({
            "task_id": task_id,
            "episode_index": episode_index,
            "environment_seed": seed,
            "source_rollout": str(source_path),
            "source_rollout_sha256": source_sha,
            "source_arrays": str(arrays_path),
            "source_arrays_sha256": arrays_sha,
            "source_admission": str(admission_path),
            "source_admission_sha256": admission_sha,
            "chunk_count": chunk_count,
            "selected_candidate_indices": selected,
        })
        for index in selected:
            entries.append({
                "task_id": task_id,
                "episode_index": episode_index,
                "environment_seed": seed,
                "source_rollout": str(source_path),
                "source_rollout_sha256": source_sha,
                "source_admission": str(admission_path),
                "source_admission_sha256": admission_sha,
                "candidate_index": index,
                "candidate_boundary_step": int(boundary_steps[index]),
                "selection_digest": hashlib.sha256(
                    f"{source_sha}|{index}".encode("utf-8")
                ).hexdigest(),
            })

    payload = {
        "kind": "p026_outcome_blind_boundary_plan",
        "protocol_version": "P026-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_before_compiler_execution": True,
        "selection_rule": "lowest_3_sha256(source_manifest_sha256|candidate_index), indices 1..N-1",
        "policy_lock": {"path": str(policy_lock), "sha256": sha256_file(policy_lock)},
        "preregistration": {
            "path": str(preregistration),
            "sha256": sha256_file(preregistration),
        },
        "selectors": ["israc-contact-subtraction", "candidate-contact", "random-scene"],
        "selector_seeds": [0, 1, 2],
        "physical_family": "compliance",
        "candidate_chunks": 4,
        "max_selected_blocks": 3,
        "invalid_boundary_treatment": "zero_witness_full_cap_charge",
        "source_count": len(source_rows),
        "boundary_count": len(entries),
        "sources": source_rows,
        "boundaries": entries,
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
        "source_count": len(source_rows),
        "boundary_count": len(entries),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
