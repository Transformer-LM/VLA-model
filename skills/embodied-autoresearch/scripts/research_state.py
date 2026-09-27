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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evidence_contract import (ContractError, check_fingerprints, check_protocol, digest,
    fingerprints, finite_nonnegative, read_object, validate_completion, validate_experiment)


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
TERMINAL_GATES = {"pass"}
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
    state.setdefault("jobs", {})
    state.setdefault("experiments", {})
    for record in phases.values():
        record.setdefault("revision", 1)
        record.setdefault("revisions", [])
    return state


def append_history(state: dict[str, Any], event: str, **details: Any) -> None:
    history = state.setdefault("history", [])
    history.append({"time": utc_now(), "event": event, **details})
    if len(history) > 500:
        del history[:-500]


def refresh_overall(state: dict[str, Any]) -> None:
    phases = state["phases"]
    if state.get("usage", {}).get("budget_exceeded"):
        state["overall_status"] = "blocked"
        state["overall_assurance"] = "none"
        return
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
    if state.get("usage", {}).get("budget_exceeded"):
        return {"next_phase": None, "reason": "resource ceiling exceeded; reconcile or explicitly revise budget"}
    for name in PHASES:
        record = state["phases"][name]
        if record["status"] == "blocked":
            return {"next_phase": None, "blocked_phase": name, "reason": record.get("note", "")}
        if record["status"] == "failed":
            return {"next_phase": None, "failed_phase": name, "reason": record.get("note", "")}
        if record["status"] in {"pending", "running"}:
            return {"next_phase": name, "status": record["status"]}
    return {"next_phase": None, "complete": state.get("overall_status") == "completed"}


def invalidate_from(state: dict, phase: str, reason: str) -> None:
    """Conservatively invalidate the linear phase suffix; preserve earlier revisions."""
    for name in PHASES[PHASES.index(phase):]:
        record = state["phases"][name]
        if record["status"] == "pending" and not record.get("artifacts"):
            continue
        archived = {k: v for k, v in record.items() if k != "revisions"}
        record["revisions"].append(archived)
        record.update(status="pending", gate="pending", acceptance="none",
                      revision=record["revision"] + 1, completed_at=None,
                      artifacts=[], artifact_hashes={}, note=reason)
    state["current_phase"] = None
    state["overall_assurance"] = "none"
    append_history(state, "phases-invalidated", phase=phase, reason=reason)


def refresh_freshness(root: Path, state: dict) -> bool:
    invalid = []
    changed = False
    for name in PHASES:
        record = state["phases"][name]
        if record["status"] != "completed":
            continue
        try:
            check_fingerprints(root, record.get("artifact_hashes"))
        except ContractError as exc:
            invalid.append((PHASES.index(name), str(exc)))
    for exp in state.get("experiments", {}).values():
        try:
            check_fingerprints(root, exp["artifact_hashes"])
            check_fingerprints(root, {exp["manifest"]: exp["manifest_sha256"]})
            if exp.pop("stale", False):
                changed = True
        except ContractError as exc:
            if not exp.get("stale"):
                exp["stale"] = True
                invalid.append((PHASES.index("implementation-experiments"), str(exc)))
    if invalid:
        index, reason = min(invalid)
        invalidate_from(state, PHASES[index], reason)
        changed = True
    return changed


def check_resources(state: dict, config: dict, extra: dict | None = None) -> None:
    compute = config.get("compute", {})
    limits = {"gpu_hours": "max_total_gpu_hours", "paid_cost_usd": "max_paid_cost_usd",
              "real_robot_trials": "max_real_robot_trials"}
    reserved = [j for j in state["jobs"].values() if j["status"] == "reserved"]
    for key, limit_key in limits.items():
        total = state["usage"][key] + sum(j["reservation"][key] for j in reserved)
        total += (extra or {}).get(key, 0)
        limit = finite_nonnegative(compute.get(limit_key, 0), limit_key)
        if total > limit:
            raise StateError(f"{key} budget exceeded: committed {total}, limit {limit}")
    if extra is not None and len(reserved) >= compute.get("max_parallel_jobs", 1):
        raise StateError("maximum concurrent reserved jobs reached")


