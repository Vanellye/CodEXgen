"""Lossless UTF-8 bytes/code-point codec with provenance."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
from typing import Iterable

@dataclass(frozen=True)
class DecodedRecord:
    source_sha256: str
    byte_length: int
    codepoints: tuple[int, ...]
    text: str

def decode_bytes(payload: bytes) -> DecodedRecord:
    text = payload.decode("utf-8", errors="strict")
    return DecodedRecord(hashlib.sha256(payload).hexdigest(), len(payload),
                         tuple(ord(ch) for ch in text), text)

def encode_codepoints(codepoints: Iterable[int]) -> bytes:
    chars: list[str] = []
    for point in codepoints:
        if not isinstance(point, int) or isinstance(point, bool):
            raise TypeError("code points must be integers")
        if point < 0 or point > 0x10FFFF or 0xD800 <= point <= 0xDFFF:
            raise ValueError(f"invalid Unicode scalar value: {point!r}")
        chars.append(chr(point))
    return "".join(chars).encode("utf-8")

def verify_round_trip(payload: bytes) -> bool:
    record = decode_bytes(payload)
    rebuilt = encode_codepoints(record.codepoints)
    return rebuilt == payload and hashlib.sha256(rebuilt).hexdigest() == record.source_sha256

def calculation_terms(values: Iterable[int]) -> tuple[int, ...]:
    """Non-zero additive terms for a derived view; canonical input is untouched."""
    if any(not isinstance(v, int) or isinstance(v, bool) for v in values):
        raise TypeError("calculation terms must be integers")
    return tuple(v for v in values if v != 0)
