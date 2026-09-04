#!/usr/bin/env python3
"""Freeze the exact policy/code/inference identity and unseen P026 roster."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tarfile
from typing import Any

from verify_source_rollout_replay import PERSONAL_ROOT, sha256_file, verify_policy_identity


ROSTER = [
    {"suite_name": "libero_goal", "task_id": 3, "episode_index": 1, "seed": 47},
    {"suite_name": "libero_goal", "task_id": 4, "episode_index": 1, "seed": 53},
    {"suite_name": "libero_goal", "task_id": 5, "episode_index": 1, "seed": 59},
    {"suite_name": "libero_goal", "task_id": 6, "episode_index": 1, "seed": 61},
    {"suite_name": "libero_goal", "task_id": 7, "episode_index": 1, "seed": 67},
    {"suite_name": "libero_goal", "task_id": 8, "episode_index": 1, "seed": 71},
    {"suite_name": "libero_goal", "task_id": 9, "episode_index": 1, "seed": 73},
]


def confined(value: str, *, file: bool) -> Path:
    path = Path(value).resolve()
    if path == PERSONAL_ROOT or PERSONAL_ROOT not in path.parents:
        raise ValueError(f"path outside personal root: {path}")
    if file and not path.is_file():
        raise FileNotFoundError(path)
    return path


def strict_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON input must be an object")
    return value


def excluded(relative: Path) -> bool:
    parts = set(relative.parts)
    if parts.intersection({".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}):
        return True
    if relative.suffix in {".pyc", ".pyo"}:
        return True
    return any(part.startswith("tmp") for part in relative.parts)


def add_code_bundle(code_root: Path, bundle: Path) -> None:
    temporary = bundle.with_suffix(bundle.suffix + ".tmp")
    with tarfile.open(temporary, "w:gz", compresslevel=6) as archive:
        for path in sorted(code_root.rglob("*")):
            relative = path.relative_to(code_root)
            if excluded(relative) or not path.is_file():
                continue
            info = archive.gettarinfo(str(path), arcname=str(Path("starVLA") / relative))
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mtime = 0
            with path.open("rb") as handle:
                archive.addfile(info, handle)
    os.replace(temporary, bundle)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--identity-source", required=True)
    parser.add_argument("--preregistration", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--code-bundle", required=True)
    args = parser.parse_args()
    identity_source_path = confined(args.identity_source, file=True)
    preregistration = confined(args.preregistration, file=True)
    output = confined(args.output, file=False)
    bundle = confined(args.code_bundle, file=False)
    if output.exists() or bundle.exists():
        raise FileExistsError("refusing to overwrite policy-lock artifacts")
    source = strict_json(identity_source_path)
    verified, status = verify_policy_identity(source)
    if not verified:
        raise ValueError(f"identity source did not verify: {status}")
    provenance = source["policy_provenance"]
    code_root = confined(str(provenance["policy_code_root"]), file=False)
    if not code_root.is_dir():
        raise ValueError("policy code root is not a directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    add_code_bundle(code_root, bundle)
    lock = {
        "kind": "israc_p026_policy_and_roster_lock_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_before_confirmatory_rollouts": True,
        "identity_sanity_source": str(identity_source_path),
        "identity_sanity_source_sha256": sha256_file(identity_source_path),
        "policy_provenance": provenance,
        "policy_code_bundle": {
            "path": str(bundle),
            "sha256": sha256_file(bundle),
            "size_bytes": bundle.stat().st_size,
        },
        "preregistration": {
            "path": str(preregistration),
            "sha256": sha256_file(preregistration),
        },
        "source_roster": ROSTER,
        "collection": {
            "num_steps_wait": 10,
            "max_steps": 400,
            "host": "127.0.0.1",
            "port": 17778,
        },
        "boundary_selection": {
            "candidate_indices": "1..N-1",
            "priority": "SHA256(source_manifest_sha256 | candidate_index)",
            "count_per_admitted_source": 3,
            "candidate_chunks": 4,
        },
    }
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(
        json.dumps(lock, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, output)
    print(json.dumps({
        "output": str(output),
        "output_sha256": sha256_file(output),
        "code_bundle_sha256": lock["policy_code_bundle"]["sha256"],
        "checkpoint_sha256": provenance["checkpoint_sha256"],
        "roster_count": len(ROSTER),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
