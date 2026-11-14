#!/usr/bin/env python3
"""ERIA Æ Database Translator.

Read-only source ingestion with separate, non-overwriting derived exports.
The engine is filesystem-path agnostic: adapters operate on readable paths,
not on a particular mount type. Unknown/binary formats remain lossless opaque
payloads rather than being guessed or silently re-encoded.
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import os
import sqlite3
import sys
import tomllib
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "1.0.0"
MAX_TEXT_BYTES = 64 * 1024 * 1024
CANONICAL = "eria.canonical/1"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_output(path: Path) -> Path:
    path = path.expanduser().absolute()
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def read_bytes(path: Path) -> bytes:
    if path.is_symlink():
        raise ValueError("Symlink sources are not followed")
    if not path.is_file():
        raise ValueError("Source must be a regular file")
    return path.read_bytes()


def sniff_format(path: Path, raw: bytes) -> str:
    ext = path.suffix.lower()
    if ext in (".json",): return "json"
    if ext in (".jsonl", ".ndjson"): return "jsonl"
    if ext in (".csv",): return "csv"
    if ext in (".tsv",): return "tsv"
    if ext in (".xml",): return "xml"
    if ext in (".toml",): return "toml"
    if ext in (".txt", ".md", ".log"): return "text"
    if ext in (".sqlite", ".sqlite3", ".db"): return "sqlite"
    if raw.startswith(b"SQLite format 3\\x00"): return "sqlite"
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        return "binary"
    return "text"


def decode_source(path: Path, raw: bytes, fmt: str) -> dict[str, Any]:
    if fmt == "binary":
        return {"kind": "opaque", "encoding": "base64",
                "data": base64.b64encode(raw).decode("ascii")}
    if fmt == "sqlite":
        # SQLite input is opened immutable/read-only; no SQL writes are exposed.
        uri = path.resolve().as_uri() + "?mode=ro&immutable=1"
        con = sqlite3.connect(uri, uri=True)
        try:
            tables = [r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )]
            payload = {}
            for table in tables:
                quoted = '"' + table.replace('"', '""') + '"'
                cols = [r[1] for r in con.execute(f"PRAGMA table_info({quoted})")]
                rows = con.execute(f"SELECT * FROM {quoted}").fetchmany(100000)
                payload[table] = {"columns": cols, "rows": rows}
            return {"kind": "database", "engine": "sqlite",
                    "tables": payload, "integrity": con.execute(
                        "PRAGMA integrity_check"
                    ).fetchone()[0]}
        finally:
            con.close()
    text = raw.decode("utf-8-sig")
    if fmt == "json":
        return {"kind": "document", "value": json.loads(text)}
    if fmt == "jsonl":
        return {"kind": "records", "value": [
            json.loads(line) for line in text.splitlines() if line.strip()
        ]}
    if fmt in ("csv", "tsv"):
        dialect = "excel-tab" if fmt == "tsv" else "excel"
        return {"kind": "table", "columns": None,
                "rows": list(csv.DictReader(text.splitlines(), dialect=dialect))}
    if fmt == "xml":
        root = ET.fromstring(text)
        def node(el):
            return {"tag": el.tag, "attributes": dict(el.attrib),
                    "text": el.text, "children": [node(c) for c in el]}
        return {"kind": "document", "value": node(root)}
    if fmt == "toml":
        return {"kind": "document", "value": tomllib.loads(text)}
    return {"kind": "text", "value": text}


def canonical_envelope(path: Path, raw: bytes) -> dict[str, Any]:
    fmt = sniff_format(path, raw)
    if len(raw) > MAX_TEXT_BYTES and fmt not in ("binary", "sqlite"):
        raise ValueError(f"Text source exceeds {MAX_TEXT_BYTES} byte safety limit")
    body = decode_source(path, raw, fmt)
    return {
        "schema": CANONICAL,
        "translator": {"name": "ERIA Æ Database Translator", "version": VERSION},
        "source": {"path": str(path.absolute()), "name": path.name,
                   "format": fmt, "size_bytes": len(raw), "sha256": sha256(raw),
                   "encoding": "utf-8" if fmt not in ("binary", "sqlite") else None},
        "captured_at": utc_now(),
        "content": body,
        "preservation": {"source_modified": False, "source_deleted": False,
                         "git_history_modified": False}
    }


def export_payload(envelope: dict[str, Any], target_format: str) -> bytes:
    content = envelope["content"]
    if target_format == "json":
        return (json.dumps(envelope, ensure_ascii=False, indent=2,
                           default=str) + "\n").encode("utf-8")
    if target_format == "txt":
        if content["kind"] == "text":
            value = content["value"]
        else:
            value = json.dumps(content, ensure_ascii=False, indent=2, default=str)
        return (str(value) + "\n").encode("utf-8")
    if target_format == "csv":
        if content["kind"] == "table":
            rows = content["rows"]
        elif content["kind"] == "records":
            rows = content["value"]
        elif content["kind"] == "database":
            raise ValueError("Choose a table before exporting a database as CSV")
        else:
            raise ValueError("CSV export requires table or record data")
        if not rows:
            return b""
        if not all(isinstance(r, dict) for r in rows):
            raise ValueError("CSV rows must be objects")
        import io
        out = io.StringIO(newline="")
        keys = list(dict.fromkeys(k for row in rows for k in row))
        writer = csv.DictWriter(out, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        return out.getvalue().encode("utf-8")
    if target_format == "jsonl":
        rows = content.get("rows") if content["kind"] == "table" else content.get("value")
        if not isinstance(rows, list):
            raise ValueError("JSONL export requires records or table data")
        return ("".join(json.dumps(r, ensure_ascii=False, default=str) + "\n"
                        for r in rows)).encode("utf-8")
    if target_format == "xml":
        root = ET.Element("eria", {"schema": CANONICAL})
        payload = ET.SubElement(root, "payload")
        payload.text = json.dumps(content, ensure_ascii=False, default=str)
        return ET.tostring(root, encoding="utf-8", xml_declaration=True)
    raise ValueError(f"Unsupported export format: {target_format}")


def translate(source: Path, output: Path, target_format: str) -> dict[str, Any]:
    raw = read_bytes(source)
    envelope = canonical_envelope(source, raw)
    result = export_payload(envelope, target_format)
    destination = safe_output(output)
    # Exclusive creation prevents races and overwrites.
    with destination.open("xb") as f:
        f.write(result)
    manifest = {
        "schema": "eria.translation-manifest/1",
        "source_path": str(source.absolute()),
        "source_sha256": envelope["source"]["sha256"],
        "source_format": envelope["source"]["format"],
        "output_path": str(destination),
        "output_sha256": sha256(result),
        "target_format": target_format,
        "translator_version": VERSION,
        "created_at": utc_now(),
        "source_modified": False
    }
    manifest_path = Path(str(destination) + ".manifest.json")
    with manifest_path.open("x", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", help="Readable regular file on any mounted filesystem")
    ap.add_argument("--to", choices=("json", "txt", "csv", "jsonl", "xml"),
                    default="json", help="Separate derived output format")
    ap.add_argument("--output", required=True, help="New output path; must not exist")
    args = ap.parse_args()
    try:
        result = translate(Path(args.source), Path(args.output), args.to)
        print(json.dumps({"status": "translated", **result}, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
