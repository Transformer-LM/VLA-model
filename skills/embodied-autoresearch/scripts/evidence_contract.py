"""Deterministic provenance checks; these do not establish scientific truth."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


class ContractError(ValueError):
    pass


def project_file(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ContractError("expected a nonempty project-relative file path")
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ContractError(f"not a project file: {value}")
    if path.stat().st_size == 0:
        raise ContractError(f"empty file: {value}")
    return path


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def fingerprints(root: Path, paths: list[str]) -> dict[str, str]:
    return {project_file(root, p).relative_to(root.resolve()).as_posix():
            digest(project_file(root, p)) for p in paths}


def check_fingerprints(root: Path, values: dict) -> None:
    if not isinstance(values, dict) or not values:
        raise ContractError("nonempty artifact hashes are required")
    for path, expected in values.items():
        if digest(project_file(root, path)) != expected:
            raise ContractError(f"stale artifact: {path}")


def read_object(root: Path, value: str) -> dict:
    try:
        data = json.loads(project_file(root, value).read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise ContractError(f"cannot read JSON object {value}: {exc}") from exc
    if not isinstance(data, dict):
        raise ContractError(f"expected JSON object: {value}")
    return data


def finite_nonnegative(value, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractError(f"{label} must be numeric")
    if not math.isfinite(value) or value < 0:
        raise ContractError(f"{label} must be finite and nonnegative")
    return float(value)


def required_paths(phase: str, config: dict) -> list[str]:
    field = config.get("research", {}).get("exploration_level") == "field"
    paths = {
        "contract": ["research-stage/FIELD_DISCOVERY_CONTRACT.md" if field else
                     "research-stage/WAM_ROUTE_CARD.md"],
        "evidence-map": ["research-stage/LITERATURE_MAP.md"] +
                        (["research-stage/DIRECTION_LANDSCAPE.md"] if field else []),
        "idea-discovery": ["idea-stage/IDEA_REPORT.md", "idea-stage/WAM_ROUTE_CARDS.md",
                           "idea-stage/NOVELTY_REPORT.json"],
        "method-plan": ["refine-logs/FINAL_PROPOSAL.md", "refine-logs/EXPERIMENT_PLAN.md",
                        "refine-logs/PREFLIGHT_REPORT.md", "refine-logs/EXPERIMENT_PROTOCOL.json"],
        "implementation-experiments": ["refine-logs/EXPERIMENT_TRACKER.md",
                                      "refine-logs/EXPERIMENT_RESULTS.md"],
        "evidence-audit": ["refine-logs/ANALYSIS_REPORT.md", "refine-logs/EXPERIMENT_AUDIT.json",
                           "refine-logs/CLAIM_VERDICT.json"],
        "review-improvement": ["review-stage/AUTO_REVIEW.md", "review-stage/REVIEW_STATE.json"],
        "research-synthesis": ["research-stage/RESEARCH_DOSSIER.md", "AUTORESEARCH_STATUS.md"],
    }
    return paths[phase]


def check_protocol(root: Path, protocol: dict) -> None:
    for field in ("protocol_id", "primary_metric", "budget_basis", "checkpoint_selection",
                  "aggregation_unit", "uncertainty_method", "stopping_rule"):
        if not isinstance(protocol.get(field), str) or not protocol[field].strip():
            raise ContractError(f"protocol missing {field}")
    check_fingerprints(root, protocol.get("protected_files"))
    editable = protocol.get("editable_paths")
    if not isinstance(editable, list) or not editable:
        raise ContractError("protocol requires editable_paths")
    for raw in editable:
        if not isinstance(raw, str) or not (root / raw).resolve().is_relative_to(root.resolve()):
            raise ContractError("editable path escapes project")


def check_report(root: Path, state: dict, phase: str, report: dict) -> None:
    if report.get("run_id") != state["run_id"]:
        raise ContractError("report run_id mismatch")
    if report.get("revision") != state["phases"][phase].get("revision", 1):
        raise ContractError("report revision mismatch")
    check_fingerprints(root, report.get("input_hashes"))


def check_claim_metrics(root: Path, claims: list) -> None:
    """Resolve metrics by JSON key path, never by finding the same number elsewhere."""
    if not isinstance(claims, list) or not claims:
        raise ContractError("claim verdict requires claims")
    for claim in claims:
        if not isinstance(claim, dict) or not claim.get("id") or not claim.get("statement"):
            raise ContractError("each claim needs id and statement")
        if claim.get("status") not in {"supported", "partial", "refuted", "inconclusive"}:
            raise ContractError("invalid claim status")
        metrics = claim.get("metrics")
        if not isinstance(metrics, list) or not metrics:
            raise ContractError("each empirical claim needs metric references")
        for metric in metrics:
            data = read_object(root, metric["source"])
            keys = metric.get("key_path")
            if not isinstance(keys, list) or not keys:
                raise ContractError("metric requires key_path array")
            try:
                for key in keys:
                    data = data[key]
            except (KeyError, IndexError, TypeError) as exc:
                raise ContractError("metric key path does not resolve") from exc
            value = metric.get("value")
            if (isinstance(value, bool) or not isinstance(value, (int, float)) or
                    not math.isfinite(value) or isinstance(data, bool) or
                    not isinstance(data, (int, float)) or not math.isfinite(data)):
                raise ContractError("metric must resolve to a finite number")
            if value != data:
                raise ContractError(f"metric mismatch at {metric['source']}:{keys}")


def validate_completion(root: Path, state: dict, phase: str, config: dict) -> list[str]:
    paths = required_paths(phase, config)
    for path in paths:
        project_file(root, path)
    if phase == "idea-discovery":
        novelty = read_object(root, paths[-1])
        if novelty.get("search_status") != "complete" or novelty.get("novelty_status") not in {
            "incremental", "potentially_distinct"
        }:
            raise ContractError("novelty unresolved or contradicted; cannot promote candidate")
        prior = novelty.get("verified_prior_work")
        if (novelty.get("evidence_coverage") != "sufficient_for_current_claim" or
                not isinstance(prior, list) or not prior or
                not isinstance(novelty.get("delta"), str) or not novelty["delta"].strip()):
            raise ContractError("novelty needs verified prior work and a concrete delta")
        for item in prior:
            if not isinstance(item, dict) or not item.get("id") or not item.get("url") or not item.get("evidence"):
                raise ContractError("prior-work entries require id, url and evidence pointers")
    if phase == "method-plan":
        protocol = read_object(root, paths[-1])
        check_protocol(root, protocol)
        paths += list(protocol["protected_files"])
    if phase == "implementation-experiments":
        if not state.get("experiments"):
            raise ContractError("record-experiment must register actual runs")
        if any(j["status"] == "reserved" for j in state.get("jobs", {}).values()):
            raise ContractError("reconcile active jobs before completing experiments")
        if not any(e["execution_status"] == "completed" for e in state["experiments"].values()):
            raise ContractError("no completed experiment")
        paths += [e["manifest"] for e in state["experiments"].values()]
    if phase == "evidence-audit":
        audit = read_object(root, paths[1])
        verdict = read_object(root, paths[2])
        for report in (audit, verdict):
            check_report(root, state, phase, report)
        if audit.get("integrity") != "pass":
            raise ContractError("integrity must pass before claims are adjudicated")
        if not state.get("experiments"):
            raise ContractError("no registered experimental evidence")
        required_inputs = {e["manifest"] for e in state["experiments"].values()}
        required_inputs |= {p for e in state["experiments"].values() for p in e["artifact_hashes"]}
        if not required_inputs.issubset(audit["input_hashes"]):
            raise ContractError("audit must bind all registered manifests and raw evidence")
        if paths[1] not in verdict["input_hashes"]:
            raise ContractError("claim verdict must bind the current integrity report")
        check_claim_metrics(root, verdict.get("claims"))
        for claim in verdict["claims"]:
            if claim.get("scope") not in {"pilot", "main"}:
                raise ContractError("claim scope must be pilot or main")
            ids = claim.get("experiment_ids")
            if not isinstance(ids, list) or not ids or any(i not in state["experiments"] for i in ids):
                raise ContractError("claim must identify registered experiments")
            if claim["scope"] == "main":
                conditions = {}
                for exp_id in ids:
                    exp = state["experiments"][exp_id]
                    if exp["execution_status"] == "completed":
                        condition = exp.get("condition_id")
                        seed = exp.get("training_seed")
                        if not condition or isinstance(seed, bool) or not isinstance(seed, int):
                            raise ContractError("main evidence needs condition_id and training_seed")
                        conditions.setdefault(condition, set()).add(seed)
                minimum = config.get("acceptance", {}).get("minimum_main_seeds", 3)
                if not conditions or any(len(seeds) < minimum for seeds in conditions.values()):
                    raise ContractError("insufficient independent training seeds for main claim; scope as pilot")
            for metric in claim["metrics"]:
                if metric["source"] not in verdict["input_hashes"]:
                    raise ContractError("claim metric source missing from input_hashes")
                if metric["source"] not in audit["input_hashes"]:
                    raise ContractError("claim metric source was not covered by integrity audit")
        paths += list(audit["input_hashes"]) + list(verdict["input_hashes"])
    if phase == "review-improvement":
        review = read_object(root, paths[1])
        check_report(root, state, phase, review)
        if (not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip() or
                not isinstance(review.get("model"), str) or not review["model"].strip()):
            raise ContractError("review requires reviewer and model provenance")
        if review.get("unresolved_critical") != []:
            raise ContractError("resolve or explicitly scope out critical review findings")
        for key in ("refine-logs/EXPERIMENT_AUDIT.json", "refine-logs/CLAIM_VERDICT.json"):
            if key not in review["input_hashes"]:
                raise ContractError("review must bind current audit and claim verdict")
        paths += list(review["input_hashes"])
    return list(dict.fromkeys(paths))


def validate_experiment(root: Path, state: dict, item: dict) -> dict:
    for key in ("experiment_id", "hypothesis_id", "job_id", "protocol_id"):
        if not isinstance(item.get(key), str) or not item[key].strip():
            raise ContractError(f"experiment missing {key}")
    if item.get("operation") not in {"baseline", "debug", "improve", "mechanism_test", "ablation", "replicate"}:
        raise ContractError("invalid experiment operation")
    if item.get("execution_status") not in {"completed", "failed", "cancelled"}:
        raise ContractError("invalid execution status")
    if item.get("scientific_outcome") not in {"supported", "refuted", "inconclusive", "not_evaluated"}:
        raise ContractError("invalid scientific outcome")
    if item["execution_status"] != "completed" and item["scientific_outcome"] != "not_evaluated":
        raise ContractError("failed execution cannot adjudicate a hypothesis")
    parent = item.get("parent_id")
    if parent and parent not in state.get("experiments", {}):
        raise ContractError("unknown parent experiment")
    job = state.get("jobs", {}).get(item["job_id"])
    if not job or job["status"] != "settled":
        raise ContractError("experiment requires a settled job")
    protocol = read_object(root, "refine-logs/EXPERIMENT_PROTOCOL.json")
    check_protocol(root, protocol)
    if item["protocol_id"] != protocol["protocol_id"]:
        raise ContractError("experiment protocol mismatch")
    artifacts = item.get("artifacts", {})
    for role in ("config", "log", "source_snapshot"):
        if role not in artifacts:
            raise ContractError(f"experiment missing artifact {role}")
    if item["execution_status"] == "completed" and "metrics" not in artifacts:
        raise ContractError("completed experiment requires metrics")
    if "metrics" in artifacts:
        read_object(root, artifacts["metrics"])
    return fingerprints(root, list(artifacts.values()))