def command_job(args, root: Path, path: Path, state: dict) -> int:
    if not RUN_ID_RE.fullmatch(args.job_id):
        raise StateError("invalid job_id")
    config = load_json(root / state["config"])
    amounts = {"gpu_hours": finite_nonnegative(args.gpu_hours, "gpu_hours"),
               "paid_cost_usd": finite_nonnegative(args.paid_cost_usd, "paid_cost_usd"),
               "real_robot_trials": finite_nonnegative(args.real_robot_trials, "real_robot_trials")}
    existing = state["jobs"].get(args.job_id)
    if args.command == "reserve-job":
        if existing:
            if existing["status"] == "reserved" and existing["reservation"] == amounts:
                print(args.job_id)
                return 0
            raise StateError("job_id already used; use a new ID for a retry")
        if state["phases"]["implementation-experiments"]["status"] != "running":
            raise StateError("begin implementation-experiments before reserving a job")
        if config.get("automation", {}).get("mode") != "execute":
            raise StateError("execution is not enabled")
        if amounts["real_robot_trials"]:
            raise StateError("real robot jobs require a separately implemented authorization adapter")
        if amounts["paid_cost_usd"] and not config["compute"].get("paid_compute_allowed"):
            raise StateError("paid compute is not authorized in configuration")
        check_resources(state, config, amounts)
        protocol = read_object(root, "refine-logs/EXPERIMENT_PROTOCOL.json")
        check_protocol(root, protocol)
        state["jobs"][args.job_id] = {"status": "reserved", "reservation": amounts,
            "protocol_sha256": digest(root / "refine-logs/EXPERIMENT_PROTOCOL.json"),
            "created_at": utc_now()}
    else:
        if not existing:
            raise StateError("cannot reconcile an unreserved job")
        if existing["status"] == "settled":
            if existing["actual"] != amounts or existing["outcome"] != args.outcome:
                raise StateError("conflicting settlement; do not overwrite actual usage")
            print(args.job_id)
            return 0
        for key, value in amounts.items():
            state["usage"][key] += value
        state["usage"]["jobs_completed"] += int(args.outcome == "completed")
        existing.update(status="settled", actual=amounts, outcome=args.outcome, settled_at=utc_now())
        try:
            check_resources(state, config)
            state["usage"]["budget_exceeded"] = False
        except StateError:
            state["usage"]["budget_exceeded"] = True
    append_history(state, args.command, job_id=args.job_id, amounts=amounts)
    save_state(root, path, state)
    print(args.job_id)
    return 0


