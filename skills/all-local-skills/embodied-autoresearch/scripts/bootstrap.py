#!/usr/bin/env python3
"""Initialize an embodied-autoresearch workspace without overwriting user files."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        slug = "embodied-wam"
    return slug[:48].rstrip("-")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="project root")
    parser.add_argument(
        "--direction",
        default="VLA and World Action Models for long-horizon robot manipulation",
        help="initial research direction",
    )
    parser.add_argument("--run-id", help="explicit lowercase run id")
    parser.add_argument("--new-run", action="store_true", help="initialize a new run even if an active run exists")
    parser.add_argument("--dry-run", action="store_true", help="show planned changes without writing")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: project root does not exist: {root}", file=sys.stderr)
        return 2

    skill_dir = Path(__file__).resolve().parent.parent
    assets = skill_dir / "assets"
    config_template = assets / "AUTORESEARCH_CONFIG.template.json"
    brief_template = assets / "RESEARCH_BRIEF.template.md"
    state_script = skill_dir / "scripts" / "research_state.py"
    required = (config_template, brief_template, state_script)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        print(f"ERROR: skill resources missing: {missing}", file=sys.stderr)
        return 2

    config_path = root / "AUTORESEARCH_CONFIG.json"
    brief_path = root / "RESEARCH_BRIEF.md"
    active_path = root / ".aris" / "autoresearch" / "active_run.json"
    directories = [
        root / ".aris" / "autoresearch" / "runs",
        root / "research-stage",
        root / "idea-stage",
        root / "refine-logs",
        root / "review-stage",
        root / "results",
    ]

    existing_active: dict[str, Any] | None = None
    if active_path.is_file() and not args.new_run:
        try:
            existing_active = read_json(active_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"ERROR: invalid active run pointer: {exc}", file=sys.stderr)
            return 2

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_id = args.run_id or f"{stamp}-{slugify(args.direction)}"
    plan = {
        "root": str(root),
        "direction": args.direction,
        "run_id": existing_active.get("run_id") if existing_active else run_id,
        "reuse_active": bool(existing_active),
        "create_config": not config_path.exists(),
        "create_brief": not brief_path.exists(),
        "create_directories": [str(path.relative_to(root)) for path in directories if not path.exists()],
        "timestamp": utc_now(),
    }
    if args.dry_run:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    if not config_path.exists():
        config = read_json(config_template)
        config.setdefault("research", {})["direction"] = args.direction
        atomic_text(config_path, json.dumps(config, ensure_ascii=False, indent=2) + "\n")

    if not brief_path.exists():
        brief = brief_template.read_text(encoding="utf-8")
        marker = "## Direction\n\n"
        insertion = f"**User-specified direction:** {args.direction}\n\n"
        if marker in brief:
            brief = brief.replace(marker, marker + insertion, 1)
        atomic_text(brief_path, brief)

    if existing_active:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0

    command = [
        sys.executable,
        str(state_script),
        "--root",
        str(root),
        "init",
        "--run-id",
        run_id,
        "--direction",
        args.direction,
        "--config",
        config_path.name,
    ]
    result = subprocess.run(command, text=True, encoding="utf-8", capture_output=True, check=False)
    if result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        return result.returncode
    plan["state"] = result.stdout.strip()
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

