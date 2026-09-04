"""Build a frozen P027-C manifest from the locked P026 evidence packages.

The manifest contains paths and existing P026 hashes only.  It never reads a
WAM score and therefore cannot select examples using the downstream model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SELECTOR_PRIORITY = {
    "israc-contact-subtraction": 0,
    "candidate-contact": 1,
    "random-scene": 2,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(payload: Any) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def personal_path(raw: str, *, must_exist: bool = True) -> Path:
    path = Path(raw).resolve(strict=must_exist)
    text = str(path)
    allowed = ("<PERSONAL_RESEARCH_ROOT>/", "<PERSONAL_RESEARCH_ROOT_ALIAS>/")
    if not text.startswith(allowed):
        raise ValueError(f"path is outside liu_meng personal storage: {path}")
    return path


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


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


def load_result(path: Path) -> dict[str, Any]:
    result = read_json(path)
    if result.get("kind") != "israc_continuous_geom_contact_support_e0":
        raise ValueError(f"unexpected result kind in locked artifact: {path}")
    if result.get("protocol_version") != "P026-v1":
        raise ValueError(f"unexpected protocol in {path}")
    if not result.get("compiler_target_wam_blind"):
        raise ValueError(f"target-WAM blindness is not certified in {path}")
    return result


def block_identity(result: dict[str, Any], block: dict[str, Any]) -> str:
    return canonical_sha256(
        {
            "rollout_sha256": result["rollout_sha256"],
            "arrays_sha256": result["arrays_sha256"],
            "environment_seed": result["environment_seed"],
            "snapshot_sha256": result["snapshot_sha256"],
            "candidate_boundary_step": result["candidate_boundary_step"],
            "candidate_chunk_index": result["candidate_chunk_index"],
            "candidate_sha256": result["candidate_sha256"],
            "factual_action_sha256": result["factual_action_sha256"],
            "parameter_family": block["parameter_metadata"]["family"],
            "geom_ids": sorted(int(value) for value in block["geom_ids"]),
        }
    )


def make_record(
    result_path: Path, result: dict[str, Any], block: dict[str, Any]
) -> dict[str, Any]:
    rollout_path = personal_path(result["rollout"])
    rollout = read_json(rollout_path)
    if sha256_file(rollout_path) != result["rollout_sha256"]:
        raise ValueError(f"source rollout hash mismatch: {rollout_path}")
    if rollout.get("source_schema_version") != "P026-source-v1":
        raise ValueError(f"unexpected source rollout schema: {rollout_path}")
    endpoint_evidence = {
        str(endpoint): {
            "path": str(personal_path(record["path"])),
            "sha256": str(record["sha256"]),
        }
        for endpoint, record in sorted(
            block["endpoint_evidence"].items(), key=lambda item: float(item[0])
        )
    }
    certified_pairs = []
    for pair in block.get("endpoint_strength_curve", []):
        left_value = str(pair["left_value"])
        right_value = str(pair["right_value"])
        left = endpoint_evidence.get(left_value)
        right = endpoint_evidence.get(right_value)
        if left is None or right is None:
            raise ValueError("certified pair references an absent endpoint")
        if left != {
            "path": str(personal_path(pair["left_evidence"]["path"])),
            "sha256": str(pair["left_evidence"]["sha256"]),
        } or right != {
            "path": str(personal_path(pair["right_evidence"]["path"])),
            "sha256": str(pair["right_evidence"]["sha256"]),
        }:
            raise ValueError("certified pair evidence differs from block endpoint evidence")
        if pair.get("certificate_payload", {}).get("failures") != []:
            raise ValueError("endpoint_strength_curve contains a failed certificate")
        certified_pairs.append(
            {
                "left_value": float(pair["left_value"]),
                "right_value": float(pair["right_value"]),
                "left_evidence": left,
                "right_evidence": right,
                "certificate_sha256": str(pair["certificate_sha256"]),
                "measurements": dict(pair["measurements"]),
            }
        )
    certified_alias = bool(block.get("unique_witness", 0))
    if certified_alias != bool(certified_pairs):
        raise ValueError("unique_witness and certified endpoint pairs disagree")
    if int(block.get("certified_endpoint_pairs", -1)) != len(certified_pairs):
        raise ValueError("certified endpoint pair count mismatch")
    repeat = block.get("repeat_evidence")
    return {
        "block_identity": block_identity(result, block),
        "result_path": str(result_path),
        "result_sha256": sha256_file(result_path),
        "rollout_path": str(rollout_path),
        "rollout_sha256": str(result["rollout_sha256"]),
        "arrays_sha256": str(result["arrays_sha256"]),
        "task": str(result.get("task_id", rollout.get("task", "unknown"))),
        "instruction": str(rollout.get("instruction", "")),
        "environment_seed": int(result["environment_seed"]),
        "snapshot_sha256": str(result["snapshot_sha256"]),
        "candidate_chunk_index": int(result["candidate_chunk_index"]),
        "candidate_boundary_step": int(result["candidate_boundary_step"]),
        "candidate_sha256": str(result["candidate_sha256"]),
        "factual_action_sha256": str(result["factual_action_sha256"]),
        "selector": str(result["block_selector"]),
        "selector_seed": int(result["selector_seed"]),
        "parameter_address": str(block["parameter_address"]),
        "parameter_family": str(block["parameter_metadata"]["family"]),
        "engine_field": str(block["parameter_metadata"]["engine_field"]),
        "geom_ids": sorted(int(value) for value in block["geom_ids"]),
        "certified_alias": certified_alias,
        "witness_key": block.get("witness_key"),
        "certified_endpoint_pairs": certified_pairs,
        "factual_observation_repeat_stable": bool(
            block.get("factual_observation_repeat_stable", False)
        ),
        "endpoint_evidence": endpoint_evidence,
        "repeat_evidence": (
            {
                "path": str(personal_path(repeat["path"])),
                "sha256": str(repeat["sha256"]),
            }
            if repeat
            else None
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--formal-dir", required=True)
    parser.add_argument("--analysis", required=True)
    parser.add_argument("--analysis-sha256", required=True)
    parser.add_argument("--matrix-lock", required=True)
    parser.add_argument("--matrix-lock-sha256", required=True)
    parser.add_argument("--compiler-lock", required=True)
    parser.add_argument("--compiler-lock-sha256", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    formal_dir = personal_path(args.formal_dir)
    analysis_path = personal_path(args.analysis)
    matrix_lock_path = personal_path(args.matrix_lock)
    compiler_lock_path = personal_path(args.compiler_lock)
    expected_hashes = {
        analysis_path: args.analysis_sha256,
        matrix_lock_path: args.matrix_lock_sha256,
        compiler_lock_path: args.compiler_lock_sha256,
    }
    for path, expected in expected_hashes.items():
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError(f"locked artifact hash mismatch: {path}: {actual} != {expected}")
    analysis = read_json(analysis_path)
    matrix_lock = read_json(matrix_lock_path)
    compiler_lock = read_json(compiler_lock_path)
    if (
        analysis.get("kind") != "p026_confirmatory_simple_baseline_analysis"
        or analysis.get("protocol_version") != "P026-v1"
        or analysis.get("matrix_complete") is not True
        or analysis.get("semantic_evidence_reverified") is not True
        or analysis.get("decision", {}).get("simple_baseline_gate_passed") is not True
    ):
        raise ValueError("P026 analysis does not authorize P027-C")
    if analysis.get("matrix_run_lock") != {
        "path": str(matrix_lock_path),
        "sha256": args.matrix_lock_sha256,
    }:
        raise ValueError("analysis is not bound to the supplied matrix lock")
    if analysis.get("compiler_lock") != {
        "path": str(compiler_lock_path),
        "sha256": args.compiler_lock_sha256,
    }:
        raise ValueError("analysis is not bound to the supplied compiler lock")
    if (
        matrix_lock.get("kind") != "p026_matrix_run_lock"
        or matrix_lock.get("purpose") != "formal"
        or matrix_lock.get("frozen") is not True
        or int(matrix_lock.get("job_count", -1)) != 189
        or matrix_lock.get("compiler_lock")
        != {"path": str(compiler_lock_path), "sha256": args.compiler_lock_sha256}
    ):
        raise ValueError("invalid or mismatched formal matrix lock")
    if compiler_lock.get("kind") != "p026_compiler_code_lock" or compiler_lock.get("frozen") is not True:
        raise ValueError("invalid compiler lock")
    locked_jobs = list(matrix_lock["jobs"])
    locked_outputs = [personal_path(job["output"]) for job in locked_jobs]
    if len(locked_outputs) != 189 or len(set(locked_outputs)) != 189:
        raise ValueError("formal matrix output set is incomplete or non-unique")
    expected_output_dir = personal_path(matrix_lock["output_directory"])
    if formal_dir != expected_output_dir:
        raise ValueError("formal-dir differs from locked matrix output directory")
    analysis_hashes = dict(analysis.get("artifact_sha256", {}))
    if set(analysis_hashes) != {str(path) for path in locked_outputs}:
        raise ValueError("analysis artifact set differs from the exact locked matrix jobs")
    output = personal_path(args.output, must_exist=False)
    if output.exists():
        raise FileExistsError(output)

    records_by_identity: dict[str, dict[str, Any]] = {}
    selectors_seen: dict[str, set[str]] = {}
    result_count = 0
    for result_path in locked_outputs:
        result_path = personal_path(str(result_path))
        expected_result_hash = analysis_hashes[str(result_path)]
        actual_result_hash = sha256_file(result_path)
        if actual_result_hash != expected_result_hash:
            raise ValueError(f"formal result hash mismatch: {result_path}")
        result = load_result(result_path)
        if result.get("artifact_output_path") != str(result_path):
            raise ValueError(f"artifact path self-reference mismatch: {result_path}")
        if result.get("matrix_run_lock") != {
            "path": str(matrix_lock_path),
            "sha256": args.matrix_lock_sha256,
        }:
            raise ValueError(f"result matrix-lock mismatch: {result_path}")
        if result.get("compiler_lock") != {
            "path": str(compiler_lock_path),
            "sha256": args.compiler_lock_sha256,
        }:
            raise ValueError(f"result compiler-lock mismatch: {result_path}")
        result_count += 1
        for block in result.get("blocks", []):
            record = make_record(result_path, result, block)
            identity = record["block_identity"]
            selectors_seen.setdefault(identity, set()).add(record["selector"])
            incumbent = records_by_identity.get(identity)
            if (
                incumbent is not None
                and incumbent["witness_key"] is not None
                and record["witness_key"] is not None
                and incumbent["witness_key"] != record["witness_key"]
            ):
                raise ValueError(f"conflicting witness keys for physical identity {identity}")
            replace = incumbent is None or (
                (not incumbent["certified_alias"] and record["certified_alias"])
                or (
                    incumbent["certified_alias"] == record["certified_alias"]
                    and (
                        SELECTOR_PRIORITY[record["selector"]], record["selector_seed"]
                    )
                    < (
                        SELECTOR_PRIORITY[incumbent["selector"]],
                        incumbent["selector_seed"],
                    )
                )
            )
            if replace:
                records_by_identity[identity] = record

    records = []
    for identity, record in sorted(records_by_identity.items()):
        record["selectors_seen"] = sorted(selectors_seen[identity])
        records.append(record)
    source_counts: dict[str, int] = {}
    for record in records:
        key = record["rollout_sha256"]
        source_counts[key] = source_counts.get(key, 0) + 1

    if result_count != 189 or not records:
        raise ValueError("locked matrix did not yield a complete non-empty manifest")
    payload = {
        "kind": "p027c_locked_latent_wam_manifest_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "compiler_target_wam_blind": True,
        "selection_uses_downstream_wam": False,
        "formal_dir": str(formal_dir),
        "p026_analysis": {"path": str(analysis_path), "sha256": args.analysis_sha256},
        "p026_matrix_lock": {"path": str(matrix_lock_path), "sha256": args.matrix_lock_sha256},
        "p026_compiler_lock": {"path": str(compiler_lock_path), "sha256": args.compiler_lock_sha256},
        "source_result_count": result_count,
        "deduplicated_block_count": len(records),
        "certified_alias_block_count": sum(
            int(record["certified_alias"]) for record in records
        ),
        "source_counts": dict(sorted(source_counts.items())),
        "records": records,
    }
    payload["records_sha256"] = canonical_sha256(records)
    commit_json_no_clobber(output, payload)
    print(
        json.dumps(
            {
                "output": str(output),
                "source_result_count": result_count,
                "deduplicated_block_count": len(records),
                "certified_alias_block_count": payload["certified_alias_block_count"],
                "source_count": len(source_counts),
                "records_sha256": payload["records_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
