"""Classify observable execution deficiencies, without judging scientific success."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evidence_contract import ContractError, project_file, read_object


def diagnose(root: Path, manifests: list[str], minimum_seeds: int = 3) -> dict:
    findings = []
    runs = []
    def add(kind, evidence, action):
        findings.append({"type": kind, "evidence": evidence, "next_action": action})
    for filename in manifests:
        item = read_object(root, filename)
        runs.append(item)
        log = item.get("artifacts", {}).get("log")
        text = project_file(root, log).read_text(encoding="utf-8", errors="replace").lower() if log else ""
        if "out of memory" in text or "cuda oom" in text:
            add("gpu_oom", log, "repair resource configuration; preserve comparison budget")
        elif "modulenotfounderror" in text:
            add("missing_dependency", log, "repair the pinned environment")
        elif item.get("execution_status") == "failed":
            add("execution_failure", log or filename, "inspect traceback; do not reject hypothesis")
        if item.get("execution_status") == "completed" and "metrics" not in item.get("artifacts", {}):
            add("missing_metrics", filename, "repair result collection before interpretation")
        if item.get("scientific_outcome") == "inconclusive":
            add("inconclusive", filename, "check uncertainty and discriminating power before pivoting")
        visual = item.get("artifacts", {}).get("rollout_diagnosis")
        if visual:
            report = read_object(root, visual)
            for episode in report.get("episodes", []):
                for key in ("episode_id", "task_id", "initial_state_id", "video_path",
                            "observed_behavior", "suspected_failure", "next_discriminating_test"):
                    if key not in episode:
                        add("incomplete_visual_diagnosis", visual, f"supply {key}")
    if not any(r.get("operation") == "baseline" and r.get("execution_status") == "completed" for r in runs):
        add("missing_baseline", manifests, "reproduce a matched baseline")
    families = {}
    for run in runs:
        if run.get("execution_status") == "completed":
            family = run.get("condition_id", run.get("hypothesis_id", "unknown"))
            families.setdefault(family, set())
            if isinstance(run.get("training_seed"), int) and not isinstance(run["training_seed"], bool):
                families[family].add(run["training_seed"])
    for family, seeds in families.items():
        if len(seeds) < minimum_seeds:
            add("insufficient_seeds", {"condition_id": family, "observed": len(seeds)},
                "pilot only; replicate according to the statistical protocol")
    return {"findings": findings, "scientific_verdict": "not_adjudicated"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--manifest", action="append", required=True)
    parser.add_argument("--minimum-seeds", type=int, default=3)
    args = parser.parse_args()
    try:
        if args.minimum_seeds < 1:
            raise ContractError("minimum seeds must be positive")
        print(json.dumps(diagnose(Path(args.root).resolve(), args.manifest, args.minimum_seeds), indent=2))
        return 0
    except (ContractError, ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
