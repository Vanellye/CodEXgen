"""Fail-closed M*ASH generation boundary and create-only artifact store.

This module does not execute generated content or provide external/device adapters.
"""
from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from typing import Callable


class BoundaryViolation(PermissionError):
    """Raised when an operation is outside the M*ASH allowlist."""


ALLOWED_CAPABILITIES = frozenset({
    "code.generate",
    "code.validate",
    "tests.isolated",
    "evidence.record",
    "review.present",
})

PROHIBITED_CAPABILITIES = frozenset({
    "credentials.extract",
    "execution.hidden",
    "dispatch.external",
    "patch.external",
    "hardware.activate",
    "biological.intervene",
    "repository.merge",
    "release.publish",
    "deployment.perform",
})


@dataclass(frozen=True)
class BoundaryEvent:
    capability: str
    decision: str
    reason: str


class ExecutionBoundaryGuard:
    """Exact allowlist: unknown and prohibited capabilities fail closed."""

    def __init__(self, audit: Callable[[BoundaryEvent], None] | None = None):
        self._audit = audit or (lambda _event: None)

    def authorize(self, capability: str) -> None:
        if capability in ALLOWED_CAPABILITIES:
            self._audit(BoundaryEvent(capability, "allow", "allowlisted"))
            return
        reason = "explicitly_prohibited" if capability in PROHIBITED_CAPABILITIES else "unknown_capability"
        self._audit(BoundaryEvent(capability, "deny", reason))
        raise BoundaryViolation(f"M*ASH boundary denied capability: {reason}")


class CreateOnlyArtifactStore:
    """Write new files beneath an existing root; never replace or follow symlinks.

    Uses descriptor-relative traversal and O_EXCL. Parent directories must already
    exist. This is intentionally a narrow artifact writer, not a general filesystem API.
    """

    def __init__(self, root: str | os.PathLike[str], guard: ExecutionBoundaryGuard):
        self.root = os.fspath(root)
        self.guard = guard
        if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
            raise RuntimeError("platform lacks required no-follow directory protections")
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        self._root_fd = os.open(self.root, flags)
        if not stat.S_ISDIR(os.fstat(self._root_fd).st_mode):
            os.close(self._root_fd)
            raise NotADirectoryError(self.root)

    def close(self) -> None:
        if self._root_fd is not None:
            os.close(self._root_fd)
            self._root_fd = None

    def __enter__(self) -> "CreateOnlyArtifactStore":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    @staticmethod
    def _parts(relative_path: str) -> list[str]:
        if not isinstance(relative_path, str) or not relative_path or "\x00" in relative_path:
            raise BoundaryViolation("invalid artifact path")
        if relative_path.startswith("/"):
            raise BoundaryViolation("absolute paths are not permitted")
        parts = relative_path.split("/")
        if any(part in ("", ".", "..") for part in parts):
            raise BoundaryViolation("path traversal or empty component rejected")
        return parts

    def write_new(self, relative_path: str, content: bytes) -> None:
        self.guard.authorize("evidence.record")
        if self._root_fd is None:
            raise RuntimeError("artifact store is closed")
        if not isinstance(content, bytes):
            raise TypeError("artifact content must be bytes")

        parts = self._parts(relative_path)
        current_fd = os.dup(self._root_fd)
        try:
            for component in parts[:-1]:
                next_fd = os.open(
                    component,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                    dir_fd=current_fd,
                )
                os.close(current_fd)
                current_fd = next_fd

            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
            file_fd = os.open(parts[-1], flags, 0o600, dir_fd=current_fd)
            try:
                view = memoryview(content)
                while view:
                    written = os.write(file_fd, view)
                    if written <= 0:
                        raise OSError("short write")
                    view = view[written:]
                os.fsync(file_fd)
            finally:
                os.close(file_fd)
            os.fsync(current_fd)
        finally:
            os.close(current_fd)
