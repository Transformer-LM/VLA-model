"""Manifest-bound, strict checkpoint inspection and host construction."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Mapping

import torch

from .canonical import file_sha256
from .constants import CHECKPOINT_KEYSET_SHA256
from .filesystem import PersonalRootGuard


CHECKPOINT_SHA256 = {
    1000: "6e2f52758054f0da6d76640dfcfc3dd324b0a14f2cf24d4626262781fd1d4735",
    5000: "4b0067d806a321065d1521f4940d34920de234902ae4fe83a2a642ab984b277a",
    10000: "1687afbdcab4f4593c6261d64ac478fd151a0ebd7b641236b60ce1a01fbdee7b",
}
CHECKPOINT_PATH = {
    step: Path(
        "<PERSONAL_RESEARCH_ROOT>/checkpoints/cf-dynalign/"
        f"cf_dynalign_baseline_libero_all_20260727_185501/checkpoints/steps_{step}_pytorch_model.pt"
    )
    for step in CHECKPOINT_SHA256
}
ALLOWED_PREFIXES = ("qwen_vl_interface.", "action_model.")
FORBIDDEN_SUBSTRINGS = ("predictor", "lambda_cf", "cf_", "dynalign", "future_head", "world_model")
EXPECTED_STATE_KEYS = 730


class CheckpointContractError(RuntimeError):
    pass


@dataclass(frozen=True)
class CheckpointAudit:
    step: int
    path: str
    sha256: str
    key_count: int
    keyset_sha256: str
    tensor_count: int
    dtypes: tuple[str, ...]


def validate_state_keys(keys: Mapping[str, object] | set[str] | tuple[str, ...] | list[str]) -> tuple[str, ...]:
    names = tuple(keys.keys()) if isinstance(keys, Mapping) else tuple(keys)
    if len(names) != EXPECTED_STATE_KEYS:
        raise CheckpointContractError(f"Expected exactly {EXPECTED_STATE_KEYS} state keys, got {len(names)}")
    if len(set(names)) != len(names):
        raise CheckpointContractError("Checkpoint contains duplicate state keys")
    for name in names:
        if not isinstance(name, str) or not name.startswith(ALLOWED_PREFIXES):
            raise CheckpointContractError(f"Forbidden checkpoint key prefix: {name!r}")
        lowered = name.lower()
        if any(token in lowered for token in FORBIDDEN_SUBSTRINGS):
            raise CheckpointContractError(f"Forbidden checkpoint key substring: {name!r}")
    ordered = tuple(sorted(names))
    digest = hashlib.sha256()
    for name in ordered:
        digest.update(name.encode("utf-8"))
        digest.update(b"\n")
    if digest.hexdigest() != CHECKPOINT_KEYSET_SHA256:
        raise CheckpointContractError("Checkpoint exact sorted key-set digest mismatch")
    return ordered


def load_audited_state_dict(step: int) -> tuple[dict[str, torch.Tensor], CheckpointAudit]:
    if step not in CHECKPOINT_PATH:
        raise CheckpointContractError(f"Unknown checkpoint step: {step}")
    path = CHECKPOINT_PATH[step]
    PersonalRootGuard().require_existing(path, regular=True)
    actual_hash = file_sha256(path)
    if actual_hash != CHECKPOINT_SHA256[step]:
        raise CheckpointContractError(f"Checkpoint SHA256 mismatch for step {step}")
    value = torch.load(path, map_location="cpu", weights_only=True)
    if not isinstance(value, dict):
        raise CheckpointContractError(f"Checkpoint payload is not a state-dict mapping: {type(value)!r}")
    validate_state_keys(value)
    non_tensors = [key for key, tensor in value.items() if not isinstance(tensor, torch.Tensor)]
    if non_tensors:
        raise CheckpointContractError(f"Checkpoint has non-tensor values: {non_tensors[:5]}")
    audit = CheckpointAudit(
        step=step,
        path=str(path),
        sha256=actual_hash,
        key_count=len(value),
        keyset_sha256=CHECKPOINT_KEYSET_SHA256,
        tensor_count=len(value),
        dtypes=tuple(sorted({str(tensor.dtype) for tensor in value.values()})),
    )
    return value, audit


def strict_load_host_state(host: torch.nn.Module, state_dict: dict[str, torch.Tensor]) -> None:
    expected = set(host.state_dict())
    actual = set(validate_state_keys(state_dict))
    if expected != actual:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise CheckpointContractError(
            f"Host/checkpoint key-set mismatch; missing={missing[:8]}, unexpected={unexpected[:8]}"
        )
    host.load_state_dict(state_dict, strict=True)
    for parameter in host.parameters():
        parameter.requires_grad_(False)
    host.eval()
