"""Quarantined artifact writing and pre-reveal telemetry filtering."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .canonical import atomic_write_canonical_json, canonical_json_sha256, file_sha256
from .filesystem import PersonalRootGuard


PRE_REVEAL_STDOUT_FIELDS = frozenset(
    {
        "launch_uuid",
        "exit_code",
        "gpu_seconds",
        "wall_seconds",
        "peak_memory_bytes",
        "nonfinite",
        "filesystem_guard_pass",
        "gpu_guard_pass",
        "process_ownership_pass",
        "nonfinite_any",
        "hard_operator_safety_abort",
        "artifact_sha256",
    }
)


def filter_pre_reveal_telemetry(record: dict[str, Any]) -> dict[str, Any]:
    forbidden = set(record) - PRE_REVEAL_STDOUT_FIELDS
    if forbidden:
        raise ValueError(f"Pre-reveal telemetry contains forbidden fields: {sorted(forbidden)}")
    return dict(record)


@dataclass
class SealedBatch:
    root: Path
    expected_record_ids: tuple[str, ...]
    guard: PersonalRootGuard = field(default_factory=PersonalRootGuard)

    def __post_init__(self) -> None:
        if len(set(self.expected_record_ids)) != len(self.expected_record_ids):
            raise ValueError("Expected record IDs must be unique")
        self.guard.require_existing(self.root, regular=False)

    @property
    def records_dir(self) -> Path:
        return self.root / "records"

    def initialize(self) -> str:
        if self.records_dir.exists():
            raise FileExistsError(f"Sealed batch already initialized: {self.records_dir}")
        self.records_dir.mkdir(mode=0o700)
        manifest = {
            "status": "sealed-incomplete",
            "expected_record_ids": list(self.expected_record_ids),
            "expected_count": len(self.expected_record_ids),
        }
        return atomic_write_canonical_json(self.root / "expected_manifest.json", manifest)

    def write_record(self, record_id: str, payload: dict[str, Any]) -> str:
        if record_id not in self.expected_record_ids:
            raise KeyError(f"Unexpected logical record: {record_id}")
        target = self.records_dir / f"{record_id}.json"
        if target.exists() or target.is_symlink():
            raise FileExistsError(f"Sealed logical record is immutable: {record_id}")
        return atomic_write_canonical_json(target, payload)

    def completion_manifest(self) -> dict[str, Any]:
        present: dict[str, str] = {}
        for record_id in self.expected_record_ids:
            path = self.records_dir / f"{record_id}.json"
            if path.is_file() and not path.is_symlink():
                present[record_id] = file_sha256(path)
        missing = [record_id for record_id in self.expected_record_ids if record_id not in present]
        return {
            "status": "sealed-complete" if not missing else "sealed-incomplete",
            "expected_count": len(self.expected_record_ids),
            "present_count": len(present),
            "missing_record_ids": missing,
            "record_sha256": present,
            "record_set_sha256": canonical_json_sha256(present),
        }

    def freeze_completion(self, *, terminal_invalid: bool = False) -> str:
        manifest = self.completion_manifest()
        if manifest["missing_record_ids"]:
            if not terminal_invalid:
                raise RuntimeError("Cannot normally reveal an incomplete sealed batch")
            manifest["status"] = "terminal-invalid-audit-only"
            manifest["claim_gate"] = "permanently-failed"
        else:
            manifest["claim_gate"] = "eligible-for-next-frozen-gate"
        target = self.root / "completion_manifest.json"
        if target.exists() or target.is_symlink():
            raise FileExistsError("Completion manifest is immutable")
        return atomic_write_canonical_json(target, manifest)


def require_exact_records(paths: Iterable[Path], expected: int) -> None:
    paths_tuple = tuple(paths)
    if len(paths_tuple) != expected:
        raise RuntimeError(f"Expected exactly {expected} records, found {len(paths_tuple)}")
    if any(path.is_symlink() or not path.is_file() for path in paths_tuple):
        raise RuntimeError("All records must be non-symlink regular files")
