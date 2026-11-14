#!/usr/bin/env python3
"""Æị: read-only, provenance-preserving file and database interpreter.

This is a deterministic format adapter, not a natural-language model. It reads
local files, emits a derived JSON description, and never edits the source.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sqlite3
import sys
try:
    import tomllib
except ImportError:  # Python 3.10 compatibility
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

VERSION = "0.1.0"
DEFAULT_MAX_BYTES = 10 * 1024 * 1024
DEFAULT_ROW_LIMIT = 100
TEXT_SUFFIXES = {
    ".py", ".sh", ".kt", ".java", ".c", ".h", ".hpp", ".cpp", ".rs",
    ".go", ".js", ".ts", ".html", ".css", ".md", ".txt", ".ptn",
    ".yaml", ".yml", ".toml", ".ini", ".cfg", ".gradle", ".kts",
    ".sql", ".xml", ".json", ".csv", ".log",
}
SQLITE_SUFFIXES = {".db", ".sqlite", ".sqlite3"}


class AeiError(ValueError):
    """A file could not be safely inspected or decoded."""


@dataclass(frozen=True)
class AeiResult:
    translator: str
    version: str
    status: str
    source_path: str
    format: str
    size_bytes: int
    source_sha256: str
    source_authority: str
    derived_authority: str
    interpretation: str
    data: Any
    limitations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["limitations"] = list(self.limitations)
        return value


def _safe_path(root: Path, relative_path: str) -> Path:
    base = root.resolve(strict=True)
    candidate = base / relative_path
    # Reject symlink traversal rather than relying only on the resolved target.
    current = base
    for part in Path(relative_path).parts:
        if part in {"", ".", ".."}:
            if part == "..":
                raise AeiError("Path traversal is not allowed.")
            continue
        current = current / part
        if current.is_symlink():
            raise AeiError("Symbolic links are not followed by Æị.")
    resolved = candidate.resolve(strict=True)
    if resolved == base or base not in resolved.parents:
        raise AeiError("Requested path escapes the selected repository root.")
    if not resolved.is_file():
        raise AeiError("Requested path is not a regular file.")
    return resolved


def _xml_value(element: ET.Element) -> dict[str, Any]:
    result: dict[str, Any] = {"tag": element.tag}
    if element.attrib:
        result["attributes"] = dict(element.attrib)
    text = (element.text or "").strip()
    if text:
        result["text"] = text
    children = [_xml_value(child) for child in list(element)]
    if children:
        result["children"] = children
    return result


def _sqlite_read(path: Path, row_limit: int) -> dict[str, Any]:
    uri = "file:" + quote(str(path), safe="/") + "?mode=ro"
    try:
        connection = sqlite3.connect(uri, uri=True, timeout=2.0)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA query_only=ON")
            tables = connection.execute(
                "SELECT name, sql FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            ).fetchall()
            output = []
            for table in tables:
                name = table["name"]
                escaped = '"' + name.replace('"', '""') + '"'
                columns = [
                    dict(row) for row in connection.execute(
                        f"PRAGMA table_info({escaped})"
                    ).fetchall()
                ]
                rows = [
                    dict(row) for row in connection.execute(
                        f"SELECT * FROM {escaped} LIMIT ?", (row_limit,)
                    ).fetchall()
                ]
                output.append({
                    "table": name,
                    "schema_sql": table["sql"],
                    "columns": columns,
                    "rows_preview": rows,
                    "preview_limit": row_limit,
                })
            return {"tables": output, "table_count": len(output)}
        finally:
            connection.close()
    except sqlite3.Error as exc:
        raise AeiError(f"SQLite read-only inspection failed: {exc}") from exc


def _decode(raw: bytes, suffix: str, path: Path, row_limit: int) -> tuple[str, str, Any, tuple[str, ...]]:
    if raw.startswith(b"SQLite format 3\x00") or suffix in SQLITE_SUFFIXES:
        return "SQLite", "decoded", _sqlite_read(path, row_limit), ()
    if b"\x00" in raw[:8192]:
        return "binary/unknown", "metadata_only", {
            "binary": True,
            "header_hex": raw[:32].hex(),
        }, ("Binary payload was not decoded.",)

    try:
        text = raw.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        return "binary/unknown", "metadata_only", {
            "binary": True,
            "header_hex": raw[:32].hex(),
        }, ("File is not valid UTF-8; source bytes were preserved.",)

    if suffix == ".json":
        try:
            value = json.loads(text)
        except json.JSONDecodeError as exc:
            raise AeiError(f"Invalid JSON at line {exc.lineno}, column {exc.colno}.") from exc
        count = len(value) if isinstance(value, (list, dict)) else 1
        return "JSON", "decoded", {"top_level_type": type(value).__name__,
                                    "item_count": count, "value": value}, ()
    if suffix == ".csv":
        reader = csv.DictReader(io.StringIO(text, newline=""))
        rows = []
        for index, row in enumerate(reader):
            if index >= row_limit:
                break
            rows.append(dict(row))
        return "CSV", "decoded", {
            "columns": reader.fieldnames or [],
            "rows_preview": rows,
            "preview_limit": row_limit,
        }, ()
    if suffix == ".xml":
        try:
            root = ET.fromstring(text)
        except ET.ParseError as exc:
            raise AeiError(f"Invalid XML: {exc}") from exc
        return "XML", "decoded", _xml_value(root), ()
    if suffix == ".toml":
        if tomllib is None:
            return "TOML", "unsupported_dependency", {"text_preview": text[:4000]}, (
                "Install tomli on Python 3.10 to decode TOML; source bytes remain unchanged.",
            )
        try:
            value = tomllib.loads(text)
        except Exception as exc:
            raise AeiError(f"Invalid TOML: {exc}") from exc
        return "TOML", "decoded", value, ()
    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # optional dependency; safe loader only
        except ImportError:
            return "YAML", "unsupported_dependency", {
                "text_preview": text[:4000]
            }, ("Install PyYAML to decode YAML; no unsafe loader is used.",)
        try:
            value = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise AeiError(f"Invalid YAML: {exc}") from exc
        return "YAML", "decoded", value, ()
    if suffix in TEXT_SUFFIXES or not suffix:
        lines = text.splitlines()
        return ("Source/text" if suffix in TEXT_SUFFIXES else "UTF-8 text",
                "decoded",
                {"line_count": len(lines), "text_preview": "\n".join(lines[:80]),
                 "preview_lines": min(len(lines), 80)},
                ("Source code is described, not executed or semantically rewritten.",)
                if suffix in TEXT_SUFFIXES else ())
    return "UTF-8 text", "decoded", {"text_preview": text[:4000]}, (
        "Unknown extension; returned a bounded text preview only.",
    )


def inspect_file(root: str | Path, relative_path: str, *,
                 max_bytes: int = DEFAULT_MAX_BYTES,
                 row_limit: int = DEFAULT_ROW_LIMIT) -> AeiResult:
    if max_bytes < 1 or row_limit < 1:
        raise AeiError("max_bytes and row_limit must be positive.")
    base = Path(root).expanduser().resolve(strict=True)
    path = _safe_path(base, relative_path)
    size = path.stat().st_size
    if size > max_bytes:
        raise AeiError(f"File exceeds Æị size limit ({size} > {max_bytes} bytes).")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    fmt, status, data, limitations = _decode(
        raw, path.suffix.lower(), path, row_limit
    )
    return AeiResult(
        translator="Æị",
        version=VERSION,
        status=status,
        source_path=path.relative_to(base).as_posix(),
        format=fmt,
        size_bytes=len(raw),
        source_sha256=digest,
        source_authority="NON_AUTHORITATIVE",
        derived_authority="NON_AUTHORITATIVE",
        interpretation=(
            "A read-only structural interpretation of the source. "
            "It is derived evidence, not a replacement for the original."
        ),
        data=data,
        limitations=limitations,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="repository-relative file path")
    parser.add_argument("--root", default=".", help="selected repository/filesystem root")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument("--row-limit", type=int, default=DEFAULT_ROW_LIMIT)
    args = parser.parse_args(argv)
    try:
        result = inspect_file(args.root, args.path,
                              max_bytes=args.max_bytes, row_limit=args.row_limit)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0
    except (AeiError, OSError) as exc:
        print(json.dumps({"translator": "Æị", "status": "HOLD",
                          "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
