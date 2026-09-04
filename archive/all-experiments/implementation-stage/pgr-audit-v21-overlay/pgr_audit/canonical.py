"""Canonical hashing and atomic serialization required by PGR-Audit v2.1."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import tempfile
from pathlib import Path
from typing import Any, Iterator


def canonical_json_bytes(value: Any) -> bytes:
    """Return the protocol's canonical JSON representation, without a newline."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_json_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def file_sha256(path: str | os.PathLike[str], chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_bytes):
            digest.update(chunk)
    return digest.hexdigest()


def _regular_files(root: Path) -> Iterator[tuple[str, Path]]:
    root_lstat = root.lstat()
    if stat.S_ISLNK(root_lstat.st_mode) or not stat.S_ISDIR(root_lstat.st_mode):
        raise ValueError(f"Directory hash root must be a real directory: {root}")

    entries: list[tuple[str, Path]] = []
    for candidate in root.rglob("*"):
        info = candidate.lstat()
        if stat.S_ISLNK(info.st_mode):
            raise ValueError(f"Symlink forbidden in canonical directory hash: {candidate}")
        if stat.S_ISDIR(info.st_mode):
            continue
        if not stat.S_ISREG(info.st_mode):
            raise ValueError(f"Non-regular entry forbidden in canonical directory hash: {candidate}")
        relative = candidate.relative_to(root).as_posix()
        entries.append((relative, candidate))

    for entry in sorted(entries, key=lambda pair: pair[0]):
        yield entry


def directory_manifest_records(root: str | os.PathLike[str]) -> Iterator[dict[str, Any]]:
    root_path = Path(root)
    for relative, candidate in _regular_files(root_path):
        yield {
            "bytes": candidate.stat().st_size,
            "path": relative,
            "sha256": file_sha256(candidate),
        }


def directory_sha256(root: str | os.PathLike[str]) -> str:
    digest = hashlib.sha256()
    for record in directory_manifest_records(root):
        digest.update(canonical_json_bytes(record))
        digest.update(b"\n")
    return digest.hexdigest()


def atomic_write_bytes(path: str | os.PathLike[str], payload: bytes, mode: int = 0o600) -> None:
    """Atomically replace a file and fsync both file and containing directory."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        parent_descriptor = os.open(target.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(parent_descriptor)
        finally:
            os.close(parent_descriptor)
    except BaseException:
        try:
            temporary.unlink(missing_ok=True)
        finally:
            raise


def atomic_write_canonical_json(path: str | os.PathLike[str], value: Any, mode: int = 0o600) -> str:
    payload = canonical_json_bytes(value)
    atomic_write_bytes(path, payload, mode=mode)
    return hashlib.sha256(payload).hexdigest()
