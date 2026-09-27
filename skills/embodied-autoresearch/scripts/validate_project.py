#!/usr/bin/env python3
"""Validate embodied-autoresearch configuration, dependencies, and stage readiness."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


DISCOVERY_SKILLS = (
    "wam-research",
    "paper-search",
)
EXPERIMENT_SKILLS = (
    "experiment-bridge",
    "run-experiment",
)
PHASE_SKILLS = {
    "contract": ("wam-research",),
    "evidence-map": ("paper-search",),
    "idea-discovery": ("wam-research", "scoop-check"),
    "method-plan": ("research-refine-pipeline",),
    "implementation-experiments": EXPERIMENT_SKILLS,
    "evidence-audit": ("analyze-results", "experiment-audit", "result-to-claim"),
    "review-improvement": ("auto-review-loop",),
    "research-synthesis": (),
}


def resolve_skill(root: Path, name: str, config: dict) -> Path | None:
    # Explicit project installation roots take precedence; no archive discovery.
    roots = config.get("skill_roots", [".agents/skills", "skills/all-local-skills", "skills"])
    for value in roots:
        candidate = (root / value / name / "SKILL.md").resolve()
        if candidate.is_file():
            return candidate
    return None


def read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise ValueError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object in {path}")
    return value


def nested(config: dict[str, Any], section: str) -> dict[str, Any]:
    value = config.get(section)
    if not isinstance(value, dict):
        raise ValueError(f"configuration section must be an object: {section}")
    return value


def active_state(root: Path) -> dict[str, Any] | None:
    pointer_path = root / ".aris" / "autoresearch" / "active_run.json"
    if not pointer_path.is_file():
        return None
    pointer = read_json(pointer_path)
    relative = pointer.get("state")
    if not isinstance(relative, str):
        raise ValueError("active_run.json has no valid state path")
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError("active state path escapes project root") from exc
    return read_json(path)


def local_gpu_status() -> tuple[bool, str]:
    command = shutil.which("nvidia-smi")
    if not command:
        return False, "nvidia-smi not found"
    try:
        result = subprocess.run(
            [command, "--query-gpu=name,memory.total", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"nvidia-smi failed: {exc}"
    if result.returncode != 0 or not result.stdout.strip():
        return False, (result.stderr or "nvidia-smi returned no GPU").strip()
    return True, result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--stage", choices=("discovery", "experiments", *PHASE_SKILLS), default="discovery")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    blockers: list[str] = []
    warnings: list[str] = []
    checks: list[dict[str, Any]] = []

    if not root.is_dir():
        blockers.append(f"project root does not exist: {root}")
        config: dict[str, Any] = {}
    else:
        config_path = root / "AUTORESEARCH_CONFIG.json"
        brief_path = root / "RESEARCH_BRIEF.md"
        if not config_path.is_file():
            blockers.append("AUTORESEARCH_CONFIG.json is missing; run bootstrap.py")
            config = {}
        else:
            try:
                config = read_json(config_path)
            except ValueError as exc:
                blockers.append(str(exc))
                config = {}
        if not brief_path.is_file() or brief_path.stat().st_size == 0:
            blockers.append("RESEARCH_BRIEF.md is missing or empty; run bootstrap.py")
        else:
            brief = brief_path.read_text(encoding="utf-8")
            if "ready-for-discovery" not in brief:
                warnings.append("research brief does not declare ready-for-discovery")

    if config:
        try:
            project = nested(config, "project")
            research = nested(config, "research")
            automation = nested(config, "automation")
            compute = nested(config, "compute")
            acceptance = nested(config, "acceptance")
            safety = nested(config, "safety")
        except ValueError as exc:
            blockers.append(str(exc))
            project = research = automation = compute = acceptance = safety = {}

        if config.get("schema_version") != 1:
            blockers.append("unsupported or missing configuration schema_version")
        direction = research.get("direction")
        if not isinstance(direction, str) or not direction.strip():
            blockers.append("research.direction must be a non-empty string")
        exploration_level = research.get("exploration_level", "direction")
        if exploration_level not in {"field", "direction", "idea"}:
            blockers.append("research.exploration_level must be field, direction, or idea")
        selected_macro_direction = research.get("selected_macro_direction")
        if selected_macro_direction is not None and (
            not isinstance(selected_macro_direction, str) or not selected_macro_direction.strip()
        ):
            blockers.append("research.selected_macro_direction must be null or a non-empty string")
        if exploration_level == "field":
            if automation.get("require_direction_checkpoint") is not True:
                blockers.append(
                    "field exploration requires automation.require_direction_checkpoint=true"
                )
            if automation.get("auto_select_idea") is not False:
                blockers.append(
                    "field exploration requires automation.auto_select_idea=false until direction selection"
                )
        if project.get("research_only") is not True:
            warnings.append("project.research_only is not true; this skill still stops before paper writing")
        if project.get("paper_writing") is not False:
            warnings.append("project.paper_writing is enabled but ignored by embodied-autoresearch")
        if research.get("simulation_first") is not True:
            warnings.append("simulation_first is disabled; hardware execution still requires an explicit gate")
        if automation.get("max_idea_cycles", 0) not in range(1, 11):
            blockers.append("automation.max_idea_cycles must be between 1 and 10")
        if automation.get("max_repair_attempts", 0) not in range(1, 11):
            blockers.append("automation.max_repair_attempts must be between 1 and 10")
        if automation.get("max_review_rounds") != 4:
            warnings.append("installed auto-review-loop currently uses four rounds; config differs")
        if acceptance.get("same_family_review_is_provisional") is not True:
            blockers.append("same-family Codex review must remain provisional")
        if not isinstance(acceptance.get("minimum_main_seeds"), int) or acceptance.get("minimum_main_seeds", 0) < 1:
            blockers.append("acceptance.minimum_main_seeds must be a positive integer")

        required_skills = list(PHASE_SKILLS.get(args.stage, EXPERIMENT_SKILLS if args.stage == "experiments" else DISCOVERY_SKILLS))
        if args.stage == "idea-discovery":
            provider = config.get("ideation", {}).get("provider", "idea-discovery-robot")
            if provider not in {"idea-spark", "idea-discovery-robot"}:
                blockers.append("unsupported ideation.provider")
            else:
                required_skills.append(provider)
        missing_skills = [
            name for name in required_skills if resolve_skill(root, name, config) is None
        ]
        checks.append({"name": "required_skills", "ok": not missing_skills, "missing": missing_skills,
                       "resolved": {name: str(resolve_skill(root, name, config)) for name in required_skills if name not in missing_skills}})
        if missing_skills:
            blockers.append(f"missing required skills: {', '.join(missing_skills)}")

        if args.stage in {"experiments", "implementation-experiments"}:
            if exploration_level == "field" and not selected_macro_direction:
                blockers.append(
                    "select and persist research.selected_macro_direction before experiments"
                )
            mode = automation.get("mode")
            if mode != "execute":
                blockers.append(f"automation.mode={mode!r}; set execute before experiments")
            backend = compute.get("backend")
            if backend == "unconfigured":
                blockers.append("compute backend is unconfigured")
            elif backend == "local":
                gpu_ok, gpu_detail = local_gpu_status()
                checks.append({"name": "local_gpu", "ok": gpu_ok, "detail": gpu_detail})
                if not gpu_ok:
                    blockers.append(f"local GPU preflight failed: {gpu_detail}")
            elif backend == "remote":
                host = compute.get("remote_host")
                if not isinstance(host, str) or not host.strip():
                    blockers.append("compute.remote_host is required for remote backend")
                else:
                    checks.append({"name": "remote_host_configured", "ok": True, "detail": host})
            else:
                blockers.append(f"unsupported compute.backend: {backend!r}")

            for key in ("max_pilot_gpu_hours", "max_total_gpu_hours"):
                value = compute.get(key)
                if not isinstance(value, (int, float)) or value <= 0:
                    blockers.append(f"compute.{key} must be positive before experiments")
            if compute.get("max_parallel_jobs", 0) not in range(1, 65):
                blockers.append("compute.max_parallel_jobs must be between 1 and 64")
            if compute.get("paid_compute_allowed") is True and safety.get("require_approval_for_external_spend") is not True:
                blockers.append("paid compute cannot bypass the external-spend approval gate")
            if safety.get("allow_real_robot") is True or compute.get("max_real_robot_trials", 0) > 0:
                blockers.append("real-robot execution requires a separate explicit approval record")
            if safety.get("allow_private_data_upload") is True:
                blockers.append("private-data upload is not authorized by this pipeline")

        try:
            state = active_state(root)
        except ValueError as exc:
            blockers.append(str(exc))
            state = None
        if state:
            usage = state.get("usage", {})
            checks.append({"name": "active_run", "ok": True, "run_id": state.get("run_id")})
            if isinstance(direction, str) and state.get("direction") != direction:
                blockers.append("active run direction does not match research.direction")
            if usage.get("budget_exceeded") is True:
                blockers.append("active run has exceeded a configured resource ceiling")
        else:
            warnings.append("no active run; bootstrap will initialize one")
    else:
        checks.append({"name": "required_skills", "ok": False, "missing": "configuration unavailable"})

    environment = {
        name: shutil.which(name) for name in ("codex", "python", "git", "ssh", "nvidia-smi")
    }
    # An already-running host needs no second CLI; this script proves Python exists.
    if not environment["codex"]:
        warnings.append("Codex CLI unavailable; external unattended supervisor cannot start")
    environment["active_python"] = sys.executable

    report = {
        "stage": args.stage,
        "ready": not blockers,
        "blockers": blockers,
        "warnings": warnings,
        "checks": checks,
        "environment": environment,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"{args.stage}: {'READY' if report['ready'] else 'BLOCKED'}")
        for blocker in blockers:
            print(f"BLOCKER: {blocker}")
        for warning in warnings:
            print(f"WARNING: {warning}")
    return 0 if report["ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
