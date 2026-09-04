"""Exact, fail-closed lifecycle wrapper for the V2-007 engineering canary."""

from __future__ import annotations

import argparse
import json
import math
import os
import signal
import socket
import subprocess
import sys
import time
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .canonical import atomic_write_canonical_json, canonical_json_sha256, file_sha256
from .checkpoint import CHECKPOINT_SHA256
from .constants import (
    ARTIFACT_ROOT,
    CANARY_EXPECTED_WALL_SECONDS,
    CANARY_HUNG_TIMEOUT_SECONDS,
    CANARY_ROLE_SEED,
    CHECKPOINT_KEYSET_SHA256,
    ISOLATED_WORKSPACE,
    RUNTIME_CACHE,
    RUNTIME_CONFIG,
    RUNTIME_CUDA_CACHE,
    RUNTIME_HF_HOME,
    RUNTIME_HOME,
    RUNTIME_TMP,
    RUNTIME_TORCH_EXTENSIONS,
    RUNTIME_TORCH_HOME,
    RUNTIME_WANDB,
    TRAIN_PYTHON,
)
from .filesystem import PersonalRootGuard, enforce_private_umask
from .gpu_guard import (
    GPUGuardError,
    GPUReservation,
    GPUSnapshot,
    GPUState,
    assert_owned_gpu_binding,
    assert_recorded_gpu_pids_absent,
    assert_second_snapshot,
    choose_idle_gpu,
    pids_in_process_group,
    proc_start_ticks,
    snapshot_sha256,
    take_snapshot,
)
from .provenance import CanaryProvenance, verify_canary_provenance


class LaunchLifecycleError(RuntimeError):
    pass


PRE_COMPLETION_SUCCESS_FILES = frozenset(
    {"launch.json", "stdout.log", "stderr.log", "child_bound.json", "canary_metrics.json"}
)
FINAL_SUCCESS_FILES = PRE_COMPLETION_SUCCESS_FILES | frozenset({"completion.json", "terminal_manifest.json"})


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def exact_canary_command(checkpoint_step: int) -> tuple[str, ...]:
    if checkpoint_step not in CHECKPOINT_SHA256:
        raise LaunchLifecycleError(f"Unsupported canary checkpoint step: {checkpoint_step}")
    return (
        str(TRAIN_PYTHON),
        "-m",
        "pgr_audit.engineering_canary",
        "--checkpoint-step",
        str(checkpoint_step),
    )


def _open_exclusive(path: Path):
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    return os.fdopen(descriptor, "wb", closefd=True)


def _private_environment(
    selected: GPUState,
    launch_uuid: str,
    output: Path,
    provenance: CanaryProvenance,
) -> dict[str, str]:
    environment = os.environ.copy()
    for key in tuple(environment):
        upper = key.upper()
        if upper in {
            "PYTHONPATH",
            "PYTHONHOME",
            "CUDA_VISIBLE_DEVICES",
            "HOME",
            "TMPDIR",
            "TMP",
            "TEMP",
            "XDG_CACHE_HOME",
            "XDG_CONFIG_HOME",
            "HF_HOME",
            "TORCH_HOME",
            "TORCH_EXTENSIONS_DIR",
            "CUDA_CACHE_PATH",
            "WANDB_DIR",
            "WANDB_MODE",
            "WANDB_API_KEY",
            "PYTHONHASHSEED",
            "CUBLAS_WORKSPACE_CONFIG",
        } or upper.endswith("_PROXY"):
            environment.pop(key, None)
    environment.update(
        {
            "PATH": "<PERSONAL_RESEARCH_ROOT>/conda/envs/cf-dynalign/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "CUDA_DEVICE_ORDER": "PCI_BUS_ID",
            "CUDA_VISIBLE_DEVICES": selected.hardware_uuid,
            "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
            "PYTHONHASHSEED": str(CANARY_ROLE_SEED),
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "WANDB_MODE": "offline",
            "PYTHONNOUSERSITE": "1",
            "TOKENIZERS_PARALLELISM": "false",
            "HOME": str(RUNTIME_HOME),
            "TMPDIR": str(RUNTIME_TMP),
            "XDG_CACHE_HOME": str(RUNTIME_CACHE),
            "XDG_CONFIG_HOME": str(RUNTIME_CONFIG),
            "HF_HOME": str(RUNTIME_HF_HOME),
            "TORCH_HOME": str(RUNTIME_TORCH_HOME),
            "TORCH_EXTENSIONS_DIR": str(RUNTIME_TORCH_EXTENSIONS),
            "CUDA_CACHE_PATH": str(RUNTIME_CUDA_CACHE),
            "WANDB_DIR": str(RUNTIME_WANDB),
            "NO_PROXY": "*",
            "PGR_SELECTED_PHYSICAL_INDEX": str(selected.physical_index),
            "PGR_SELECTED_GPU_UUID": selected.hardware_uuid,
            "PGR_LAUNCH_UUID": launch_uuid,
            "PGR_OUTPUT_DIR": str(output),
            "PGR_APPROVAL_SHA256": provenance.approval_sha256,
            "PGR_OVERLAY_SOURCE_SHA256": provenance.overlay_source_sha256,
            "PGR_ENVIRONMENT_LOCK_SHA256": provenance.environment_lock_sha256,
            "PGR_SANITIZED_CONFIG_SHA256": provenance.sanitized_config_sha256,
            "PGR_REVIEW_RESPONSE_SHA256": provenance.review_response_sha256,
        }
    )
    return environment


