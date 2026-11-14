#!/usr/bin/env python3
"""ERIA Repository Representation Forge.

Builds an on-demand, deterministic-structure inventory of a selected Git
worktree. It reads source files, never executes them, never alters Git or
source files, and writes a report only to a caller-selected new path.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import stat
import sys
import tomllib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from eria_repository_conversation import Repository, RepoError  # noqa: E402

SCHEMA = "eria.repository-forge/1"
MAX_PARSE_BYTES = 2 * 1024 * 1024
MAX_SYMBOLS_PER_FILE = 500
SKIP_DIRS = {
    ".git", ".gradle", ".idea", "node_modules", "__pycache__", ".venv",
    "venv", "build", "dist", ".pytest_cache",
}
SECRET_NAME = re.compile(
    r"(^\.env($|\.)|secret|credential|token|password|private[_-]?key|"
    r"(^|\.)keystore|\.jks$|\.p12$|\.pem$)",
    re.I,
)
SECRET_VALUE = re.compile(
    r"(?i)((?:api[_-]?key|access[_-]?token|password|client_secret|"
    r"private[_-]?key)\s*[:=]\s*)(['\"]?)([A-Za-z0-9_\-./+=]{8,})\2"
)
LANGUAGES = {
    ".py": "Python", ".sh": "Bash", ".kt": "Kotlin", ".kts": "Kotlin DSL",
    ".java": "Java", ".c": "C", ".h": "C/C++ header", ".hpp": "C++ header",
    ".cpp": "C++", ".rs": "Rust", ".go": "Go", ".swift": "Swift",
    ".js": "JavaScript", ".jsx": "JavaScript/React", ".ts": "TypeScript",
    ".tsx": "TypeScript/React", ".html": "HTML", ".css": "CSS",
    ".json": "JSON", ".jsonl": "JSON Lines", ".yaml": "YAML",
    ".yml": "YAML", ".toml": "TOML", ".xml": "XML", ".gradle": "Gradle",
    ".md": "Markdown", ".txt": "Text", ".sql": "SQL", ".csv": "CSV",
    ".xml": "XML", ".properties": "Java properties",
}
GENERIC_DECLARATION = re.compile(
    r"^\s*(?:export\s+)?(?:(?:public|private|protected|internal|open|abstract|"
    r"data|sealed|final|static)\s+)*(?:class|interface|object|enum\s+class|"
    r"fun|function|def|struct|trait|type|record)\s+([A-Za-z_$][\w$]*)",
    re.M,
)
IMPORT_LINE = re.compile(
    r"^\s*(?:import\s+([^;#]+)|from\s+([A-Za-z0-9_.]+)\s+import\s+[^#]+)",
    re.M,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def redact(text: str) -> str:
    return SECRET_VALUE.sub(
        lambda m: f"{m.group(1)}{m.group(2)}[REDACTED]{m.group(2)}",
        text,
    )


def _safe_rel(root: Path, relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("Repository inventory returned an unsafe relative path")
    candidate = root / rel
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("Path escapes the selected repository") from exc
    return candidate


def _sha256_file(path: Path, *, capture_text: bool) -> tuple[str, int, bytes | None]:
    digest = hashlib.sha256()
    size = 0
    buffer = bytearray() if capture_text else None
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
                size += len(chunk)
                if buffer is not None:
                    if size <= MAX_PARSE_BYTES:
                        buffer.extend(chunk)
                    else:
                        buffer = None
    except OSError as exc:
        raise ValueError("File became unavailable during repository extraction") from exc
    return digest.hexdigest(), size, bytes(buffer) if buffer is not None else None


def _skip_reason(relative: str) -> str | None:
    parts = Path(relative).parts
    if any(part in SKIP_DIRS for part in parts):
        return "generated-or-cache-directory"
    if SECRET_NAME.search(Path(relative).name):
        return "sensitive-name-restricted"
    return None


def _extract_structure(relative: str, raw: bytes) -> dict[str, Any]:
    result: dict[str, Any] = {
        "kind": "opaque",
        "symbols": [],
        "imports": [],
        "headings": [],
        "top_level_keys": [],
        "parse_status": "not-applicable",
    }
    if b"\0" in raw[:8192]:
        result["kind"] = "binary"
        result["parse_status"] = "binary-not-decoded"
        return result
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        result["kind"] = "binary"
        result["parse_status"] = "non-utf8-not-decoded"
        return result

    text = redact(text)
    suffix = Path(relative).suffix.lower()
    result["kind"] = "text"
    result["parse_status"] = "structural-extraction-only"

    if suffix == ".py":
        result["kind"] = "python-source"
        try:
            tree = ast.parse(text, filename=relative)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    result["symbols"].append({
                        "kind": "class" if isinstance(node, ast.ClassDef) else "function",
                        "name": node.name,
                        "line": node.lineno,
                    })
                elif isinstance(node, ast.Import):
                    result["imports"].extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    result["imports"].append(node.module)
            result["parse_status"] = "python-ast-parsed-without-execution"
        except SyntaxError as exc:
            result["parse_status"] = "syntax-error"
            result["parse_note"] = f"line {exc.lineno}: {exc.msg}"
    elif suffix in {".md", ".markdown"}:
        result["kind"] = "documentation"
        result["headings"] = [
            {"level": len(match.group(1)), "text": match.group(2).strip()[:180]}
            for match in re.finditer(r"^(#{1,6})\s+(.+)$", text, re.M)
        ][:MAX_SYMBOLS_PER_FILE]
    elif suffix == ".json":
        result["kind"] = "structured-json"
        try:
            value = json.loads(text)
            if isinstance(value, dict):
                result["top_level_keys"] = sorted(str(k)[:120] for k in value.keys())[:MAX_SYMBOLS_PER_FILE]
            elif isinstance(value, list):
                result["top_level_keys"] = ["<array>"]
            result["parse_status"] = "json-parsed-with-values-omitted"
        except json.JSONDecodeError as exc:
            result["parse_status"] = "syntax-error"
            result["parse_note"] = f"line {exc.lineno}: {exc.msg}"
    elif suffix == ".toml":
        result["kind"] = "structured-toml"
        try:
            value = tomllib.loads(text)
            result["top_level_keys"] = sorted(str(k)[:120] for k in value.keys())[:MAX_SYMBOLS_PER_FILE]
            result["parse_status"] = "toml-parsed-with-values-omitted"
        except tomllib.TOMLDecodeError:
            result["parse_status"] = "syntax-error"
    elif suffix == ".xml":
        result["kind"] = "structured-xml"
        try:
            root = ET.fromstring(text)
            tags = {root.tag}
            tags.update(node.tag for node in root.iter())
            result["top_level_keys"] = sorted(str(tag)[:120] for tag in tags)[:MAX_SYMBOLS_PER_FILE]
            result["parse_status"] = "xml-parsed-with-text-omitted"
        except ET.ParseError:
            result["parse_status"] = "syntax-error"
    else:
        if suffix in {".kt", ".kts"}:
            result["kind"] = "kotlin-source"
        elif suffix in {".java"}:
            result["kind"] = "java-source"
        elif suffix in {".js", ".jsx", ".ts", ".tsx"}:
            result["kind"] = "javascript-or-typescript-source"
        result["symbols"] = [
            {"kind": "declaration", "name": match.group(1)}
            for match in GENERIC_DECLARATION.finditer(text)
        ][:MAX_SYMBOLS_PER_FILE]
        result["imports"] = [
            (match.group(1) or match.group(2)).strip().strip('"\'')
            for match in IMPORT_LINE.finditer(text)
        ][:MAX_SYMBOLS_PER_FILE]
    result["symbols"] = result["symbols"][:MAX_SYMBOLS_PER_FILE]
    result["imports"] = sorted(set(result["imports"]))[:MAX_SYMBOLS_PER_FILE]
    return result


def _resolve_local_import(root: Path, source: str, name: str) -> str | None:
    source_path = Path(source)
    candidates: list[Path] = []
    if name.startswith("."):
        base = (root / source_path).parent
        stem = (base / name).resolve()
        candidates.extend([Path(str(stem) + ext) for ext in (".py", ".kt", ".java", ".js", ".ts", ".tsx")])
        candidates.extend([stem / "__init__.py", stem / "index.js", stem / "index.ts"])
    else:
        module = name.split(" as ", 1)[0].strip()
        module_path = Path(*module.split("."))
        candidates.extend([
            root / (str(module_path) + ".py"),
            root / module_path / "__init__.py",
        ])
        suffix = Path(source).suffix.lower()
        if suffix in {".kt", ".java"}:
            candidates.append(root / (str(module_path) + ".kt"))
            candidates.append(root / (str(module_path) + ".java"))
    for candidate in candidates:
        try:
            if candidate.is_symlink():
                continue
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(root)
            if resolved.is_file() and not resolved.is_symlink():
                return resolved.relative_to(root).as_posix()
        except (OSError, ValueError):
            continue
    return None


def forge_repository(repository: Repository) -> dict[str, Any]:
    """Return a complete safe inventory and structural representation."""
    root = repository.root.resolve(strict=True)
    paths = repository.files()
    files: list[dict[str, Any]] = []
    relationships: list[dict[str, str]] = []
    language_counts: dict[str, int] = {}
    total_bytes = 0

    try:
        head = repository.git("rev-parse", "--short", "HEAD").strip()
    except RepoError:
        head = "unavailable"
    try:
        branch = repository.git("branch", "--show-current").strip() or "detached"
    except RepoError:
        branch = "unavailable"

    for relative in paths:
        candidate = _safe_rel(root, relative)
        try:
            st = candidate.lstat()
        except OSError:
            files.append({"path": relative, "classification": "UNAVAILABLE"})
            continue
        if stat.S_ISLNK(st.st_mode):
            files.append({
                "path": relative, "classification": "RESTRICTED",
                "reason": "symlink-not-followed", "size_bytes": st.st_size,
            })
            continue
        if not stat.S_ISREG(st.st_mode):
            files.append({"path": relative, "classification": "NON_REGULAR_SKIPPED"})
            continue

        reason = _skip_reason(relative)
        language = LANGUAGES.get(Path(relative).suffix.lower(), "Other")
        language_counts[language] = language_counts.get(language, 0) + 1
        item: dict[str, Any] = {
            "path": relative,
            "language_or_format": language,
            "size_bytes": st.st_size,
        }
        if reason:
            item.update({"classification": "RESTRICTED" if reason == "sensitive-name-restricted"
                         else "EXCLUDED_FROM_DEEP_PARSE", "reason": reason})
            files.append(item)
            continue

        try:
            digest, size, raw = _sha256_file(candidate, capture_text=st.st_size <= MAX_PARSE_BYTES)
            total_bytes += size
            item.update({
                "classification": "OBSERVED",
                "sha256": digest,
                "size_bytes": size,
                "parse_status": "size-limit-metadata-only" if raw is None else "pending",
            })
            if raw is not None:
                structure = _extract_structure(relative, raw)
                item["structure"] = structure
                item["parse_status"] = structure["parse_status"]
                for imported in structure["imports"]:
                    target = _resolve_local_import(root, relative, imported)
                    if target:
                        relationships.append({
                            "from": relative, "to": target,
                            "kind": "resolved-local-import", "evidence": imported,
                        })
            files.append(item)
        except (OSError, ValueError) as exc:
            item.update({"classification": "UNAVAILABLE", "reason": type(exc).__name__})
            files.append(item)

    counts: dict[str, int] = {}
    for item in files:
        key = item["classification"]
        counts[key] = counts.get(key, 0) + 1

    return {
        "schema": SCHEMA,
        "generated_at": utc_now(),
        "repository": {
            "name": root.name,
            "head": head,
            "branch": branch,
            "inventory_basis": "git ls-files --cached --others --exclude-standard",
        },
        "summary": {
            "files_seen": len(paths),
            "files_by_classification": counts,
            "files_by_language_or_format": dict(sorted(language_counts.items())),
            "bytes_hashed": total_bytes,
            "resolved_local_import_relationships": len(relationships),
        },
        "files": files,
        "relationships": relationships,
        "interpretation_contract": {
            "observations": "Hashes, paths, sizes, file formats, syntax nodes, and resolved imports are directly observed.",
            "inferences": "Any architectural or semantic conclusion must be separately labeled INFERRED and cite supporting file paths and lines.",
            "source_authority": "The forge does not assert that source-code comments, documentation, or claims are true.",
        },
        "safety": {
            "source_files_modified": False,
            "git_history_modified": False,
            "code_executed": False,
            "network_accessed": False,
            "secret_named_files_read": False,
            "symlinks_followed": False,
            "output_written": False,
        },
        "limitations": [
            "On-demand snapshot only; this is not an always-running filesystem watcher.",
            "The forge scans tracked and non-ignored untracked files reported by Git; ignored files and Git internals are outside this inventory.",
            "Sensitive-name files are listed as restricted metadata only and are not opened or hashed.",
            "Large files are fully hashed but not structurally parsed above the configured parse-size limit.",
            "Parsing is structural and deterministic; no embedded general-purpose AI model or semantic correctness proof is claimed.",
            "Dependencies and local imports are partial evidence; dynamic loading and runtime behavior are not inferred.",
        ],
    }


def write_forge(report: dict[str, Any], output: str | Path, repository_root: Path) -> Path:
    """Write a JSON representation to a new path outside the scanned worktree."""
    target = Path(output).expanduser().absolute()
    root = repository_root.resolve(strict=True)
    try:
        target.resolve(strict=False).relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("Forge output must be outside the repository being scanned")
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Refusing to overwrite forge output: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    report["safety"]["output_written"] = True
    with target.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--output", help="New JSON output path outside the selected repository")
    args = parser.parse_args()
    try:
        repository = Repository(args.repository)
        report = forge_repository(repository)
        if args.output:
            path = write_forge(report, args.output, repository.root)
            print(json.dumps({"status": "forged", "output": str(path),
                              "summary": report["summary"]}, indent=2))
        else:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (RepoError, OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
