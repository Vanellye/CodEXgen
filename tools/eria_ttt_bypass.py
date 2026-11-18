#!/usr/bin/env python3
"""ERIA TTT explicit code-translation/transmission bypass.

For explicitly classified code with bypass enabled, preserve original bytes,
skip translator and transmitter, and append a hash-only audit event outside
the repository by default. This module does not modify source files or Git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional, Union

Payload = Union[str, bytes, bytearray]
Translator = Callable[[Payload], Any]
Transmitter = Callable[[Any], Any]


class CodeTranslationBypass(Exception):
    """Control-flow exception: preserve code and skip both pipeline stages."""
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class PipelineResult:
    status: str
    payload: Payload
    source_sha256: str
    translated_payload: Any = None
    transmission_result: Any = None
    audit_path: Optional[str] = None


def _as_bytes(payload: Payload) -> bytes:
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, bytearray):
        return bytes(payload)
    if isinstance(payload, str):
        return payload.encode("utf-8")
    raise TypeError("payload must be str, bytes, or bytearray")


def _default_audit_path() -> Path:
    return Path.home() / ".eria" / "audit" / "ttt_code_bypass.jsonl"


def _write_audit(*, audit_path: Path, source_name: str, reason: str,
                 payload_bytes: bytes) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "code_translation_and_transmission_bypassed",
        "source_name": source_name,
        "reason": reason,
        "payload_bytes": len(payload_bytes),
        "source_sha256": hashlib.sha256(payload_bytes).hexdigest(),
        "translation_invoked": False,
        "transmitter_invoked": False,
        "repository_mutated": False,
    }
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def process_payload(payload: Payload, *, content_kind: str, bypass_code: bool,
                    reason: str, translator: Translator, transmitter: Transmitter,
                    source_name: str = "<memory>",
                    audit_path: Optional[Union[str, Path]] = None) -> PipelineResult:
    """Skip translation and transmission only for code with explicit opt-in."""
    if not callable(translator) or not callable(transmitter):
        raise TypeError("translator and transmitter must be callable")
    if not isinstance(content_kind, str) or not content_kind.strip():
        raise ValueError("content_kind must be a non-empty string")
    raw = _as_bytes(payload)
    digest = hashlib.sha256(raw).hexdigest()
    try:
        if content_kind.strip().lower() == "code" and bypass_code:
            if not isinstance(reason, str) or not reason.strip():
                raise ValueError("A reason is required when bypass_code=True")
            raise CodeTranslationBypass(reason.strip())
    except CodeTranslationBypass as bypass:
        path = Path(audit_path).expanduser() if audit_path else _default_audit_path()
        # Fail closed: inability to write the audit prevents a silent bypass.
        _write_audit(audit_path=path, source_name=source_name,
                     reason=bypass.reason, payload_bytes=raw)
        return PipelineResult(
            status="bypassed_local_not_transmitted",
            payload=payload,
            source_sha256=digest,
            audit_path=str(path),
        )
    translated = translator(payload)
    transmitted = transmitter(translated)
    return PipelineResult(
        status="translated_and_transmitted",
        payload=payload,
        source_sha256=digest,
        translated_payload=translated,
        transmission_result=transmitted,
    )


def _demo() -> int:
    original = b'fun main() { println("ERIA") }\n'
    calls = {"translator": 0, "transmitter": 0}

    def translator(value: Payload) -> Payload:
        calls["translator"] += 1
        return value

    def transmitter(value: Any) -> str:
        calls["transmitter"] += 1
        return "sent"

    result = process_payload(
        original, content_kind="code", bypass_code=True,
        reason="Preserve source bytes; skip translation and outbound transmission",
        translator=translator, transmitter=transmitter, source_name="demo.kt",
    )
    print("ERIA TTT bypass demonstration")
    print(f"status: {result.status}")
    print(f"source_unchanged: {result.payload == original}")
    print(f"sha256: {result.source_sha256}")
    print(f"translator_calls: {calls['translator']}")
    print(f"transmitter_calls: {calls['transmitter']}")
    print(f"audit: {result.audit_path}")
    return 0 if (
        result.status == "bypassed_local_not_transmitted"
        and result.payload == original
        and calls == {"translator": 0, "transmitter": 0}
    ) else 1


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true",
                        help="run a local self-test; no network transmission occurs")
    args = parser.parse_args(argv)
    if args.demo:
        return _demo()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
