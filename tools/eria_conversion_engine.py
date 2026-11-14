#!/usr/bin/env python3
"""ERIA canonical conversion engine.

Format conversion and human-language translation are deliberately separate.
The engine never edits its source file and never executes source code.
Python standard library only.
"""
from __future__ import annotations

import argparse
import csv
import errno
import hashlib
import io
import json
import os
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol


ENGINE_VERSION = "1.0.0"
SUPPORTED_INPUTS = {"json", "csv", "txt"}
SUPPORTED_OUTPUTS = {"json", "csv", "txt"}


class ConversionError(Exception):
    """Raised when input cannot be safely converted."""


@dataclass
class TranslationResult:
    text: str
    source_language: str
    target_language: str
    provider: str
    confidence: float | None = None


class TranslationAdapter(Protocol):
    """Plug in a real translation provider; do not confuse conversion with translation."""

    name: str

    def translate(self, text: str, source_language: str,
                  target_language: str) -> TranslationResult: ...


@dataclass
class ConversionEnvelope:
    schema: str
    source: dict[str, Any]
    content_type: str
    payload: Any
    transformations: list[dict[str, Any]] = field(default_factory=list)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def detect_format(path: Path, raw: bytes) -> str:
    suffix = path.suffix.lower().lstrip(".")
    if suffix in SUPPORTED_INPUTS:
        return suffix
    sample = raw.decode("utf-8-sig", errors="replace").lstrip()
    if sample.startswith("{") or sample.startswith("["):
        return "json"
    if "," in sample.partition("\n")[0]:
        return "csv"
    return "txt"


def decode_source(raw: bytes) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            pass
    raise ConversionError("Cannot decode input as UTF-8, UTF-16 or Windows-1252.")


def load_payload(text: str, fmt: str) -> Any:
    if fmt == "json":
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ConversionError(f"Invalid JSON at line {exc.lineno}, column {exc.colno}.") from exc
    if fmt == "csv":
        return list(csv.DictReader(io.StringIO(text, newline="")))
    if fmt == "txt":
        return {"text": text}
    raise ConversionError(f"Unsupported input format: {fmt}")


def flatten_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        if all(isinstance(item, dict) for item in payload):
            return payload
        return [{"value": item} for item in payload]
    if isinstance(payload, dict):
        return [payload]
    return [{"value": payload}]


def render_payload(envelope: ConversionEnvelope, target: str) -> bytes:
    if target == "json":
        return (json.dumps(asdict(envelope), ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if target == "txt":
        payload = envelope.payload
        if isinstance(payload, dict) and set(payload) == {"text"}:
            text = str(payload["text"])
        else:
            text = json.dumps(payload, ensure_ascii=False, indent=2)
        return text.encode("utf-8")
    if target == "csv":
        rows = flatten_rows(envelope.payload)
        if not rows:
            return b""
        columns: list[str] = []
        for row in rows:
            for key in row:
                if key not in columns:
                    columns.append(str(key))
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False)
                             if isinstance(value, (dict, list)) else value
                             for key, value in row.items()})
        return stream.getvalue().encode("utf-8")
    raise ConversionError(f"Unsupported output format: {target}")


def atomic_write_new(path: Path, data: bytes) -> None:
    """Create a new output atomically; refuse to overwrite any existing file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ConversionError(f"Refusing to overwrite existing output: {path}")
    fd, temporary = tempfile.mkstemp(prefix=".eria-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as exc:
            raise ConversionError(f"Output appeared during conversion: {path}") from exc
        except OSError as exc:
            # Android shared storage may not support hard links. Fall back to
            # exclusive creation, which still guarantees no overwrite.
            unsupported = {errno.EPERM, errno.EOPNOTSUPP, errno.ENOTSUP, errno.EXDEV}
            if exc.errno not in unsupported:
                raise
            try:
                out_fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError as exists:
                raise ConversionError(f"Output appeared during conversion: {path}") from exists
            try:
                with os.fdopen(out_fd, "wb") as output:
                    output.write(data)
                    output.flush()
                    os.fsync(output.fileno())
            except Exception:
                try:
                    path.unlink()
                except OSError:
                    pass
                raise
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def convert_file(source: Path, target: Path, output_format: str,
                 ratio_marker: float = 11.11) -> tuple[Path, Path]:
    source = source.resolve()
    target = target.resolve()
    if not source.is_file():
        raise ConversionError(f"Source file does not exist: {source}")
    if source == target:
        raise ConversionError("Source and output paths must be different.")
    if output_format not in SUPPORTED_OUTPUTS:
        raise ConversionError(f"Output format must be one of: {sorted(SUPPORTED_OUTPUTS)}")

    raw = source.read_bytes()
    text, encoding = decode_source(raw)
    input_format = detect_format(source, raw)
    if input_format not in SUPPORTED_INPUTS:
        raise ConversionError(f"Unsupported detected input format: {input_format}")

    payload = load_payload(text, input_format)
    envelope = ConversionEnvelope(
        schema="eria.canonical.v1",
        source={
            "path": str(source),
            "format": input_format,
            "encoding": encoding,
            "size_bytes": len(raw),
            "sha256": sha256(raw),
        },
        content_type=input_format,
        payload=payload,
        transformations=[{
            "operation": "format_conversion",
            "engine": "ERIA",
            "engine_version": ENGINE_VERSION,
            "output_format": output_format,
            "ratio_marker": ratio_marker,
            "ratio_marker_note": "Recorded metadata only; not an accuracy or quality score.",
        }],
    )
    output_bytes = render_payload(envelope, output_format)
    atomic_write_new(target, output_bytes)

    manifest = {
        "schema": "eria.provenance.v1",
        "engine_version": ENGINE_VERSION,
        "created_unix": time.time(),
        "source": envelope.source,
        "derived": {
            "path": str(target),
            "format": output_format,
            "size_bytes": len(output_bytes),
            "sha256": sha256(output_bytes),
        },
        "validation": {
            "status": "format-rendered",
            "semantic_accuracy": "not-evaluated",
            "information_loss": "not-assessed",
        },
        "transformations": envelope.transformations,
    }
    manifest_path = target.with_name(target.name + ".eria-manifest.json")
    atomic_write_new(
        manifest_path,
        (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    )
    return target, manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description="ERIA safe canonical data converter")
    parser.add_argument("source", type=Path)
    parser.add_argument("--to", required=True, choices=sorted(SUPPORTED_OUTPUTS))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--ratio-marker", type=float, default=11.11)
    args = parser.parse_args()

    output = args.output or args.source.with_name(
        args.source.stem + ".eria-derived." + args.to
    )
    try:
        converted, manifest = convert_file(
            args.source, output, args.to, args.ratio_marker
        )
    except (ConversionError, OSError) as exc:
        parser.exit(2, f"ERIA conversion HOLD: {exc}\n")

    print(f"OUTPUT={converted}")
    print(f"MANIFEST={manifest}")
    print("SOURCE_PRESERVED=true")
    print("SEMANTIC_TRANSLATION=not-performed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
