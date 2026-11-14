"""ERIA compiled inspection storage.

Persists derived Æị records under storage/compiled without copying, moving,
or modifying original source files. Each artifact has a separate provenance
manifest and content digest.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .aei import AeiError, inspect_file

SENSITIVE_PATH = re.compile(
    r"(^|[/_.-])(.env|secrets?|credentials?|private[_-]?key|id_rsa)([/_.-]|$)",
    re.IGNORECASE,
)


class AeiStorage:
    def __init__(self, repository: str | Path):
        self.root = Path(repository).expanduser().resolve(strict=True)
        if not self.root.is_dir():
            raise AeiError("Storage repository root is not a directory.")
        self.base = self.root / "storage"
        self.compiled = self.base / "compiled"
        self.manifests = self.base / "manifests"

    def _prepare(self) -> None:
        for directory in (self.base, self.compiled, self.manifests):
            if directory.exists() and directory.is_symlink():
                raise AeiError("Storage directories cannot be symbolic links.")
            directory.mkdir(parents=True, exist_ok=True)
            resolved = directory.resolve(strict=True)
            if resolved == self.root or self.root not in resolved.parents:
                raise AeiError("Storage directory escapes the repository root.")

    @staticmethod
    def _write_new(path: Path, payload: bytes) -> None:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(path, flags, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
        except Exception:
            try:
                path.unlink()
            except OSError:
                pass
            raise

    def compile(self, relative_path: str) -> dict[str, Any]:
        if not relative_path or SENSITIVE_PATH.search(relative_path):
            raise AeiError("Credential-like paths are not eligible for compiled storage.")
        result = inspect_file(self.root, relative_path)
        self._prepare()
        created = datetime.now(timezone.utc).isoformat()
        identifier = uuid.uuid4().hex
        stem = f"{created[:10]}-{result.source_sha256[:12]}-{identifier}"
        record = {
            "schema": "eria.compiled-inspection/1.0",
            "created_at": created,
            "translator": "Æị",
            "compiled_by": "ERIA/PANTHEON",
            "source": {
                "path": result.source_path,
                "format": result.format,
                "size_bytes": result.size_bytes,
                "sha256": result.source_sha256,
                "authority": result.source_authority,
            },
            "derived": {
                "authority": result.derived_authority,
                "status": result.status,
                "interpretation": result.interpretation,
                "limitations": list(result.limitations),
                "data": result.data,
            },
            "preservation": {
                "source_modified": False,
                "source_copied": False,
                "source_deleted": False,
                "git_history_modified": False,
            },
        }
        artifact_bytes = (
            json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        ).encode("utf-8")
        artifact_sha = hashlib.sha256(artifact_bytes).hexdigest()
        artifact_name = stem + ".json"
        manifest = {
            "schema": "eria.compiled-manifest/1.0",
            "artifact": f"compiled/{artifact_name}",
            "artifact_sha256": artifact_sha,
            "source": record["source"],
            "created_at": created,
            "transformations": ["Æị read-only inspection", "JSON serialization"],
            "authority": "NON_AUTHORITATIVE",
        }
        manifest_bytes = (
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        ).encode("utf-8")
        manifest_name = stem + ".manifest.json"
        artifact_path = self.compiled / artifact_name
        manifest_path = self.manifests / manifest_name
        self._write_new(artifact_path, artifact_bytes)
        try:
            self._write_new(manifest_path, manifest_bytes)
        except Exception:
            artifact_path.unlink(missing_ok=True)
            raise
        return {
            "status": "stored",
            "artifact": f"storage/compiled/{artifact_name}",
            "manifest": f"storage/manifests/{manifest_name}",
            "artifact_sha256": artifact_sha,
            "source": record["source"],
            "source_modified": False,
            "authority": "NON_AUTHORITATIVE",
        }
