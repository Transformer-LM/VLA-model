#!/usr/bin/env python3
"""Run the frozen P026 compiler matrix with bounded CPU concurrency."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


SELECTOR_SHORT = {
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
        raise ValueError("plan must be a JSON object")
    return value


def gpu_snapshot() -> str:
    commands = (
        ["nvidia-smi", "--query-gpu=index,memory.used,utilization.gpu", "--format=csv,noheader"],
        ["nvidia-smi", "--query-compute-apps=gpu_uuid,pid,process_name,used_memory", "--format=csv,noheader"],
    )
    rows = []
    for command in commands:
        result = subprocess.run(command, text=True, capture_output=True, check=True)
        rows.append(result.stdout.strip())
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    parser.add_argument("--plan-sha256", required=True)
    parser.add_argument("--compiler-lock", required=True)
    parser.add_argument("--compiler-lock-sha256", required=True)
    parser.add_argument("--matrix-run-lock", required=True)
    parser.add_argument("--matrix-run-lock-sha256", required=True)
    parser.add_argument("--launch-record", required=True)
    parser.add_argument("--launch-record-sha256", required=True)
    parser.add_argument("--implementation-root", required=True)
    parser.add_argument("--support-code", required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        raise ValueError("workers must be between one and four")

    plan_path = Path(args.plan).resolve()
    if sha256_file(plan_path) != args.plan_sha256:
        raise ValueError("frozen boundary-plan hash mismatch")
    plan = read_json(plan_path)
    if plan.get("kind") != "p026_outcome_blind_boundary_plan" or (
        plan.get("frozen_before_compiler_execution") is not True
    ):
        raise ValueError("boundary plan is not a frozen P026 plan")
    compiler_lock_path = Path(args.compiler_lock).resolve()
    if sha256_file(compiler_lock_path) != args.compiler_lock_sha256:
        raise ValueError("compiler lock hash mismatch")
    compiler_lock = read_json(compiler_lock_path)
    if compiler_lock.get("kind") != "p026_compiler_code_lock" or (
        compiler_lock.get("frozen") is not True
    ):
        raise ValueError("compiler lock is not frozen")
    if compiler_lock.get("boundary_plan", {}).get("sha256") != args.plan_sha256:
        raise ValueError("compiler lock is bound to another boundary plan")
    for reference in compiler_lock.get("files", []):
        path = Path(str(reference["path"])).resolve()
        if sha256_file(path) != str(reference["sha256"]):
            raise ValueError(f"locked code drift before matrix launch: {reference['role']}")
    for label in ("preregistration", "policy_lock"):
        reference = compiler_lock.get(label)
        if not isinstance(reference, dict):
            raise ValueError(f"compiler lock lacks {label}")
        path = Path(str(reference["path"])).resolve()
        if sha256_file(path) != str(reference["sha256"]):
            raise ValueError(f"locked {label} drift before matrix launch")
    amendments = compiler_lock.get("protocol_amendments")
    if not isinstance(amendments, list) or [row.get("version") for row in amendments] != [
        "v1", "v2"
    ]:
        raise ValueError("compiler lock lacks the exact v1/v2 amendment chain")
    amendment_paths = []
    for reference in amendments:
        path = Path(str(reference["path"])).resolve()
        if sha256_file(path) != str(reference["sha256"]):
            raise ValueError(
                f"locked protocol amendment {reference['version']} drift before matrix launch"
            )
        amendment_paths.append(path)
    if (
        [path.name for path in amendment_paths]
        != ["P026_PROTOCOL_AMENDMENT.md", "P026_PROTOCOL_AMENDMENT_V2.md"]
        or len(set(amendment_paths)) != 2
        or len({str(row.get("sha256")) for row in amendments}) != 2
        or amendments[1].get("predecessor_sha256") != amendments[0].get("sha256")
        or str(amendments[0].get("sha256"))
        not in amendment_paths[1].read_text(encoding="utf-8")
    ):
        raise ValueError("protocol amendment chain is aliased or not predecessor-pinned")
    compiler_reference = {
        "path": str(compiler_lock_path), "sha256": args.compiler_lock_sha256
    }
    matrix_lock_path = Path(args.matrix_run_lock).resolve()
    if sha256_file(matrix_lock_path) != args.matrix_run_lock_sha256:
        raise ValueError("matrix-run lock hash mismatch")
    matrix_lock = read_json(matrix_lock_path)
    if (
        matrix_lock.get("kind") != "p026_matrix_run_lock"
        or matrix_lock.get("frozen") is not True
        or matrix_lock.get("compiler_lock") != compiler_reference
        or matrix_lock.get("boundary_plan") != {
            "path": str(plan_path), "sha256": args.plan_sha256
        }
    ):
        raise ValueError("matrix-run lock chain is invalid")
    jobs_payload = matrix_lock.get("jobs")
    if not isinstance(jobs_payload, list) or int(matrix_lock.get("job_count", -1)) != len(
        jobs_payload
    ):
        raise ValueError("matrix-run job list is invalid")
    output_dir = Path(str(matrix_lock["output_directory"])).resolve()
    if not output_dir.is_dir():
        raise ValueError("matrix-run output directory is missing")
    launch_path = Path(args.launch_record).resolve()
    if sha256_file(launch_path) != args.launch_record_sha256:
        raise ValueError("launch record hash mismatch")
    launch_record = read_json(launch_path)
    launch_reference = {
        "path": str(launch_path), "sha256": args.launch_record_sha256
    }
    if (
        launch_record.get("kind") != "p026_immutable_launch_record"
        or launch_record.get("boundary_plan") != matrix_lock.get("boundary_plan")
        or launch_record.get("compiler_lock") != compiler_reference
        or launch_record.get("matrix_run_lock") != {
            "path": str(matrix_lock_path), "sha256": args.matrix_run_lock_sha256
        }
        or Path(str(launch_record.get("output_directory"))).resolve() != output_dir
        or launch_record.get("output_directory_entries_at_launch") != []
        or launch_record.get("no_formal_cell_started_before_record") is not True
    ):
        raise ValueError("launch record does not bind the current empty matrix run")
    marker = output_dir / "MATRIX_RUN_STARTED.json"
    marker_payload = {
        "kind": "p026_matrix_run_start_marker",
        "matrix_run_lock": {
            "path": str(matrix_lock_path), "sha256": args.matrix_run_lock_sha256
        },
        "compiler_lock": compiler_reference,
        "launch_record": launch_reference,
    }
    if marker.exists():
        if read_json(marker) != marker_payload:
            raise ValueError("matrix-run resume marker differs from current lock chain")
    else:
        if any(output_dir.iterdir()):
            raise ValueError("matrix-run output directory was not empty at first launch")
        temporary_marker = marker.with_suffix(f".tmp.{os.getpid()}")
        temporary_marker.write_text(
            json.dumps(marker_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        os.replace(temporary_marker, marker)
    planned = {
        (str(row["source_rollout_sha256"]), int(row["candidate_index"])): row
        for row in plan["boundaries"]
    }
    jobs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    seen_outputs: set[str] = set()
    for row in jobs_payload:
        key = (str(row.get("source_rollout_sha256")), int(row.get("candidate_index", -1)))
        if key not in planned:
            raise ValueError("matrix-run job boundary escapes frozen plan")
        boundary = planned[key]
        if (
            row.get("selector") not in plan["selectors"]
            or int(row.get("selector_seed", -1)) not in {
                int(value) for value in plan["selector_seeds"]
            }
            or str(Path(str(row.get("source_rollout"))).resolve())
            != str(Path(str(boundary["source_rollout"])).resolve())
            or str(Path(str(row.get("source_admission"))).resolve())
            != str(Path(str(boundary["source_admission"])).resolve())
            or row.get("source_admission_sha256")
            != boundary["source_admission_sha256"]
        ):
            raise ValueError("matrix-run job fields differ from frozen boundary plan")
        output_path = Path(str(row.get("output"))).resolve()
        log_path = Path(str(row.get("log"))).resolve()
        if output_path.parent != output_dir or log_path.parent != output_dir or (
            str(output_path) in seen_outputs
        ):
            raise ValueError("matrix-run output paths are non-unique or escape output directory")
        seen_outputs.add(str(output_path))
        jobs.append((boundary, row))

    implementation = Path(args.implementation_root).resolve()
    support = Path(args.support_code).resolve()
    # Preserve the venv entry path. Resolving it follows the symlink to
    # /usr/bin/python and silently drops the personal environment's sys.path.
    python = Path(args.python)
    env = dict(os.environ)
    env.update({
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": f"{implementation}:<PERSONAL_RESEARCH_ROOT>/workspace/third_party/LIBERO",
        "LIBERO_CONFIG_PATH": "<PERSONAL_RESEARCH_ROOT>/config/libero",
        "MUJOCO_GL": "osmesa",
        "PYOPENGL_PLATFORM": "osmesa",
        "LD_LIBRARY_PATH": (
            "<PERSONAL_RESEARCH_ROOT>/renderer-runtime/osmesa/prefix/usr/lib/x86_64-linux-gnu:"
            "<PERSONAL_RESEARCH_ROOT>/renderer-runtime/osmesa/prefix/lib/x86_64-linux-gnu"
        ),
        "MESA_SHADER_CACHE_DIR": "<PERSONAL_RESEARCH_ROOT>/renderer-runtime/osmesa/cache",
        "XDG_CACHE_HOME": "<PERSONAL_RESEARCH_ROOT>/renderer-runtime/osmesa/cache",
    })

    def run_one(job: tuple[dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
        boundary, locked_job = job
        selector = str(locked_job["selector"])
        seed = int(locked_job["selector_seed"])
        tag = (
            f"t{int(boundary['task_id'])}_e{int(boundary['episode_index'])}_"
            f"c{int(boundary['candidate_index']):02d}_{SELECTOR_SHORT[selector]}_seed{seed}"
        )
        output = Path(str(locked_job["output"])).resolve()
        log = Path(str(locked_job["log"])).resolve()
        if output.exists():
            verification = subprocess.run(
                [
                    str(python), str(implementation / "verify_p025_manifest.py"),
                    "--manifest", str(output),
                    "--allowed-root", "<PERSONAL_RESEARCH_ROOT>",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
            if verification.returncode != 0:
                raise RuntimeError(
                    f"existing output fails verification for {tag}: {verification.stderr}"
                )
            existing_record = read_json(output)
            if existing_record.get("compiler_lock") != compiler_reference or (
                existing_record.get("matrix_run_lock") != {
                    "path": str(matrix_lock_path),
                    "sha256": args.matrix_run_lock_sha256,
                }
            ):
                raise RuntimeError("existing output belongs to another lock chain")
            return {"status": "verified_existing", "output": str(output)}
        if log.exists():
            raise RuntimeError(
                f"locked cell has a prior failed/interrupted log and cannot be retried: {log}"
            )
        snapshot = gpu_snapshot()
        command = [
            str(python), str(implementation / "certify_continuous_contact_support.py"),
            "--rollout", str(boundary["source_rollout"]),
            "--source-admission-report", str(boundary["source_admission"]),
            "--compiler-lock", str(compiler_lock_path),
            "--matrix-run-lock", str(matrix_lock_path),
            "--support-code", str(support),
            "--output", str(output),
            "--candidate-index", str(int(boundary["candidate_index"])),
            "--candidate-chunks", str(int(plan["candidate_chunks"])),
            "--family", str(plan["physical_family"]),
            "--block-selector", selector,
            "--selector-seed", str(seed),
            "--max-selected-blocks", str(int(plan["max_selected_blocks"])),
            "--height", "64", "--width", "64",
        ]
        compiler = subprocess.run(command, env=env, text=True, capture_output=True)
        verification = None
        if compiler.returncode == 0:
            verification = subprocess.run(
                [
                    str(python), str(implementation / "verify_p025_manifest.py"),
                    "--manifest", str(output),
                    "--allowed-root", "<PERSONAL_RESEARCH_ROOT>",
                ],
                env=env,
                text=True,
                capture_output=True,
            )
        log_payload = (
            "GPU_SNAPSHOT_BEFORE_CPU_COMPILER\n" + snapshot + "\n"
            + "COMMAND\n" + json.dumps(command) + "\n"
            + "COMPILER_STDOUT\n" + compiler.stdout
            + "\nCOMPILER_STDERR\n" + compiler.stderr
        )
        if verification is not None:
            log_payload += (
                "\nVERIFIER_STDOUT\n" + verification.stdout
                + "\nVERIFIER_STDERR\n" + verification.stderr
            )
        temporary = log.with_suffix(log.suffix + f".tmp.{os.getpid()}")
        temporary.write_text(log_payload, encoding="utf-8")
        os.replace(temporary, log)
        if compiler.returncode != 0:
            raise RuntimeError(f"compiler failed for {tag}; see {log}")
        if verification is None or verification.returncode != 0:
            raise RuntimeError(f"verifier failed for {tag}; see {log}")
        return {"status": "completed", "output": str(output)}

    completed: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_one, job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            completed.append(result)
            print(json.dumps(result, sort_keys=True), flush=True)
    print(json.dumps({
        "plan_sha256": args.plan_sha256,
        "compiler_lock_sha256": args.compiler_lock_sha256,
        "matrix_run_lock_sha256": args.matrix_run_lock_sha256,
        "launch_record_sha256": args.launch_record_sha256,
        "job_count": len(jobs),
        "completed_or_existing": len(completed),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
