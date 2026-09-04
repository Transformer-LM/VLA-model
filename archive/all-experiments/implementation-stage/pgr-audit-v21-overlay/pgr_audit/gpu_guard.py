"""Fresh physical-GPU snapshot and private atomic UUID reservation guard."""

from __future__ import annotations

import json
import os
import pwd
import socket
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Sequence

from .canonical import atomic_write_canonical_json, canonical_json_bytes, canonical_json_sha256, file_sha256
from .constants import EXPECTED_GPU_UUID_BY_INDEX, GPU_LOCK_ROOT, GPU_PREFERENCE
from .filesystem import PersonalRootGuard


class GPUGuardError(RuntimeError):
    pass


@dataclass(frozen=True)
class GPUState:
    physical_index: int
    hardware_uuid: str
    memory_used_mib: int
    utilization_percent: int
    compute_pids: tuple[int, ...]
    compute_owners: tuple[tuple[int, str | None], ...] = ()

    @property
    def idle(self) -> bool:
        return not self.compute_pids and self.memory_used_mib <= 500 and self.utilization_percent <= 5


@dataclass(frozen=True)
class GPUSnapshot:
    utc: str
    monotonic: float
    states: tuple[GPUState, ...]

    def by_index(self, index: int) -> GPUState:
        matches = [state for state in self.states if state.physical_index == index]
        if len(matches) != 1:
            raise GPUGuardError(f"Snapshot has {len(matches)} entries for physical GPU {index}")
        return matches[0]


Runner = Callable[[Sequence[str]], str]


def _run(command: Sequence[str]) -> str:
    return subprocess.run(command, check=True, text=True, capture_output=True).stdout


def _csv_rows(text: str) -> list[list[str]]:
    return [[field.strip() for field in line.split(",")] for line in text.splitlines() if line.strip()]


def take_snapshot(runner: Runner = _run) -> GPUSnapshot:
    gpu_rows = _csv_rows(
        runner(
            (
                "nvidia-smi",
                "--query-gpu=index,uuid,memory.used,utilization.gpu",
                "--format=csv,noheader,nounits",
            )
        )
    )
    process_text = runner(
        (
            "nvidia-smi",
            "--query-compute-apps=gpu_uuid,pid",
            "--format=csv,noheader,nounits",
        )
    )
    process_by_uuid: dict[str, list[int]] = {}
    for row in _csv_rows(process_text):
        if len(row) != 2 or row[0] in ("N/A", "[N/A]") or row[1] in ("N/A", "[N/A]"):
            raise GPUGuardError(f"Malformed or unexplained nvidia-smi compute row: {row!r}")
        try:
            process_by_uuid.setdefault(row[0], []).append(int(row[1]))
        except ValueError as error:
            raise GPUGuardError(f"Non-integer compute PID: {row!r}") from error

    states: list[GPUState] = []
    for row in gpu_rows:
        if len(row) != 4:
            raise GPUGuardError(f"Malformed nvidia-smi GPU row: {row!r}")
        index, hardware_uuid, memory, utilization = int(row[0]), row[1], int(row[2]), int(row[3])
        if EXPECTED_GPU_UUID_BY_INDEX.get(index) != hardware_uuid:
            raise GPUGuardError(f"Physical GPU {index} UUID mismatch: {hardware_uuid}")
        pids = tuple(sorted(process_by_uuid.get(hardware_uuid, [])))
        owners: list[tuple[int, str | None]] = []
        for pid in pids:
            try:
                owner = pwd.getpwuid(Path(f"/proc/{pid}").stat().st_uid).pw_name
            except (FileNotFoundError, KeyError, PermissionError):
                owner = None
            owners.append((pid, owner))
        states.append(
            GPUState(
                physical_index=index,
                hardware_uuid=hardware_uuid,
                memory_used_mib=memory,
                utilization_percent=utilization,
                compute_pids=pids,
                compute_owners=tuple(owners),
            )
        )
    if {state.physical_index for state in states} != set(EXPECTED_GPU_UUID_BY_INDEX):
        raise GPUGuardError("Snapshot does not contain exactly physical GPUs 0-3")
    return GPUSnapshot(
        utc=datetime.now(timezone.utc).isoformat(),
        monotonic=time.monotonic(),
        states=tuple(sorted(states, key=lambda state: state.physical_index)),
    )