def validate_private_environment(environment: dict[str, str], selected_uuid: str) -> None:
    expected = {
        "CUDA_VISIBLE_DEVICES": selected_uuid,
        "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
        "PYTHONHASHSEED": str(CANARY_ROLE_SEED),
        "HOME": str(RUNTIME_HOME),
        "TMPDIR": str(RUNTIME_TMP),
        "XDG_CACHE_HOME": str(RUNTIME_CACHE),
        "XDG_CONFIG_HOME": str(RUNTIME_CONFIG),
        "HF_HOME": str(RUNTIME_HF_HOME),
        "TORCH_HOME": str(RUNTIME_TORCH_HOME),
        "TORCH_EXTENSIONS_DIR": str(RUNTIME_TORCH_EXTENSIONS),
        "CUDA_CACHE_PATH": str(RUNTIME_CUDA_CACHE),
        "WANDB_MODE": "offline",
        "WANDB_DIR": str(RUNTIME_WANDB),
    }
    mismatches = {key: (value, environment.get(key)) for key, value in expected.items() if environment.get(key) != value}
    if mismatches or "PYTHONPATH" in environment or "PYTHONHOME" in environment:
        raise LaunchLifecycleError(f"Private deterministic environment mismatch: {mismatches}")


def _validate_handshake(
    path: Path,
    *,
    process_pid: int,
    pgid: int,
    selected_index: int,
    selected_uuid: str,
    launch_uuid: str,
) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "pid": process_pid,
        "pgid": pgid,
        "visible_device_count": 1,
        "cuda_visible_devices": selected_uuid,
        "selected_physical_index": selected_index,
        "selected_gpu_uuid": selected_uuid,
        "observed_gpu_uuid": selected_uuid,
        "launch_uuid": launch_uuid,
    }
    mismatches = {key: (expected_value, value.get(key)) for key, expected_value in expected.items() if value.get(key) != expected_value}
    if mismatches:
        raise LaunchLifecycleError(f"Child GPU handshake mismatch: {mismatches}")
    return value


def _assert_no_foreign_gpu_context(snapshot: GPUSnapshot, selected: GPUState, owned_pids: frozenset[int]) -> None:
    selected_compute = set(snapshot.by_index(selected.physical_index).compute_pids)
    foreign = selected_compute - set(owned_pids)
    if foreign:
        raise GPUGuardError(f"Foreign PIDs joined reserved GPU before binding: {sorted(foreign)}")
    for state in snapshot.states:
        if state.physical_index != selected.physical_index and set(state.compute_pids) & set(owned_pids):
            raise GPUGuardError(f"Owned PID appeared on unselected GPU {state.physical_index}")


def _capture_identities(pids: frozenset[int], identities: dict[int, int]) -> None:
    for pid in pids:
        try:
            ticks = proc_start_ticks(pid)
        except (FileNotFoundError, PermissionError, IndexError, ValueError):
            continue
        prior = identities.get(pid)
        if prior is not None and prior != ticks:
            raise LaunchLifecycleError(f"PID {pid} start-tick identity changed during launch")
        identities[pid] = ticks


