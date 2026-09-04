#!/usr/bin/env python3
"""Atomic run-state manager for embodied-autoresearch.

This script intentionally uses only the Python standard library. It records
execution state and verifies that artifacts exist; it never judges scientific
quality.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
PHASES = (
    "contract",
    "evidence-map",
    "idea-discovery",
    "method-plan",
    "implementation-experiments",
    "evidence-audit",
    "review-improvement",
    "research-synthesis",
)
TERMINAL_GATES = {"pass", "warn"}
ACCEPTANCE = {"deterministic", "provisional", "independent", "human"}
JUDGMENT_PHASES = {
    "idea-discovery",
    "method-plan",
    "evidence-audit",
    "review-improvement",
}
RUN_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")


class StateError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def project_root(value: str) -> Path:
    root = Path(value).expanduser().resolve()
    if not root.is_dir():
        raise StateError(f"project root does not exist: {root}")
    return root


def state_area(root: Path) -> Path:
    return root / ".aris" / "autoresearch"


def active_pointer(root: Path) -> Path:
    return state_area(root) / "active_run.json"


def atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise StateError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise StateError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise StateError(f"expected JSON object in {path}")
    return value


@contextmanager
def state_lock(path: Path, timeout_seconds: float = 5.0) -> Iterable[None]:
    """Use an exclusive lock file with bounded stale-lock recovery."""

    lock = path.with_suffix(path.suffix + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout_seconds
    descriptor: int | None = None
    while descriptor is None:
        try:
            descriptor = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(descriptor, f"pid={os.getpid()} time={utc_now()}\n".encode("utf-8"))
        except FileExistsError:
            try:
                age = time.time() - lock.stat().st_mtime
                if age > 300:
                    lock.unlink()
                    continue
            except FileNotFoundError:
                continue
            if time.monotonic() >= deadline:
                raise StateError(f"state is locked by another process: {lock}")
            time.sleep(0.1)
    try:
        yield
    finally:
        if descriptor is not None:
            os.close(descriptor)
        try:
            lock.unlink()
        except FileNotFoundError:
            pass


def resolve_state_path(root: Path, explicit: str | None = None) -> Path:
    if explicit:
        path = Path(explicit)
        if not path.is_absolute():
            path = root / path
        return path.resolve()
    pointer = load_json(active_pointer(root))
    relative = pointer.get("state")
    if not isinstance(relative, str) or not relative:
        raise StateError("active_run.json does not contain a state path")
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise StateError(f"active state escapes project root: {path}") from exc
    return path


def load_state(path: Path) -> dict[str, Any]:
    state = load_json(path)
    if state.get("schema_version") != SCHEMA_VERSION:
        raise StateError(f"unsupported state schema in {path}")
    phases = state.get("phases")
    if not isinstance(phases, dict) or tuple(phases.keys()) != PHASES:
        raise StateError("state phase order does not match this skill version")
    state.setdefault("overall_assurance", "none")
    return state


def append_history(state: dict[str, Any], event: str, **details: Any) -> None:
    history = state.setdefault("history", [])
    history.append({"time": utc_now(), "event": event, **details})
    if len(history) > 500:
        del history[:-500]


def refresh_overall(state: dict[str, Any]) -> None:
    phases = state["phases"]
    if all(
        phases[name]["status"] == "completed" and phases[name]["gate"] in TERMINAL_GATES
        for name in PHASES
    ):
        state["overall_status"] = "completed"
        state["current_phase"] = None
        judgment_sources = {state["phases"][name]["acceptance"] for name in JUDGMENT_PHASES}
        if judgment_sources == {"independent"}:
            state["overall_assurance"] = "independent"
        elif judgment_sources.issubset({"independent", "human"}) and "human" in judgment_sources:
            state["overall_assurance"] = "human-reviewed"
        else:
            state["overall_assurance"] = "provisional"
    elif any(phases[name]["status"] == "blocked" for name in PHASES):
        state["overall_status"] = "blocked"
    elif any(phases[name]["status"] == "failed" for name in PHASES):
        state["overall_status"] = "needs-recovery"
    else:
        state["overall_status"] = "active"
        state["overall_assurance"] = "none"


def save_state(root: Path, path: Path, state: dict[str, Any]) -> None:
    state["updated_at"] = utc_now()
    refresh_overall(state)
    atomic_json_write(path, state)
    pointer = {
        "schema_version": SCHEMA_VERSION,
        "run_id": state["run_id"],
        "state": path.relative_to(root).as_posix(),
        "updated_at": state["updated_at"],
    }
    atomic_json_write(active_pointer(root), pointer)


def ensure_phase(value: str) -> str:
    if value not in PHASES:
        raise StateError(f"unknown phase {value!r}; choose one of: {', '.join(PHASES)}")
    return value


def ensure_prior_phases_complete(state: dict[str, Any], phase: str) -> None:
    index = PHASES.index(phase)
    for prior in PHASES[:index]:
        record = state["phases"][prior]
        if record["status"] != "completed" or record["gate"] not in TERMINAL_GATES:
            raise StateError(f"cannot begin {phase}: prior phase {prior} has not passed")


def normalize_artifacts(root: Path, values: list[str]) -> list[str]:
    normalized: list[str] = []
    for raw in values:
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = root / candidate
        candidate = candidate.resolve()
        try:
            relative = candidate.relative_to(root)
        except ValueError as exc:
            raise StateError(f"artifact escapes project root: {candidate}") from exc
        if not candidate.exists():
            raise StateError(f"artifact does not exist: {relative.as_posix()}")
        if candidate.is_file() and candidate.stat().st_size == 0:
            raise StateError(f"artifact is empty: {relative.as_posix()}")
        if candidate.is_dir() and not any(candidate.iterdir()):
            raise StateError(f"artifact directory is empty: {relative.as_posix()}")
        normalized.append(relative.as_posix())
    return list(dict.fromkeys(normalized))


def next_action(state: dict[str, Any]) -> dict[str, Any]:
    for name in PHASES:
        record = state["phases"][name]
        if record["status"] == "blocked":
            return {"next_phase": None, "blocked_phase": name, "reason": record.get("note", "")}
        if record["status"] == "failed":
            return {"next_phase": None, "failed_phase": name, "reason": record.get("note", "")}
        if record["status"] in {"pending", "running"}:
            return {"next_phase": name, "status": record["status"]}
    return {"next_phase": None, "complete": state.get("overall_status") == "completed"}


def command_init(args: argparse.Namespace, root: Path) -> int:
    if not RUN_ID_RE.fullmatch(args.run_id):
        raise StateError("run id must be lowercase letters/digits/hyphens and at most 80 characters")
    path = state_area(root) / "runs" / args.run_id / "state.json"
    if path.exists():
        if not args.reuse:
            raise StateError(f"run already exists: {path}")
        state = load_state(path)
        save_state(root, path, state)
        print(path.relative_to(root).as_posix())
        return 0
    now = utc_now()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = (root / config_path).resolve()
    try:
        config_rel = config_path.relative_to(root).as_posix()
    except ValueError as exc:
        raise StateError("configuration path must be inside the project") from exc
    if not config_path.is_file():
        raise StateError(f"configuration file does not exist: {config_rel}")
    state = {
        "schema_version": SCHEMA_VERSION,
        "run_id": args.run_id,
        "direction": args.direction,
        "config": config_rel,
        "created_at": now,
        "updated_at": now,
        "overall_status": "active",
        "overall_assurance": "none",
        "current_phase": None,
        "phases": {
            name: {
                "status": "pending",
                "gate": "pending",
                "acceptance": "none",
                "attempts": 0,
                "started_at": None,
                "completed_at": None,
                "artifacts": [],
                "note": "",
            }
            for name in PHASES
        },
        "usage": {
            "gpu_hours": 0.0,
            "paid_cost_usd": 0.0,
            "real_robot_trials": 0,
            "jobs_completed": 0,
            "budget_exceeded": False,
        },
        "history": [{"time": now, "event": "run-initialized", "direction": args.direction}],
    }
    with state_lock(path):
        save_state(root, path, state)
    print(path.relative_to(root).as_posix())
    return 0


def command_status(args: argparse.Namespace, root: Path, path: Path, state: dict[str, Any]) -> int:
    action = next_action(state)
    if args.json:
        print(json.dumps({"state_path": path.relative_to(root).as_posix(), **state, "action": action}, ensure_ascii=False, indent=2))
    else:
        print(f"run: {state['run_id']} ({state['overall_status']})")
        for name in PHASES:
            record = state["phases"][name]
            print(f"- {name}: {record['status']} / {record['gate']} / {record['acceptance']}")
        print(f"next: {action}")
    return 0


def command_update_direction(
    args: argparse.Namespace,
    root: Path,
    path: Path,
    state: dict[str, Any],
) -> int:
    """Correct an unstarted run direction without rewriting completed work."""

    changed_phases = [
        name
        for name in PHASES
        if state["phases"][name]["status"] != "pending"
        or state["phases"][name]["attempts"] != 0
        or state["phases"][name]["artifacts"]
    ]
    if changed_phases:
        raise StateError(
            "direction can only be updated before research starts; "
            f"changed phases: {', '.join(changed_phases)}"
        )
    direction = args.direction.strip()
    if not direction:
        raise StateError("direction must be a non-empty string")
    old_direction = state.get("direction", "")
    state["direction"] = direction
    append_history(
        state,
        "direction-updated",
        old_direction=old_direction,
        direction=direction,
        note=args.note or "",
    )
    save_state(root, path, state)
    print(direction)
    return 0


def command_begin(args: argparse.Namespace, root: Path, path: Path, state: dict[str, Any]) -> int:
    phase = ensure_phase(args.phase)
    ensure_prior_phases_complete(state, phase)
    running = [name for name in PHASES if state["phases"][name]["status"] == "running" and name != phase]
    if running:
        raise StateError(f"another phase is already running: {running[0]}")
    record = state["phases"][phase]
    if record["status"] == "completed":
        raise StateError(f"phase already completed: {phase}")
    if record["status"] == "blocked":
        raise StateError(f"phase is blocked; use resume after the blocking condition changes: {phase}")
    record.update(
        status="running",
        gate="pending",
        acceptance="none",
        attempts=record["attempts"] + 1,
        started_at=utc_now(),
        completed_at=None,
        note=args.note or "",
    )
    state["current_phase"] = phase
    append_history(state, "phase-begun", phase=phase, attempt=record["attempts"], note=record["note"])
    save_state(root, path, state)
    print(phase)
    return 0


def command_complete(args: argparse.Namespace, root: Path, path: Path, state: dict[str, Any]) -> int:
    phase = ensure_phase(args.phase)
    record = state["phases"][phase]
    if record["status"] != "running":
        raise StateError(f"phase must be running before completion: {phase}")
    if args.gate not in TERMINAL_GATES:
        raise StateError(f"invalid completion gate: {args.gate}")
    if args.acceptance not in ACCEPTANCE:
        raise StateError(f"invalid acceptance source: {args.acceptance}")
    if phase in JUDGMENT_PHASES and args.acceptance == "deterministic":
        raise StateError(f"{phase} contains scientific judgment and cannot be deterministically accepted")
    if phase == "research-synthesis" and args.gate == "warn":
        config = load_json(root / state["config"])
        acceptance_config = config.get("acceptance", {})
        if acceptance_config.get("integrity_warn_blocks_completion") is True:
            raise StateError("research synthesis cannot complete with warn while integrity_warn_blocks_completion=true")
    if not args.artifact:
        raise StateError("at least one non-empty project artifact is required for completion")
    artifacts = normalize_artifacts(root, args.artifact)
    record.update(
        status="completed",
        gate=args.gate,
        acceptance=args.acceptance,
        completed_at=utc_now(),
        artifacts=artifacts,
        note=args.note or "",
    )
    state["current_phase"] = None
    append_history(
        state,
        "phase-completed",
        phase=phase,
        gate=args.gate,
        acceptance=args.acceptance,
        artifacts=artifacts,
        note=record["note"],
    )
    save_state(root, path, state)
    print(phase)
    return 0


def command_interrupt(
    args: argparse.Namespace,
    root: Path,
    path: Path,
    state: dict[str, Any],
    status: str,
) -> int:
    phase = ensure_phase(args.phase)
    record = state["phases"][phase]
    if record["status"] == "completed":
        raise StateError(f"cannot {status} a completed phase: {phase}")
    record.update(
        status=status,
        gate="blocked" if status == "blocked" else "fail",
        acceptance="none",
        completed_at=None,
        note=args.reason,
    )
    state["current_phase"] = None
    append_history(state, f"phase-{status}", phase=phase, reason=args.reason)
    save_state(root, path, state)
    print(phase)
    return 0


def command_resume(args: argparse.Namespace, root: Path, path: Path, state: dict[str, Any]) -> int:
    phase = ensure_phase(args.phase)
    record = state["phases"][phase]
    if record["status"] not in {"blocked", "failed"}:
        raise StateError(f"only blocked or failed phases can be resumed: {phase}")
    previous = record["status"]
    record.update(status="pending", gate="pending", acceptance="none", note=args.note or "")
    append_history(state, "phase-resumed", phase=phase, previous_status=previous, note=record["note"])
    save_state(root, path, state)
    print(phase)
    return 0


def command_record_usage(args: argparse.Namespace, root: Path, path: Path, state: dict[str, Any]) -> int:
    increments = {
        "gpu_hours": args.gpu_hours,
        "paid_cost_usd": args.paid_cost_usd,
        "real_robot_trials": args.real_robot_trials,
        "jobs_completed": args.jobs_completed,
    }
    if any(value < 0 for value in increments.values()):
        raise StateError("usage increments cannot be negative")
    usage = state["usage"]
    for key, value in increments.items():
        usage[key] += value
    config = load_json(root / state["config"])
    compute = config.get("compute", {})
    limits = {
        "gpu_hours": float(compute.get("max_total_gpu_hours", 0.0)),
        "paid_cost_usd": float(compute.get("max_paid_cost_usd", 0.0)),
        "real_robot_trials": int(compute.get("max_real_robot_trials", 0)),
    }
    exceeded = [key for key, limit in limits.items() if usage[key] > limit]
    usage["budget_exceeded"] = bool(exceeded)
    append_history(state, "usage-recorded", increments=increments, exceeded=exceeded, note=args.note or "")
    save_state(root, path, state)
    print(json.dumps(usage, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="project root")
    parser.add_argument("--state", help="explicit state path; defaults to active run")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="initialize and activate a run")
    init.add_argument("--run-id", required=True)
    init.add_argument("--direction", required=True)
    init.add_argument("--config", default="AUTORESEARCH_CONFIG.json")
    init.add_argument("--reuse", action="store_true")

    status = sub.add_parser("status", help="show active state")
    status.add_argument("--json", action="store_true")

    sub.add_parser("next", help="print the next action as JSON")

    direction = sub.add_parser(
        "update-direction",
        help="correct the direction of a run whose phases have not started",
    )
    direction.add_argument("--direction", required=True)
    direction.add_argument("--note", default="")

    begin = sub.add_parser("begin", help="mark a phase running")
    begin.add_argument("phase")
    begin.add_argument("--note", default="")

    complete = sub.add_parser("complete", help="complete a phase with verified artifacts")
    complete.add_argument("phase")
    complete.add_argument("--gate", choices=sorted(TERMINAL_GATES), required=True)
    complete.add_argument("--acceptance", choices=sorted(ACCEPTANCE), required=True)
    complete.add_argument("--artifact", action="append", default=[])
    complete.add_argument("--note", default="")

    for name in ("block", "fail"):
        command = sub.add_parser(name, help=f"mark a phase {name}ed")
        command.add_argument("phase")
        command.add_argument("--reason", required=True)

    resume = sub.add_parser("resume", help="return a blocked or failed phase to pending")
    resume.add_argument("phase")
    resume.add_argument("--note", default="")

    usage = sub.add_parser("record-usage", help="add actual resource usage")
    usage.add_argument("--gpu-hours", type=float, default=0.0)
    usage.add_argument("--paid-cost-usd", type=float, default=0.0)
    usage.add_argument("--real-robot-trials", type=int, default=0)
    usage.add_argument("--jobs-completed", type=int, default=0)
    usage.add_argument("--note", default="")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        root = project_root(args.root)
        if args.command == "init":
            return command_init(args, root)
        path = resolve_state_path(root, args.state)
        with state_lock(path):
            state = load_state(path)
            if args.command == "status":
                return command_status(args, root, path, state)
            if args.command == "next":
                print(json.dumps(next_action(state), ensure_ascii=False, indent=2))
                return 0
            if args.command == "update-direction":
                return command_update_direction(args, root, path, state)
            if args.command == "begin":
                return command_begin(args, root, path, state)
            if args.command == "complete":
                return command_complete(args, root, path, state)
            if args.command == "block":
                return command_interrupt(args, root, path, state, "blocked")
            if args.command == "fail":
                return command_interrupt(args, root, path, state, "failed")
            if args.command == "resume":
                return command_resume(args, root, path, state)
            if args.command == "record-usage":
                return command_record_usage(args, root, path, state)
        raise StateError(f"unsupported command: {args.command}")
    except StateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
