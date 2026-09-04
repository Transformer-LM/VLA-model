"""Pre-CUDA provenance verifier for the exact V2-007 engineering canary."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch

from .canonical import canonical_json_sha256, directory_sha256, file_sha256
from .checkpoint import CHECKPOINT_PATH, CHECKPOINT_SHA256
from .constants import (
    CANARY_APPROVAL_PATH,
    CANARY_ENVIRONMENT_LOCK,
    CODE_REVIEW_ROOT,
    ISOLATED_WORKSPACE,
    TRAIN_PYTHON,
)
from .filesystem import PersonalRootGuard
from .host import SANITIZED_HOST_CONFIG_PAYLOAD
from .spec import VerifiedSpec, verify_frozen_spec


EXPECTED_UPSTREAM_HEAD = "3422b9f2387b6f682cf02802904a77b23ab13afd"
QWEN_TREE_NAME = "qwen3_vl_4b_complete_tree"


class ProvenanceError(RuntimeError):
    pass


@dataclass(frozen=True)
class CanaryProvenance:
    approval_sha256: str
    checkpoint_sha256: str
    environment_lock_sha256: str
    overlay_source_sha256: str
    qwen_tree_sha256: str
    review_response_sha256: str
    sanitized_config_sha256: str
    test_file_sha256: str
    upstream_head: str


def source_tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(root.glob("*.py"), key=lambda path: path.name)
    if not files:
        raise ProvenanceError(f"No Python source files found under {root}")
    for path in files:
        record = {"bytes": path.stat().st_size, "path": path.name, "sha256": file_sha256(path)}
        digest.update(json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def _entry(spec: VerifiedSpec, logical_name: str) -> dict[str, Any]:
    values = [entry for entry in spec.input_manifest.get("entries", []) if entry.get("logical_name") == logical_name]
    if len(values) != 1:
        raise ProvenanceError(f"Expected one input-manifest entry named {logical_name}, got {len(values)}")
    return values[0]


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ProvenanceError(f"Expected JSON object: {path}")
    return value


def _verify_environment(lock: dict[str, Any]) -> None:
    if platform.python_version() != lock.get("python"):
        raise ProvenanceError("Python version differs from canary environment lock")
    executable = Path(sys.executable)
    if str(executable) != lock.get("executable") or file_sha256(executable) != lock.get("executable_sha256"):
        raise ProvenanceError("Python executable path/hash differs from canary environment lock")
    if str(torch.version.cuda) != lock.get("cuda_runtime"):
        raise ProvenanceError("Torch CUDA runtime differs from canary environment lock")
    for name, expected in lock.get("packages", {}).items():
        if importlib.metadata.version(name) != expected:
            raise ProvenanceError(f"Package version mismatch for {name}")
    freeze = subprocess.run(
        (str(executable), "-m", "pip", "freeze", "--all"),
        check=True,
        text=True,
        capture_output=True,
    ).stdout.splitlines()
    payload = "\n".join(sorted(freeze)) + "\n"
    if hashlib.sha256(payload.encode("utf-8")).hexdigest() != lock.get("pip_freeze_all_sorted_sha256"):
        raise ProvenanceError("Sorted pip-freeze digest mismatch")


def _verify_git(spec: VerifiedSpec) -> str:
    head = subprocess.run(
        ("git", "rev-parse", "HEAD"), cwd=ISOLATED_WORKSPACE, check=True, text=True, capture_output=True
    ).stdout.strip()
    if head != EXPECTED_UPSTREAM_HEAD:
        raise ProvenanceError(f"Upstream HEAD mismatch: {head}")
    for command in (("git", "diff", "--quiet", "HEAD", "--"), ("git", "diff", "--cached", "--quiet")):
        if subprocess.run(command, cwd=ISOLATED_WORKSPACE).returncode != 0:
            raise ProvenanceError("Tracked upstream workspace is dirty")
    status = subprocess.run(
        ("git", "status", "--porcelain=v1", "--untracked-files=all"),
        cwd=ISOLATED_WORKSPACE,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.splitlines()
    allowed = ("?? pgr_audit/", "?? tests/", "?? environment/", "?? CANARY_APPROVAL_TEMPLATE.json")
    if any(not line.startswith(allowed) for line in status):
        raise ProvenanceError(f"Unexpected untracked workspace entry: {status}")
    for entry in spec.input_manifest.get("entries", []):
        if entry.get("kind") != "git_blob":
            continue
        path = entry.get("repo_relative_path")
        blob = subprocess.run(
            ("git", "show", f"{head}:{path}"), cwd=ISOLATED_WORKSPACE, check=True, capture_output=True
        ).stdout
        if len(blob) != entry.get("bytes") or hashlib.sha256(blob).hexdigest() != entry.get("sha256"):
            raise ProvenanceError(f"Pinned upstream git blob mismatch: {path}")
    return head


def verify_canary_provenance(checkpoint_step: int) -> CanaryProvenance:
    guard = PersonalRootGuard()
    guard.verify_root()
    spec = verify_frozen_spec()
    for path, regular in (
        (ISOLATED_WORKSPACE, False),
        (CANARY_APPROVAL_PATH, True),
        (CANARY_ENVIRONMENT_LOCK, True),
        (TRAIN_PYTHON, True),
        (CHECKPOINT_PATH[checkpoint_step], True),
    ):
        guard.require_existing(path, regular=regular)

    approval = _load_json(CANARY_APPROVAL_PATH)
    if approval.get("schema") != "pgr-v2-007-approval-v1" or approval.get("verdict") != "PASS":
        raise ProvenanceError("Canary approval receipt is absent or not PASS")
    if approval.get("canary_authorization") != "GO" or checkpoint_step not in approval.get("approved_checkpoint_steps", []):
        raise ProvenanceError("Canary approval does not authorize this checkpoint step")

    overlay = source_tree_sha256(ISOLATED_WORKSPACE / "pgr_audit")
    test_hash = file_sha256(ISOLATED_WORKSPACE / "tests/test_foundation.py")
    environment_hash = file_sha256(CANARY_ENVIRONMENT_LOCK)
    if overlay != approval.get("overlay_source_sha256") or test_hash != approval.get("test_file_sha256"):
        raise ProvenanceError("Reviewed overlay/test hash mismatch")
    if environment_hash != approval.get("environment_lock_sha256"):
        raise ProvenanceError("Reviewed environment-lock hash mismatch")
    test_log_path = Path(approval.get("test_log_path", ""))
    guard.require_existing(test_log_path, regular=True)
    if CODE_REVIEW_ROOT.resolve(strict=True) not in test_log_path.resolve(strict=True).parents:
        raise ProvenanceError("CPU/static test log is outside the private code-review root")
    if file_sha256(test_log_path) != approval.get("test_log_sha256"):
        raise ProvenanceError("Final CPU/static test log hash mismatch")
    review_path = Path(approval.get("review_response_path", ""))
    guard.require_existing(review_path, regular=True)
    if CODE_REVIEW_ROOT.resolve(strict=True) not in review_path.resolve(strict=True).parents:
        raise ProvenanceError("Review response is outside the private code-review root")
    review_hash = file_sha256(review_path)
    if review_hash != approval.get("review_response_sha256"):
        raise ProvenanceError("Final code-review response hash mismatch")

    lock = _load_json(CANARY_ENVIRONMENT_LOCK)
    _verify_environment(lock)
    head = _verify_git(spec)
    qwen = _entry(spec, QWEN_TREE_NAME)
    qwen_path = Path(qwen["path"])
    guard.require_existing(qwen_path, regular=False)
    qwen_hash = directory_sha256(qwen_path)
    if qwen_hash != qwen.get("sha256"):
        raise ProvenanceError("Qwen tree digest mismatch")
    checkpoint_hash = file_sha256(CHECKPOINT_PATH[checkpoint_step])
    if checkpoint_hash != CHECKPOINT_SHA256[checkpoint_step]:
        raise ProvenanceError("Canary checkpoint digest mismatch")
    config_hash = canonical_json_sha256(SANITIZED_HOST_CONFIG_PAYLOAD)
    if config_hash != approval.get("sanitized_config_sha256"):
        raise ProvenanceError("Sanitized host configuration hash mismatch")

    return CanaryProvenance(
        approval_sha256=file_sha256(CANARY_APPROVAL_PATH),
        checkpoint_sha256=checkpoint_hash,
        environment_lock_sha256=environment_hash,
        overlay_source_sha256=overlay,
        qwen_tree_sha256=qwen_hash,
        review_response_sha256=review_hash,
        sanitized_config_sha256=config_hash,
        test_file_sha256=test_hash,
        upstream_head=head,
    )