def command_record_experiment(args, root: Path, path: Path, state: dict) -> int:
    if state["phases"]["implementation-experiments"]["status"] != "running":
        raise StateError("experiment phase must be running")
    item = read_object(root, args.manifest)
    hashes = validate_experiment(root, state, item)
    job = state["jobs"][item["job_id"]]
    if job["outcome"] != item["execution_status"]:
        raise StateError("manifest status differs from job outcome")
    if job["protocol_sha256"] != digest(root / "refine-logs/EXPERIMENT_PROTOCOL.json"):
        raise StateError("protocol changed since job reservation")
    manifest = normalize_artifacts(root, [args.manifest])[0]
    payload = {**item, "manifest": manifest, "manifest_sha256": digest(root / manifest),
               "artifact_hashes": hashes}
    existing = state["experiments"].get(item["experiment_id"])
    if existing and existing != payload:
        raise StateError("experiment ID is immutable; register a new revision ID")
    if any(e["job_id"] == item["job_id"] and k != item["experiment_id"]
           for k, e in state["experiments"].items()):
        raise StateError("job already bound to a different experiment")
    state["experiments"][item["experiment_id"]] = payload
    append_history(state, "experiment-recorded", experiment_id=item["experiment_id"])
    save_state(root, path, state)
    print(item["experiment_id"])
    return 0


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
                "revision": 1,
                "revisions": [],
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
        "jobs": {},
        "experiments": {},
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
    config = load_json(root / state["config"])
    check_resources(state, config)
    if phase == "idea-discovery" and config.get("research", {}).get("exploration_level") == "field":
        if not config["research"].get("selected_macro_direction"):
            raise StateError("awaiting human macro-direction selection")
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
    if phase in {"evidence-audit", "review-improvement"} and args.command != "adjudicate":
        raise StateError("verdict-bearing phases require adjudicate")
    if args.acceptance == "independent" and phase in {"evidence-audit", "review-improvement"}:
        report_path = ("refine-logs/EXPERIMENT_AUDIT.json" if phase == "evidence-audit"
                       else "review-stage/REVIEW_STATE.json")
        provenance = read_object(root, report_path)
        reviewer_family = provenance.get("reviewer_model_family")
        executor_family = provenance.get("executor_model_family")
        if not reviewer_family or not executor_family or reviewer_family == executor_family:
            raise StateError("independent review requires recorded, distinct model families")
    config = load_json(root / state["config"])
    check_resources(state, config)
    if args.gate == "warn":
        raise StateError("warn is not a completion gate; record limitations and meet phase requirements")
    if phase in JUDGMENT_PHASES and args.acceptance == "deterministic":
        raise StateError(f"{phase} contains scientific judgment and cannot be deterministically accepted")
    required = validate_completion(root, state, phase, config)
    if any(e.get("stale") for e in state["experiments"].values()):
        raise StateError("registered evidence changed; restore immutable artifacts before completion")
    artifacts = normalize_artifacts(root, required + args.artifact)
    record.update(
        status="completed",
        gate=args.gate,
        acceptance=args.acceptance,
        completed_at=utc_now(),
        artifacts=artifacts,
        artifact_hashes=fingerprints(root, artifacts),
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
    raise StateError("record-usage retired: use reserve-job/reconcile-job for idempotent accounting")


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

    adjudicate = sub.add_parser("adjudicate", help="validate an integrity/claim or review report")
    adjudicate.add_argument("phase", choices=("evidence-audit", "review-improvement"))
    adjudicate.add_argument("--gate", choices=("pass",), default="pass")
    adjudicate.add_argument("--acceptance", choices=("provisional", "independent", "human"), required=True)
    adjudicate.add_argument("--artifact", action="append", default=[])
    adjudicate.add_argument("--note", default="")
    reopen = sub.add_parser("reopen", help="archive and invalidate a phase and its downstream phases")
    reopen.add_argument("phase", choices=PHASES)
    reopen.add_argument("--reason", required=True)
    experiment = sub.add_parser("record-experiment")
    experiment.add_argument("--manifest", required=True)
    for operation in ("reserve-job", "reconcile-job"):
        job = sub.add_parser(operation)
        job.add_argument("job_id")
        job.add_argument("--gpu-hours", type=float, required=True)
        job.add_argument("--paid-cost-usd", type=float, default=0)
        job.add_argument("--real-robot-trials", type=int, default=0)
        if operation == "reconcile-job":
            job.add_argument("--outcome", choices=("completed", "failed", "cancelled"), required=True)

    for name in ("block", "fail"):
        command = sub.add_parser(name, help=f"mark a phase {name}ed")
        command.add_argument("phase")
        command.add_argument("--reason", required=True)

    resume = sub.add_parser("resume", help="return a blocked or failed phase to pending")
    resume.add_argument("phase")
    resume.add_argument("--note", default="")

    usage = sub.add_parser("record-usage", help="retired; use reserve-job/reconcile-job")
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
            changed = refresh_freshness(root, state)
            config = load_json(root / state["config"])
            try:
                check_resources(state, config)
                exceeded = False
            except StateError:
                exceeded = True
            if state["usage"].get("budget_exceeded") != exceeded:
                state["usage"]["budget_exceeded"] = exceeded
                append_history(state, "budget-status", exceeded=exceeded)
                changed = True
            if changed:
                save_state(root, path, state)
            if args.command == "reopen":
                if any(j["status"] == "reserved" for j in state["jobs"].values()):
                    raise StateError("reconcile active jobs before reopening phases")
                invalidate_from(state, args.phase, args.reason)
                save_state(root, path, state)
                return 0
            if args.command in {"reserve-job", "reconcile-job"}:
                return command_job(args, root, path, state)
            if args.command == "record-experiment":
                return command_record_experiment(args, root, path, state)
            if args.command == "status":
                return command_status(args, root, path, state)
            if args.command == "next":
                print(json.dumps(next_action(state), ensure_ascii=False, indent=2))
                return 0
            if args.command == "update-direction":
                return command_update_direction(args, root, path, state)
            if args.command == "begin":
                return command_begin(args, root, path, state)
            if args.command in {"complete", "adjudicate"}:
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
    except (StateError, ContractError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