def _terminate_verified_live_group(process: subprocess.Popen[bytes], pgid: int, leader_start_ticks: int) -> None:
    if process.poll() is not None:
        return
    if os.getpgid(process.pid) != pgid or proc_start_ticks(process.pid) != leader_start_ticks:
        raise LaunchLifecycleError("Refusing to signal an unverified or reused process group")
    os.killpg(pgid, signal.SIGTERM)
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        if process.poll() is None:
            if os.getpgid(process.pid) != pgid or proc_start_ticks(process.pid) != leader_start_ticks:
                raise LaunchLifecycleError("Process identity changed before SIGKILL")
            os.killpg(pgid, signal.SIGKILL)
            process.wait(timeout=10)


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def validate_canary_metrics(value: dict[str, Any], checkpoint_step: int, provenance: CanaryProvenance) -> None:
    exact = {
        "canary_kind": "engineering-only-no-scientific-target",
        "checkpoint_step": checkpoint_step,
        "scientific_examples_read": 0,
        "scientific_outcomes_read": 0,
        "robot_trials": 0,
        "paid_cost_usd": 0.0,
        "synthetic_examples": 1,
        "approval_sha256": provenance.approval_sha256,
        "overlay_source_sha256": provenance.overlay_source_sha256,
        "environment_lock_sha256": provenance.environment_lock_sha256,
        "sanitized_config_sha256": provenance.sanitized_config_sha256,
        "review_response_sha256": provenance.review_response_sha256,
    }
    mismatches = {key: (expected, value.get(key)) for key, expected in exact.items() if value.get(key) != expected}
    parity = value.get("interface_parity", {})
    host = value.get("host_audit", {})
    checkpoint = host.get("checkpoint", {}) if isinstance(host, dict) else {}
    for key, expected in {
        "hidden_size": 2560,
        "action_horizon": 8,
        "trainable_parameter_count": 0,
    }.items():
        if host.get(key) != expected:
            mismatches[f"host_audit.{key}"] = (expected, host.get(key))
    if checkpoint.get("sha256") != provenance.checkpoint_sha256:
        mismatches["host_audit.checkpoint.sha256"] = (
            provenance.checkpoint_sha256,
            checkpoint.get("sha256"),
        )
    if checkpoint.get("key_count") != 730 or checkpoint.get("keyset_sha256") != CHECKPOINT_KEYSET_SHA256:
        mismatches["host_audit.checkpoint.keyset"] = (
            (730, CHECKPOINT_KEYSET_SHA256),
            (checkpoint.get("key_count"), checkpoint.get("keyset_sha256")),
        )
    determinism = value.get("determinism", {})
    for key, expected in {
        "cublas_workspace_config": ":4096:8",
        "cudnn_benchmark": False,
        "cudnn_deterministic": True,
        "deterministic_algorithms": True,
        "matmul_precision": "highest",
        "pythonhashseed": str(CANARY_ROLE_SEED),
        "tf32_cudnn": False,
        "tf32_matmul": False,
    }.items():
        if determinism.get(key) != expected:
            mismatches[f"determinism.{key}"] = (expected, determinism.get(key))
    threshold = parity.get("threshold")
    for field in (
        "direct_vs_interface_max_abs",
        "interface_repeat_max_abs",
        "in_memory_cache_roundtrip_max_abs",
    ):
        if not _finite_number(parity.get(field)) or not _finite_number(threshold) or parity[field] > threshold:
            mismatches[f"interface_parity.{field}"] = (f"finite <= {threshold}", parity.get(field))
    for field in ("max_memory_allocated_bytes", "max_memory_reserved_bytes", "model_load_seconds", "parity_seconds"):
        if not _finite_number(value.get(field)) or value[field] < 0:
            mismatches[field] = ("finite nonnegative", value.get(field))
    if mismatches:
        raise LaunchLifecycleError(f"Canary metrics validation failed: {mismatches}")


def _file_hashes(output: Path, names: set[str] | frozenset[str]) -> dict[str, str]:
    return {name: file_sha256(output / name) for name in sorted(names)}


def _validate_exact_regular_files(output: Path, expected: frozenset[str]) -> None:
    observed: set[str] = set()
    for entry in output.iterdir():
        if entry.is_symlink() or not entry.is_file():
            raise LaunchLifecycleError(f"Non-regular output is forbidden: {entry}")
        observed.add(entry.name)
    if observed != set(expected):
        raise LaunchLifecycleError(f"Output set mismatch: expected={sorted(expected)}, observed={sorted(observed)}")


def _seal_output(output: Path, *, success: bool) -> None:
    expected = FINAL_SUCCESS_FILES if success else frozenset(path.name for path in output.iterdir())
    _validate_exact_regular_files(output, expected)
    for path in output.iterdir():
        os.chmod(path, 0o400)
    os.chmod(output, 0o500)


