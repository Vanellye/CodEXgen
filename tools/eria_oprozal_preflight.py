#!/usr/bin/env python3
"""Fail-closed, non-executing preflight for Oprozal faculty candidates.

This is deliberately not an execution sandbox. It parses Python source without
importing, compiling to bytecode, or executing the candidate. Actual execution
remains disabled until a separately reviewed OS sandbox and trusted PONS grant
verifier are available.
"""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Any


MAX_SOURCE_BYTES = 1_000_000
SCHEMA = "eria.oprozal.preflight/1.0"


class PreflightError(ValueError):
    pass


def _safe_source(root: Path, relative_path: str) -> tuple[Path, bytes]:
    if not relative_path or "\\" in relative_path:
        raise PreflightError("source_path_must_be_relative_posix")
    rel = Path(relative_path)
    if rel.is_absolute() or any(part in ("", ".", "..") for part in rel.parts):
        raise PreflightError("source_path_traversal_rejected")
    repo = root.resolve()
    path = (repo / rel).resolve()
    if repo not in path.parents:
        raise PreflightError("source_path_escapes_repository")
    if path.is_symlink() or not path.is_file():
        raise PreflightError("source_must_be_regular_non_symlink_file")
    size = path.stat().st_size
    if size > MAX_SOURCE_BYTES:
        raise PreflightError("source_exceeds_size_limit")
    raw = path.read_bytes()
    if b"\x00" in raw[:8192]:
        raise PreflightError("binary_source_not_supported")
    return path, raw


def inspect_python(root: Path, relative_path: str, source_revision: str) -> dict[str, Any]:
    """Return a source-hash-bound static syntax result; never execute source."""
    path, raw = _safe_source(root, relative_path)
    digest = hashlib.sha256(raw).hexdigest()
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "runner": "AST_STATIC_PREFLIGHT",
        "execution_performed": False,
        "source_write_performed": False,
        "source_path": relative_path,
        "source_sha256": digest,
        "source_revision": source_revision or "unknown",
        "source_authority": "NON_AUTHORITATIVE",
        "language": "python",
        "status": "STATIC_CHECKS_PASSED",
        "checks": {
            "path_containment": "PASS",
            "size_limit": "PASS",
            "binary_detection": "PASS",
            "sha256": "PASS",
            "python_ast_parse": "PENDING",
        },
        "diagnostics": [],
    }
    try:
        ast.parse(raw.decode("utf-8"), filename=relative_path, mode="exec")
        result["checks"]["python_ast_parse"] = "PASS"
    except UnicodeDecodeError as exc:
        result["checks"]["python_ast_parse"] = "FAIL"
        result["status"] = "STATIC_CHECKS_FAILED"
        result["diagnostics"].append({
            "kind": "encoding_error", "line": None, "message": str(exc)
        })
    except SyntaxError as exc:
        result["checks"]["python_ast_parse"] = "FAIL"
        result["status"] = "STATIC_CHECKS_FAILED"
        result["diagnostics"].append({
            "kind": "syntax_error",
            "line": exc.lineno,
            "column": exc.offset,
            "message": exc.msg,
        })
    return result
