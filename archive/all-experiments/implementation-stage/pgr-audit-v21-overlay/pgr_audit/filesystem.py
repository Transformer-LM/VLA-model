"""Fail-closed personal-root containment and UUID output creation."""

from __future__ import annotations

import os
import stat
import uuid
from dataclasses import dataclass
from pathlib import Path

from .constants import CANONICAL_PERSONAL_ROOT, LOGICAL_PERSONAL_ROOT


class PathContractError(RuntimeError):
    pass


def _is_within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


@dataclass(frozen=True)
class PersonalRootGuard:
    logical_root: Path = LOGICAL_PERSONAL_ROOT
    canonical_root: Path = CANONICAL_PERSONAL_ROOT

    def verify_root(self) -> Path:
        resolved = self.logical_root.resolve(strict=True)
        expected = self.canonical_root.resolve(strict=True)
        if resolved != expected:
            raise PathContractError(f"Logical root resolves to {resolved}, expected {expected}")
        # The logical root may itself be a symlink; symlink mode bits are not
        # meaningful on Linux. Check the resolved directory's permissions.
        if expected.stat().st_mode & stat.S_IWOTH:
            raise PathContractError(f"Canonical personal root is world-writable: {expected}")
        return expected

    def require_existing(self, path: str | os.PathLike[str], *, regular: bool | None = None) -> Path:
        requested = Path(path)
        if not requested.is_absolute() or not _is_within(requested, self.logical_root):
            raise PathContractError(f"Path is not specified under logical personal root: {requested}")
        resolved_root = self.verify_root()
        resolved = requested.resolve(strict=True)
        if not _is_within(resolved, resolved_root):
            raise PathContractError(f"Resolved path escapes personal root: {requested} -> {resolved}")
        info = requested.lstat()
        if stat.S_ISLNK(info.st_mode):
            raise PathContractError(f"Final path is a symlink: {requested}")
        if regular is True and not stat.S_ISREG(info.st_mode):
            raise PathContractError(f"Expected a regular file: {requested}")
        if regular is False and not stat.S_ISDIR(info.st_mode):
            raise PathContractError(f"Expected a directory: {requested}")
        return resolved

    def require_new_path(self, path: str | os.PathLike[str]) -> Path:
        requested = Path(path)
        if not requested.is_absolute() or not _is_within(requested, self.logical_root):
            raise PathContractError(f"New path is not specified under logical personal root: {requested}")
        if requested.exists() or requested.is_symlink():
            raise FileExistsError(f"New output must not preexist: {requested}")
        resolved_root = self.verify_root()
        resolved_parent = requested.parent.resolve(strict=True)
        if not _is_within(resolved_parent, resolved_root):
            raise PathContractError(f"New output parent escapes personal root: {requested.parent}")
        if requested.parent.is_symlink():
            raise PathContractError(f"New output parent is a symlink: {requested.parent}")
        return resolved_parent / requested.name

    def create_uuid_directory(self, parent: str | os.PathLike[str], *, label: str) -> Path:
        parent_path = Path(parent)
        self.require_existing(parent_path, regular=False)
        if not label or any(character not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for character in label):
            raise ValueError(f"Unsafe output label: {label!r}")
        output = parent_path / f"{label}-{uuid.uuid4()}"
        safe_output = self.require_new_path(output)
        safe_output.mkdir(mode=0o700)
        self.require_existing(output, regular=False)
        return output


def enforce_private_umask() -> int:
    previous = os.umask(0o077)
    os.umask(0o077)
    return previous