def run_guarded_canary(checkpoint_step: int) -> Path:
    enforce_private_umask()
    guard = PersonalRootGuard()
    guard.verify_root()
    guard.require_existing(ISOLATED_WORKSPACE, regular=False)
    for directory in (
        ARTIFACT_ROOT,
        RUNTIME_HOME,
        RUNTIME_TMP,
        RUNTIME_CACHE,
        RUNTIME_CONFIG,
        RUNTIME_HF_HOME,
        RUNTIME_TORCH_HOME,
        RUNTIME_TORCH_EXTENSIONS,
        RUNTIME_CUDA_CACHE,
        RUNTIME_WANDB,
    ):
        guard.require_existing(directory, regular=False)

    # This may hash large model inputs, inspect the exact clean source and check
    # the environment. It deliberately runs before the first GPU snapshot.
    provenance = verify_canary_provenance(checkpoint_step)
    command = exact_canary_command(checkpoint_step)
    command_hash = canonical_json_sha256(list(command))
    output_parent = ARTIFACT_ROOT / "engineering-canary"
    output_parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    guard.require_existing(output_parent, regular=False)
    output = guard.create_uuid_directory(output_parent, label=f"step{checkpoint_step}")

    launch_uuid = str(uuid.uuid4())
    reservation: GPUReservation | None = None
    process: subprocess.Popen[bytes] | None = None
    selected: GPUState | None = None
    pgid: int | None = None
    leader_start_ticks: int | None = None
    recorded_identities: dict[int, int] = {}
    first: GPUSnapshot | None = None
    second: GPUSnapshot | None = None
    binding_snapshot: GPUSnapshot | None = None
    heartbeat_snapshots: list[dict[str, Any]] = []
    post_snapshot: GPUSnapshot | None = None
    release_path: Path | None = None
    release_sha256: str | None = None
    release_payload: dict[str, Any] | None = None
    reservation_initial_sha256: str | None = None
    reservation_original_path: Path | None = None
    binding_verified = False
    exit_code: int | None = None
    lifecycle_error: str | None = None
    stop_reason = "not-started"
    started_utc = _utc_now()
    started_monotonic = time.monotonic()
    child_started_monotonic: float | None = None
    child_ended_monotonic: float | None = None
    stdout_handle = None
    stderr_handle = None

    try:
        first = take_snapshot()
        selected = choose_idle_gpu(first)
        reservation = GPUReservation(state=selected, launch_uuid=launch_uuid, logical_run_id="V2-007")
        reservation_original_path = reservation.acquire()
        reservation_initial_sha256 = file_sha256(reservation_original_path)
        second = take_snapshot()
        assert_second_snapshot(first, second, selected)
        environment = _private_environment(selected, launch_uuid, output, provenance)
        validate_private_environment(environment, selected.hardware_uuid)
        launch_record = {
            "attempt_no": 1,
            "checkpoint_step": checkpoint_step,
            "command": list(command),
            "command_hash": command_hash,
            "cwd": str(ISOLATED_WORKSPACE),
            "expected_wall_seconds": CANARY_EXPECTED_WALL_SECONDS,
            "filesystem_guard_pass": True,
            "first_snapshot": asdict(first),
            "hung_timeout_seconds": CANARY_HUNG_TIMEOUT_SECONDS,
            "input_hashes": asdict(provenance),
            "launch_uuid": launch_uuid,
            "logical_run_id": "V2-007",
            "physical_gpu_indices": [selected.physical_index],
            "physical_gpu_uuids": [selected.hardware_uuid],
            "retry_of": None,
            "role_seed": CANARY_ROLE_SEED,
            "second_snapshot": asdict(second),
            "started_monotonic": started_monotonic,
            "started_utc": started_utc,
            "visibility_class": "engineering-public-no-scientific-outcome",
        }
        atomic_write_canonical_json(output / "launch.json", launch_record)
        stdout_handle = _open_exclusive(output / "stdout.log")
        stderr_handle = _open_exclusive(output / "stderr.log")
        process = subprocess.Popen(
            list(command),
            cwd=ISOLATED_WORKSPACE,
            env=environment,
            stdout=stdout_handle,
            stderr=stderr_handle,
            start_new_session=True,
        )
        child_started_monotonic = time.monotonic()
        pgid = os.getpgid(process.pid)
        leader_start_ticks = proc_start_ticks(process.pid)
        recorded_identities[process.pid] = leader_start_ticks
        handshake_path = output / "child_bound.json"
        next_heartbeat = time.monotonic()
        deadline = child_started_monotonic + CANARY_HUNG_TIMEOUT_SECONDS
        while process.poll() is None:
            now = time.monotonic()
            if now >= deadline:
                stop_reason = "hung-timeout"
                raise LaunchLifecycleError(f"V2-007 exceeded {CANARY_HUNG_TIMEOUT_SECONDS} seconds")
            if now >= next_heartbeat:
                owned = pids_in_process_group(pgid)
                _capture_identities(owned, recorded_identities)
                heartbeat = take_snapshot()
                _assert_no_foreign_gpu_context(heartbeat, selected, owned)
                if binding_verified:
                    assert_owned_gpu_binding(heartbeat, selected, owned_pids=owned, child_pid=process.pid)
                reservation.refresh()
                heartbeat_snapshots.append(
                    {"snapshot": asdict(heartbeat), "snapshot_sha256": snapshot_sha256(heartbeat)}
                )
                next_heartbeat = now + 20.0
            if not binding_verified and handshake_path.is_file():
                _validate_handshake(
                    handshake_path,
                    process_pid=process.pid,
                    pgid=pgid,
                    selected_index=selected.physical_index,
                    selected_uuid=selected.hardware_uuid,
                    launch_uuid=launch_uuid,
                )
                owned = pids_in_process_group(pgid)
                _capture_identities(owned, recorded_identities)
                binding_snapshot = take_snapshot()
                assert_owned_gpu_binding(binding_snapshot, selected, owned_pids=owned, child_pid=process.pid)
                binding_verified = True
            time.sleep(0.25)
        exit_code = process.returncode
        child_ended_monotonic = time.monotonic()
        if not binding_verified:
            raise LaunchLifecycleError("Canary exited before verified GPU binding")
        if exit_code != 0:
            raise LaunchLifecycleError(f"Canary exited with status {exit_code}")
        metrics_path = output / "canary_metrics.json"
        if not metrics_path.is_file():
            raise LaunchLifecycleError("Successful child omitted canary_metrics.json")
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        if not isinstance(metrics, dict):
            raise LaunchLifecycleError("Canary metrics must be a JSON object")
        validate_canary_metrics(metrics, checkpoint_step, provenance)
        stop_reason = "completed"
    except BaseException as error:
        lifecycle_error = f"{type(error).__name__}: {error}"
        if stop_reason == "not-started":
            stop_reason = "lifecycle-error"
        if process is not None and pgid is not None and leader_start_ticks is not None:
            try:
                _terminate_verified_live_group(process, pgid, leader_start_ticks)
            except BaseException as termination_error:
                lifecycle_error += f"; termination={type(termination_error).__name__}: {termination_error}"
        if process is not None:
            exit_code = process.poll()
            child_ended_monotonic = time.monotonic()
    finally:
        if stdout_handle is not None:
            stdout_handle.close()
        if stderr_handle is not None:
            stderr_handle.close()

        release_verified = False
        if reservation is not None and selected is not None:
            try:
                post_snapshot = take_snapshot()
                assert_recorded_gpu_pids_absent(post_snapshot, frozenset(recorded_identities))
                remaining_on_selected = post_snapshot.by_index(selected.physical_index).compute_pids
                if remaining_on_selected:
                    raise GPUGuardError(
                        f"Reserved GPU is occupied at release proof: {remaining_on_selected}"
                    )
                release_path, release_sha256, release_payload = reservation.archive_release(
                    post_exit_snapshot_sha256=snapshot_sha256(post_snapshot)
                )
                release_verified = True
            except BaseException as release_error:
                if lifecycle_error is None:
                    lifecycle_error = f"{type(release_error).__name__}: {release_error}"
                    stop_reason = "unverified-reservation-release"
                else:
                    lifecycle_error += f"; release={type(release_error).__name__}: {release_error}"

        ended_monotonic = time.monotonic()
        ended_utc = _utc_now()
        elapsed = ended_monotonic - started_monotonic
        gpu_interval = 0.0
        if child_started_monotonic is not None:
            gpu_interval = max(0.0, (child_ended_monotonic or ended_monotonic) - child_started_monotonic)
        existing_names = {path.name for path in output.iterdir() if path.is_file() and not path.is_symlink()}
        output_hashes_before_completion = _file_hashes(output, existing_names)
        completion = {
            "actual_gpu_hours": gpu_interval / 3600.0,
            "actual_intervals": [{"end_monotonic": child_ended_monotonic, "start_monotonic": child_started_monotonic}],
            "assignment_order": [2, 3, 0, 1],
            "attempt_no": 1,
            "binding_verified": binding_verified,
            "checkpoint_hash": provenance.checkpoint_sha256,
            "command_hash": command_hash,
            "config_hash": provenance.sanitized_config_sha256,
            "cwd": str(ISOLATED_WORKSPACE),
            "elapsed_seconds": elapsed,
            "exit_code": exit_code,
            "expected_wall_seconds": CANARY_EXPECTED_WALL_SECONDS,
            "filesystem_guard_pass": True,
            "fold": None,
            "heartbeat_snapshots": heartbeat_snapshots,
            "host": socket.gethostname(),
            "hung_timeout_seconds": CANARY_HUNG_TIMEOUT_SECONDS,
            "input_output_hashes": {"inputs": asdict(provenance), "outputs_before_completion": output_hashes_before_completion},
            "launch_uuid": launch_uuid,
            "lifecycle_error": lifecycle_error,
            "logical_run_id": "V2-007",
            "occupancy_before": asdict(first) if first is not None else None,
            "occupancy_post_bind": asdict(binding_snapshot) if binding_snapshot is not None else None,
            "paid_cost_usd": 0.0,
            "pgid": pgid,
            "physical_gpu_indices": [selected.physical_index] if selected is not None else [],
            "physical_gpu_uuids": [selected.hardware_uuid] if selected is not None else [],
            "pid": process.pid if process is not None else None,
            "post_exit_snapshot": asdict(post_snapshot) if post_snapshot is not None else None,
            "quarantine_path_hash": None,
            "reservation_acquired_utc_monotonic": {
                "monotonic": reservation.acquired_monotonic if reservation is not None else None,
                "utc": reservation.acquired_utc if reservation is not None else None,
            },
            "reservation_initial_sha256": reservation_initial_sha256,
            "reservation_lease_deadline": release_payload.get("lease_deadline_monotonic") if release_payload else None,
            "reservation_path": str(release_path if release_path is not None else reservation.path if reservation else ""),
            "reservation_original_path": str(reservation_original_path) if reservation_original_path is not None else None,
            "reservation_release_sha256": release_sha256,
            "reservation_released_utc_monotonic": {
                "monotonic": release_payload.get("released_monotonic") if release_payload else None,
                "utc": release_payload.get("released_utc") if release_payload else None,
            },
            "reservation_release_verified": release_verified,
            "retry_of": None,
            "robot_trials": 0,
            "seed": CANARY_ROLE_SEED,
            "snapshot_age": second.monotonic - first.monotonic if first is not None and second is not None else None,
            "snapshot_time": first.utc if first is not None else None,
            "start_end_monotonic": [started_monotonic, ended_monotonic],
            "start_end_utc": [started_utc, ended_utc],
            "stop_reason": stop_reason,
            "task_state_manifest_hash": None,
            "uid": os.getuid(),
            "visibility_class": "engineering-public-no-scientific-outcome",
        }
        atomic_write_canonical_json(output / "completion.json", completion)
        success = lifecycle_error is None and exit_code == 0 and release_verified and binding_verified
        if success:
            _validate_exact_regular_files(output, FINAL_SUCCESS_FILES - {"terminal_manifest.json"})
        pre_terminal = {path.name for path in output.iterdir() if path.is_file() and not path.is_symlink()}
        terminal = {
            "complete": True,
            "files": _file_hashes(output, pre_terminal),
            "final_expected_files": sorted(FINAL_SUCCESS_FILES) if success else sorted(pre_terminal | {"terminal_manifest.json"}),
            "launch_uuid": launch_uuid,
            "status": "success" if success else "failed-preserved",
        }
        atomic_write_canonical_json(output / "terminal_manifest.json", terminal)
        _seal_output(output, success=success)

    if lifecycle_error is not None:
        raise LaunchLifecycleError(f"{lifecycle_error}; evidence={output}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint-step", type=int, choices=(1000, 5000, 10000), default=1000)
    args = parser.parse_args()
    try:
        output = run_guarded_canary(args.checkpoint_step)
    except BaseException as error:
        print(f"CANARY_LAUNCH_FAILED {type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print(str(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