def choose_idle_gpu(snapshot: GPUSnapshot) -> GPUState:
    for index in GPU_PREFERENCE:
        state = snapshot.by_index(index)
        if state.idle:
            return state
    raise GPUGuardError("No physical GPU satisfies the frozen idle definition")


def proc_start_ticks(pid: int) -> int:
    text = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    # comm may contain spaces and parentheses. Everything after the final ') '
    # starts at field 3; starttime is field 22, hence offset 19 here.
    tail = text.rsplit(") ", 1)[1].split()
    return int(tail[19])


def boot_id() -> str:
    return Path("/proc/sys/kernel/random/boot_id").read_text(encoding="ascii").strip()


@dataclass
class GPUReservation:
    state: GPUState
    launch_uuid: str
    logical_run_id: str
    lease_seconds: float = 90.0
    root: Path = GPU_LOCK_ROOT
    acquired_monotonic: float | None = None
    path: Path | None = None
    acquired_utc: str | None = None
    guard: PersonalRootGuard = field(default_factory=PersonalRootGuard, repr=False)

    def _payload(self, lease_deadline: float) -> dict[str, object]:
        pid = os.getpid()
        return {
            "acquired_monotonic": self.acquired_monotonic,
            "acquired_utc": self.acquired_utc,
            "boot_id": boot_id(),
            "hardware_uuid": self.state.hardware_uuid,
            "host": socket.gethostname(),
            "launch_uuid": self.launch_uuid,
            "lease_deadline_monotonic": lease_deadline,
            "logical_run_id": self.logical_run_id,
            "pgid": os.getpgid(pid),
            "pid": pid,
            "proc_start_ticks": proc_start_ticks(pid),
            "uid": os.getuid(),
        }

    def acquire(self) -> Path:
        if self.path is not None:
            raise GPUGuardError("Reservation object already used")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.guard.require_existing(self.root, regular=False)
        self.acquired_monotonic = time.monotonic()
        self.acquired_utc = datetime.now(timezone.utc).isoformat()
        path = self.root / f"{self.state.hardware_uuid}.lock"
        payload = canonical_json_bytes(self._payload(self.acquired_monotonic + self.lease_seconds))
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as error:
            raise GPUGuardError(f"GPU UUID reservation already exists: {path}") from error
        try:
            os.write(descriptor, payload)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        parent_descriptor = os.open(self.root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(parent_descriptor)
        finally:
            os.close(parent_descriptor)
        self.path = path
        return path

    def refresh(self) -> str:
        if self.path is None or self.acquired_monotonic is None:
            raise GPUGuardError("Cannot refresh an unacquired reservation")
        existing = json.loads(self.path.read_text(encoding="utf-8"))
        if existing.get("launch_uuid") != self.launch_uuid or existing.get("pid") != os.getpid():
            raise GPUGuardError("Reservation ownership changed")
        return atomic_write_canonical_json(
            self.path,
            self._payload(time.monotonic() + self.lease_seconds),
            mode=0o600,
        )

    def archive_release(self, *, post_exit_snapshot_sha256: str) -> tuple[Path, str, dict[str, object]]:
        if self.path is None:
            raise GPUGuardError("Cannot release an unacquired reservation")
        existing = json.loads(self.path.read_text(encoding="utf-8"))
        if existing.get("launch_uuid") != self.launch_uuid or existing.get("pid") != os.getpid():
            raise GPUGuardError("Refusing to alter a reservation owned by another launch")
        released_monotonic = time.monotonic()
        released_utc = datetime.now(timezone.utc).isoformat()
        released_payload = dict(existing)
        released_payload.update(
            {
                "post_exit_snapshot_sha256": post_exit_snapshot_sha256,
                "released_monotonic": released_monotonic,
                "released_utc": released_utc,
                "status": "verified-released",
            }
        )
        atomic_write_canonical_json(self.path, released_payload, mode=0o600)
        archive = self.root / "archive"
        archive.mkdir(mode=0o700, exist_ok=True)
        target = archive / f"{self.launch_uuid}-{self.state.hardware_uuid}.released.json"
        if target.exists() or target.is_symlink():
            raise GPUGuardError(f"Reservation archive already exists: {target}")
        os.rename(self.path, target)
        for directory in (archive, self.root):
            descriptor = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        self.path = None
        return target, file_sha256(target), released_payload


def assert_second_snapshot(first: GPUSnapshot, second: GPUSnapshot, selected: GPUState) -> GPUState:
    if second.monotonic - first.monotonic > 5.0:
        raise GPUGuardError("GPU snapshots are more than five seconds apart")
    refreshed = second.by_index(selected.physical_index)
    if refreshed.hardware_uuid != selected.hardware_uuid or not refreshed.idle:
        raise GPUGuardError("Selected GPU changed identity or became occupied while reserved")
    return refreshed


def pids_in_process_group(pgid: int, proc_root: Path = Path("/proc")) -> frozenset[int]:
    """Return live PIDs in *pgid* without relying on a shell process listing."""

    members: set[int] = set()
    for candidate in proc_root.iterdir():
        if not candidate.name.isdigit():
            continue
        try:
            text = (candidate / "stat").read_text(encoding="utf-8")
            tail = text.rsplit(") ", 1)[1].split()
            # Fields after comm begin at field 3: pgrp (field 5) is offset 2.
            candidate_pgid = int(tail[2])
        except (FileNotFoundError, PermissionError, IndexError, ValueError):
            continue
        if candidate_pgid == pgid:
            members.add(int(candidate.name))
    return frozenset(members)


def assert_owned_gpu_binding(
    snapshot: GPUSnapshot,
    selected: GPUState,
    *,
    owned_pids: frozenset[int],
    child_pid: int,
) -> None:
    """Prove the child is on one selected GPU and no foreign PID joined it."""

    if child_pid not in owned_pids:
        raise GPUGuardError("Launched child is not in the owned process group")
    selected_state = snapshot.by_index(selected.physical_index)
    selected_compute = set(selected_state.compute_pids)
    if child_pid not in selected_compute:
        raise GPUGuardError("Launched child has no compute context on the selected GPU")
    foreign = selected_compute - set(owned_pids)
    if foreign:
        raise GPUGuardError(f"Foreign compute PIDs appeared on reserved GPU: {sorted(foreign)}")
    other_bindings = {
        state.physical_index: sorted(set(state.compute_pids) & set(owned_pids))
        for state in snapshot.states
        if state.physical_index != selected.physical_index and set(state.compute_pids) & set(owned_pids)
    }
    if other_bindings:
        raise GPUGuardError(f"Owned process group is bound to unselected GPUs: {other_bindings}")


def snapshot_sha256(snapshot: GPUSnapshot) -> str:
    return canonical_json_sha256(
        {
            "monotonic": snapshot.monotonic,
            "states": [
                {
                    "compute_owners": list(state.compute_owners),
                    "compute_pids": list(state.compute_pids),
                    "hardware_uuid": state.hardware_uuid,
                    "memory_used_mib": state.memory_used_mib,
                    "physical_index": state.physical_index,
                    "utilization_percent": state.utilization_percent,
                }
                for state in snapshot.states
            ],
            "utc": snapshot.utc,
        }
    )


def assert_recorded_gpu_pids_absent(snapshot: GPUSnapshot, recorded_pids: frozenset[int]) -> None:
    lingering = {
        state.physical_index: sorted(set(state.compute_pids) & set(recorded_pids))
        for state in snapshot.states
        if set(state.compute_pids) & set(recorded_pids)
    }
    if lingering:
        raise GPUGuardError(f"Recorded launch GPU PIDs still present after exit: {lingering}")
