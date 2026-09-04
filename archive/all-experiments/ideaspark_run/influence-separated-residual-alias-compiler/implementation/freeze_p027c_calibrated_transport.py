"""Freeze a leakage-resistant P027-C residual-transport calibration run."""

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
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--checkpoint-sha256", required=True)
    parser.add_argument("--support", required=True)
    parser.add_argument("--support-sha256", required=True)
    parser.add_argument("--evaluator", required=True)
    parser.add_argument("--evaluator-sha256", required=True)
    parser.add_argument("--eval-source-sha256", required=True)
    parser.add_argument("--eval-candidate-indices", nargs="+", type=int, required=True)
    parser.add_argument("--alpha-grid", nargs="+", type=float, required=True)
    parser.add_argument("--decay-grid", nargs="+", type=float, required=True)
    parser.add_argument("--residual-window", type=int, default=8)
    parser.add_argument("--minimum-relative-control-improvement", type=float, default=0.01)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--result", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    files = {
        "manifest": (personal_path(args.manifest), args.manifest_sha256),
        "checkpoint": (personal_path(args.checkpoint), args.checkpoint_sha256),
        "support": (personal_path(args.support), args.support_sha256),
        "evaluator": (personal_path(args.evaluator), args.evaluator_sha256),
    }
    for label, (path, expected) in files.items():
        if sha256_file(path) != expected:
            raise ValueError(f"{label} hash mismatch")
    result = personal_path(args.result, must_exist=False)
    output = personal_path(args.output, must_exist=False)
    if result == output or result.exists() or output.exists():
        raise FileExistsError("result or run-lock output is occupied")
    manifest = json.loads(files["manifest"][0].read_text(encoding="utf-8"))
    if (
        manifest.get("kind") != "p027c_locked_latent_wam_manifest_v1"
        or manifest.get("compiler_target_wam_blind") is not True
        or manifest.get("selection_uses_downstream_wam") is not False
        or canonical_sha256(manifest.get("records")) != manifest.get("records_sha256")
    ):
        raise ValueError("manifest integrity or blindness check failed")
    source_records = [
        record
        for record in manifest["records"]
        if record["rollout_sha256"] == args.eval_source_sha256
    ]
    available_indices = {int(record["candidate_chunk_index"]) for record in source_records}
    eval_indices = sorted(set(args.eval_candidate_indices))
    if (
        not source_records
        or len(eval_indices) != 3
        or not set(eval_indices) <= available_indices
    ):
        raise ValueError("held-out source/candidate selection is absent from manifest")
    alphas = sorted(set(args.alpha_grid))
    decays = sorted(set(args.decay_grid))
    if (
        alphas != args.alpha_grid
        or decays != args.decay_grid
        or not alphas
        or alphas[0] != 0.0
        or any(not math.isfinite(value) or value < 0.0 for value in alphas)
        or any(not math.isfinite(value) or not 0.0 <= value <= 1.0 for value in decays)
        or args.residual_window < 1
        or not math.isfinite(args.minimum_relative_control_improvement)
        or args.minimum_relative_control_improvement <= 0.0
    ):
        raise ValueError("invalid calibration configuration")

    payload = {
        "kind": "p027c_calibrated_transport_run_lock_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "frozen": True,
        "frozen_before_calibration_outcomes": True,
        "selection_uses_downstream_heldout_outcomes": False,
        "manifest": {"path": str(files["manifest"][0]), "sha256": args.manifest_sha256},
        "checkpoint": {"path": str(files["checkpoint"][0]), "sha256": args.checkpoint_sha256},
        "support": {"path": str(files["support"][0]), "sha256": args.support_sha256},
        "evaluator": {"path": str(files["evaluator"][0]), "sha256": args.evaluator_sha256},
        "eval_source_sha256": args.eval_source_sha256,
        "eval_candidate_indices": eval_indices,
        "eval_selection_rule": (
            f"All three candidate boundaries {eval_indices} already present for the "
            "frozen held-out rollout source; every boundary is reported separately."
        ),
        "alpha_grid": alphas,
        "decay_grid": decays,
        "residual_window": args.residual_window,
        "minimum_relative_control_improvement": args.minimum_relative_control_improvement,
        "calibration_rule": (
            "Choose alpha and decay only on non-held-out-source endpoints where both "
            "factual and candidate mechanisms are active, using equal source weighting."
        ),
        "heldout_gate_rule": (
            "Alias-specific harm is interpretable only per exact candidate boundary and "
            "only if held-out ordinary-overlap controls also benefit from the calibrated correction."
        ),
        "device": args.device,
        "output": str(result),
    }
    commit_json_no_clobber(output, payload)
    print(json.dumps({"output": str(output), "sha256": sha256_file(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
