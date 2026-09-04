"""Runtime verification of the exact frozen protocol and jury authorization."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .canonical import file_sha256
from .constants import (
    CONFIG_SHA256,
    FREEZE_MANIFEST_SHA256,
    JURY_RESPONSE_SHA256,
    PREREG_ROOT,
    PROTOCOL_ID,
    PROTOCOL_SHA256,
)
from .filesystem import PersonalRootGuard


class SpecVerificationError(RuntimeError):
    pass


@dataclass(frozen=True)
class VerifiedSpec:
    protocol: dict[str, Any]
    active_config: dict[str, Any]
    input_manifest: dict[str, Any]
    preregistration_lock: dict[str, Any]
    bundle_manifest: dict[str, Any]
    authorized_scopes: frozenset[str]


_BASENAME_BY_LOCKED_PATH = {
    "refine-logs/PGR_AUDIT_PROTOCOL.json": "PGR_AUDIT_PROTOCOL.json",
    "AUTORESEARCH_CONFIG_HYBRID_EXPANDED.json": "AUTORESEARCH_CONFIG_HYBRID_EXPANDED.json",
    "refine-logs/INPUT_MANIFEST.json": "INPUT_MANIFEST.json",
    "refine-logs/FINAL_PROPOSAL.md": "FINAL_PROPOSAL.md",
    "refine-logs/EXPERIMENT_PLAN.md": "EXPERIMENT_PLAN.md",
    "refine-logs/EXPERIMENT_TRACKER.md": "EXPERIMENT_TRACKER.md",
    "idea-stage/docs/research_contract.md": "research_contract.md",
    "refine-logs/PREREGISTRATION_LOCK.json": "PREREGISTRATION_LOCK.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SpecVerificationError(f"Cannot parse frozen JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise SpecVerificationError(f"Frozen JSON must be an object: {path}")
    return value


def verify_frozen_spec(root: Path = PREREG_ROOT) -> VerifiedSpec:
    guard = PersonalRootGuard()
    guard.require_existing(root, regular=False)

    bundle_path = root / "PGR_V2_FREEZE_MANIFEST_20260807_111946.json"
    jury_path = root / "009-experiment-plan-v21-jury.response.md"
    if file_sha256(bundle_path) != FREEZE_MANIFEST_SHA256:
        raise SpecVerificationError("Freeze-manifest raw-byte SHA256 mismatch")
    if file_sha256(jury_path) != JURY_RESPONSE_SHA256:
        raise SpecVerificationError("Execution-jury raw-byte SHA256 mismatch")

    bundle = _load_json(bundle_path)
    for entry in bundle.get("files", []):
        source_path = entry.get("path")
        expected = entry.get("sha256")
        basename = _BASENAME_BY_LOCKED_PATH.get(source_path)
        if basename is None or not isinstance(expected, str):
            raise SpecVerificationError(f"Unknown or malformed frozen entry: {entry!r}")
        actual = file_sha256(root / basename)
        if actual != expected:
            raise SpecVerificationError(f"Frozen file mismatch for {source_path}: {actual} != {expected}")

    protocol_path = root / "PGR_AUDIT_PROTOCOL.json"
    config_path = root / "AUTORESEARCH_CONFIG_HYBRID_EXPANDED.json"
    if file_sha256(protocol_path) != PROTOCOL_SHA256 or file_sha256(config_path) != CONFIG_SHA256:
        raise SpecVerificationError("Compiled protocol/config hash constants do not match runtime inputs")

    protocol = _load_json(protocol_path)
    config = _load_json(config_path)
    inputs = _load_json(root / "INPUT_MANIFEST.json")
    lock = _load_json(root / "PREREGISTRATION_LOCK.json")

    if protocol.get("protocol_id") != PROTOCOL_ID:
        raise SpecVerificationError("Protocol ID mismatch")
    if protocol.get("checkpoint_screen", {}).get("rollouts") != 150:
        raise SpecVerificationError("Screen cardinality must be 150")
    closed_loop = protocol.get("closed_loop_evaluation", {})
    if closed_loop.get("stage1", {}).get("total_rollouts") != 6000:
        raise SpecVerificationError("Stage-1 cardinality must be 6000")
    if closed_loop.get("stage2", {}).get("total_rollouts") != 4000:
        raise SpecVerificationError("Stage-2 cardinality must be 4000")
    if protocol.get("compute_telemetry", {}).get("gpu_hour_cap") is not None:
        raise SpecVerificationError("GPU-hour admission cap must be null")
    if config.get("safety", {}).get("allow_real_robot") is not False:
        raise SpecVerificationError("Live robot must remain disabled")
    if protocol.get("real_robot_safety", {}).get("live_action_authorized_now") is not False:
        raise SpecVerificationError("Protocol unexpectedly authorizes live robot action")

    return VerifiedSpec(
        protocol=protocol,
        active_config=config,
        input_manifest=inputs,
        preregistration_lock=lock,
        bundle_manifest=bundle,
        authorized_scopes=frozenset({"A", "B", "C", "D", "E"}),
    )
