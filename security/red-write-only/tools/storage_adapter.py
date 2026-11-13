"""Create-only filesystem adapter guarded at the point of mutation.

The host supplies an already-open, trusted output-root directory descriptor.
Allowed subdirectories must already exist and must not be symlinks.
"""
import os
import stat
import time
import uuid

from .execution_boundary_guard import ExecutionBoundaryGuard


class StorageDenied(PermissionError):
    pass


class CreateOnlyStorageAdapter:
    def __init__(self, root_fd: int, guard: ExecutionBoundaryGuard, audit_sink):
        if not callable(audit_sink):
            raise TypeError("an append-only audit_sink is required")
        if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
            raise RuntimeError("platform lacks required no-follow directory primitives")
        self._root_fd = os.dup(root_fd)
        self._guard = guard
        self._audit = audit_sink

    def close(self):
        if self._root_fd is not None:
            os.close(self._root_fd)
            self._root_fd = None

    def create(self, operation: str, path: str, content: bytes, grant):
        if self._root_fd is None:
            raise StorageDenied("adapter_closed")
        if not isinstance(content, bytes):
            raise TypeError("content must be bytes; no implicit execution or serialization")
        if len(content) > 1_000_000:
            raise StorageDenied("artifact_size_limit_exceeded")

        decision = self._guard.authorize(operation, path, grant)
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": int(time.time()),
            "actor": getattr(grant, "actor", "unknown"),
            "operation": operation,
            "target_path": path,
            "decision": "ALLOW_ATTEMPT" if decision.allowed else "DENY",
            "reason": decision.reason,
            "source_revision": getattr(grant, "source_revision", ""),
            "authorization_ref": getattr(grant, "approval_ref", ""),
        }
        # Fail closed if the append-only audit sink cannot record the decision.
        self._audit(event)
        if not decision.allowed:
            raise StorageDenied(decision.reason)

        parts = path.split("/")
        parent_fd = os.dup(self._root_fd)
        file_fd = None
        try:
            # Traverse only pre-existing directories, anchored to the trusted root.
            for segment in parts[:-1]:
                next_fd = os.open(
                    segment,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                    dir_fd=parent_fd,
                )
                os.close(parent_fd)
                parent_fd = next_fd

            # O_EXCL is the authoritative no-overwrite check; O_NOFOLLOW is defense in depth.
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
            file_fd = os.open(parts[-1], flags, 0o600, dir_fd=parent_fd)
            metadata = os.fstat(file_fd)
            if not stat.S_ISREG(metadata.st_mode) or (metadata.st_mode & 0o077):
                raise StorageDenied("unsafe_created_file_mode")

            view = memoryview(content)
            while view:
                written = os.write(file_fd, view)
                if written <= 0:
                    raise OSError("short_write")
                view = view[written:]
            os.fsync(file_fd)
            os.fsync(parent_fd)
            return {
                "created": True,
                "path": path,
                "mode": stat.S_IMODE(metadata.st_mode),
                "bytes_written": len(content),
                "authorization_ref": grant.approval_ref,
            }
        except FileExistsError as exc:
            raise StorageDenied("create_only_existing_target_denied") from exc
        except OSError as exc:
            # No fallback, overwrite, unlink, shell, or alternate path is attempted.
            raise StorageDenied("filesystem_create_denied") from exc
        finally:
            if file_fd is not None:
                os.close(file_fd)
            os.close(parent_fd)
