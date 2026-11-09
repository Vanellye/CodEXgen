"""Analyze approved Python source without importing or executing it.

Generated modules are structural catalogs, not copied executable source. They contain
component names, signatures, docstrings, and SHA-256 provenance only.
"""
from __future__ import annotations
import ast
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

class AnalysisError(ValueError):
    """Raised when an approval, source, or output boundary is invalid."""

MAX_SOURCE_BYTES = 2 * 1024 * 1024

def _inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False

def _safe_roots(source_root: Path, output_root: Path) -> None:
    source = source_root.resolve(strict=True)
    output = output_root.resolve(strict=False)
    if not source.is_dir():
        raise AnalysisError(f"Source root is not a directory: {source}")
    if source == output or _inside(output, source) or _inside(source, output):
        raise AnalysisError("Source and output directories must be separate, non-overlapping trees.")
    if output.exists() and not output.is_dir():
        raise AnalysisError("Output path exists and is not a directory.")
    if output.exists() and any(output.iterdir()):
        raise AnalysisError("Output directory is not empty; choose a fresh directory to preserve prior artifacts.")

def _safe_source_path(source_root: Path, approved_path: str) -> Path:
    candidate_text = str(approved_path).strip()
    if not candidate_text or Path(candidate_text).is_absolute():
        raise AnalysisError("Approved paths must be non-empty and relative to the source root.")
    candidate = source_root / candidate_text
    if any(part in ("", ".", "..") for part in Path(candidate_text).parts):
        raise AnalysisError(f"Unsafe approved path: {approved_path}")
    if candidate.is_symlink():
        raise AnalysisError(f"Symbolic links are not accepted: {approved_path}")
    resolved = candidate.resolve(strict=True)
    if not _inside(resolved, source_root.resolve()):
        raise AnalysisError(f"Approved path escapes the source root: {approved_path}")
    if not resolved.is_file() or resolved.suffix != ".py":
        raise AnalysisError(f"Approved path must identify a regular .py file: {approved_path}")
    if resolved.stat().st_size > MAX_SOURCE_BYTES:
        raise AnalysisError(f"Source exceeds {MAX_SOURCE_BYTES} bytes: {approved_path}")
    return resolved

def _argument_names(arguments: ast.arguments) -> list[str]:
    names = [arg.arg for arg in arguments.posonlyargs]
    names.extend(arg.arg for arg in arguments.args)
    if arguments.vararg:
        names.append("*" + arguments.vararg.arg)
    names.extend(arg.arg for arg in arguments.kwonlyargs)
    if arguments.kwarg:
        names.append("**" + arguments.kwarg.arg)
    return names

def _component(node: ast.AST) -> dict[str, Any] | None:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return {
            "kind": "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function",
            "name": node.name,
            "line": node.lineno,
            "arguments": _argument_names(node.args),
            "returns": ast.unparse(node.returns) if node.returns is not None else None,
            "docstring": ast.get_docstring(node, clean=True),
        }
    if isinstance(node, ast.ClassDef):
        return {
            "kind": "class",
            "name": node.name,
            "line": node.lineno,
            "bases": [ast.unparse(base) for base in node.bases],
            "methods": [
                child.name for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            ],
            "docstring": ast.get_docstring(node, clean=True),
        }
    return None

def analyze_approved_files(source_root: str | Path, approved_paths: list[str]) -> list[dict[str, Any]]:
    """Parse only explicitly listed files. No imports, eval, exec, or source execution."""
    root = Path(source_root).resolve(strict=True)
    if not approved_paths:
        raise AnalysisError("At least one explicitly approved source file is required.")
    seen: set[str] = set()
    records: list[dict[str, Any]] = []
    for approved in approved_paths:
        path = _safe_source_path(root, approved)
        relative = path.relative_to(root).as_posix()
        if relative in seen:
            raise AnalysisError(f"Duplicate approved path: {relative}")
        seen.add(relative)
        raw = path.read_bytes()
        try:
            source = raw.decode("utf-8")
            tree = ast.parse(source, filename=relative, mode="exec")
        except (UnicodeDecodeError, SyntaxError) as exc:
            raise AnalysisError(f"Cannot parse approved file {relative}: {exc}") from exc
        components = [item for node in tree.body if (item := _component(node)) is not None]
        records.append({
            "source_path": relative,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "size_bytes": len(raw),
            "components": components,
        })
    return records

def _module_filename(source_path: str) -> str:
    stem = Path(source_path).stem.lower()
    safe = re.sub(r"[^a-z0-9_]+", "_", stem).strip("_") or "source"
    digest = hashlib.sha256(source_path.encode("utf-8")).hexdigest()[:8]
    return f"{safe}_{digest}_catalog.py"

def _render_catalog(record: dict[str, Any], generated_at: str) -> str:
    payload = {
        "source_path": record["source_path"],
        "source_sha256": record["sha256"],
        "generated_at_utc": generated_at,
        "components": record["components"],
    }
    return (
        '"""Generated Pantheon structural catalog; source code was not copied or executed."""\n'
        f"CATALOG = {json.dumps(payload, ensure_ascii=False, indent=2)}\n"
    )

def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".pantheon-", dir=str(path.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise

def generate_pantheon_modules(
    source_root: str | Path,
    output_root: str | Path,
    approved_paths: list[str],
) -> dict[str, Any]:
    """Generate structural catalogs in a distinct, initially empty directory."""
    source = Path(source_root).resolve(strict=True)
    output = Path(output_root).resolve(strict=False)
    _safe_roots(source, output)
    records = analyze_approved_files(source, approved_paths)
    generated_at = datetime.now(timezone.utc).isoformat()
    output.mkdir(parents=True, exist_ok=True)
    artifacts: list[dict[str, str]] = []
    for record in records:
        filename = _module_filename(record["source_path"])
        content = _render_catalog(record, generated_at)
        compile(content, filename, "exec")
        _atomic_write(output / filename, content)
        artifacts.append({
            "path": filename,
            "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "source_path": record["source_path"],
        })
    manifest = {
        "format": "pantheon-source-catalog-v1",
        "generated_at_utc": generated_at,
        "execution_performed": False,
        "source_root_label": source.name,
        "approved_sources": records,
        "generated_artifacts": artifacts,
    }
    _atomic_write(output / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return manifest
