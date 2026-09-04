"""Freeze one outcome-blind P027-C latent-WAM E0 invocation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def personal_path(raw: str, *, must_exist: bool = True) -> Path:
    path = Path(raw).resolve(strict=must_exist)
    if not str(path).startswith(
        ("<PERSONAL_RESEARCH_ROOT>/", "<PERSONAL_RESEARCH_ROOT_ALIAS>/")
    ):
        raise ValueError(f"path is outside liu_meng personal storage: {path}")
    return path


def canonical_sha256(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    ).hexdigest()


def commit_json_no_clobber(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    try:
        with temporary.open("xb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--runner", required=True)
    parser.add_argument("--runner-sha256", required=True)
    parser.add_argument("--eval-source-sha256", required=True)
    parser.add_argument("--eval-selection-rule", required=True)
    parser.add_argument("--result", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--width", type=int, default=256)
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--residual-window", type=int, default=8)
    parser.add_argument("--residual-decay", type=float, default=0.8)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--output", required=True, help="Run-lock output path.")
    args = parser.parse_args()

    manifest_path = personal_path(args.manifest)
    runner_path = personal_path(args.runner)
    result_path = personal_path(args.result, must_exist=False)
    checkpoint_path = personal_path(args.checkpoint, must_exist=False)
    output = personal_path(args.output, must_exist=False)
    if len({result_path, checkpoint_path, output}) != 3:
        raise ValueError("run lock, result, and checkpoint paths must be distinct")
    if any(path.exists() for path in (result_path, checkpoint_path, output)):
        raise FileExistsError("a frozen output path already exists")
    if sha256_file(manifest_path) != args.manifest_sha256:
        raise ValueError("manifest hash mismatch")
    if sha256_file(runner_path) != args.runner_sha256:
        raise ValueError("runner hash mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("kind") != "p027c_locked_latent_wam_manifest_v1"
        or manifest.get("compiler_target_wam_blind") is not True
        or manifest.get("selection_uses_downstream_wam") is not False
        or canonical_sha256(manifest.get("records")) != manifest.get("records_sha256")
    ):
        raise ValueError("manifest integrity or blindness lock failed")
    if args.eval_source_sha256 not in manifest.get("source_counts", {}):
        raise ValueError("eval source is absent from manifest")
    source_records = [
        record
        for record in manifest["records"]
        if record["rollout_sha256"] == args.eval_source_sha256
    ]
    candidate_indices = sorted(
        {int(record["candidate_chunk_index"]) for record in source_records}
    )
    if not source_records or not candidate_indices or not args.eval_selection_rule.strip():
        raise ValueError("eval source selection provenance is incomplete")
    if (
        args.epochs < 1
        or args.batch_size < 1
        or args.residual_window < 1
        or args.width < 1
        or args.depth < 1
        or not math.isfinite(args.learning_rate)
        or args.learning_rate <= 0.0
        or not math.isfinite(args.residual_decay)
        or not 0.0 <= args.residual_decay <= 1.0
    ):
        raise ValueError("invalid run hyperparameters")

    payload = {
        "kind": "p027c_latent_wam_run_lock_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "frozen": True,
        "frozen_before_target_wam_load": True,
        "selection_uses_downstream_wam": False,
        "manifest": {"path": str(manifest_path), "sha256": args.manifest_sha256},
        "runner": {"path": str(runner_path), "sha256": args.runner_sha256},
        "eval_source_sha256": args.eval_source_sha256,
        "eval_source_candidate_indices": candidate_indices,
        "eval_source_selection_rule": args.eval_selection_rule.strip(),
        "artifacts": {
            "result": str(result_path),
            "checkpoint": str(checkpoint_path),
        },
        "config": {
            "seed": args.seed,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": args.learning_rate,
            "width": args.width,
            "depth": args.depth,
            "residual_window": args.residual_window,
            "residual_decay": args.residual_decay,
            "device": args.device,
        },
        "failure_recovery": (
            "A checkpoint without the committed result JSON is an incomplete orphan; "
            "it must never be reused or interpreted as a completed run."
        ),
    }
    commit_json_no_clobber(output, payload)
    print(
        json.dumps(
            {"output": str(output), "sha256": sha256_file(output)}, sort_keys=True
        )
    )


if __name__ == "__main__":
    main()
