#!/usr/bin/env python3
"""Reference Ɣơ .og byte codec.

This is a pure encoder/decoder prototype. It does not execute code or write files.
"""
from __future__ import annotations

import argparse
import sys
from typing import Iterable

PROFILE = "og-base5-syllables/0.1"
DIGIT_TO_GLYPH = ("ba", "be", "bi", "bo", "bu")
GLYPH_TO_DIGIT = {glyph: digit for digit, glyph in enumerate(DIGIT_TO_GLYPH)}
MAX_BYTES = 1_000_000


class OgCodecError(ValueError):
    """Invalid or unsupported .og input."""


def _byte_to_glyphs(value: int) -> str:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 255:
        raise OgCodecError("byte value must be an integer from 0 to 255")
    digits = [0, 0, 0, 0]
    remainder = value
    for index in range(3, -1, -1):
        digits[index] = remainder % 5
        remainder //= 5
    if remainder:
        raise OgCodecError("byte conversion overflow")
    return "-".join(DIGIT_TO_GLYPH[digit] for digit in digits)


def _glyphs_to_byte(token: str) -> int:
    syllables = token.split("-")
    if len(syllables) != 4:
        raise OgCodecError("each byte token must contain exactly four syllables")
    value = 0
    for syllable in syllables:
        try:
            digit = GLYPH_TO_DIGIT[syllable]
        except KeyError as exc:
            raise OgCodecError(f"unknown syllable: {syllable!r}") from exc
        value = value * 5 + digit
    if value > 255:
        raise OgCodecError("decoded byte exceeds 255")
    return value


def encode(data: bytes) -> str:
    if not isinstance(data, bytes):
        raise TypeError("encode expects bytes")
    if len(data) > MAX_BYTES:
        raise OgCodecError(f"input exceeds the {MAX_BYTES}-byte limit")
    payload = "empty" if not data else ", ".join(_byte_to_glyphs(byte) for byte in data)
    return "\n".join((
        "OG/0",
        "kind:BYTES",
        f"length:{len(data)}",
        f"payload:{payload}",
        f"codec:{PROFILE}",
    ))


def decode(document: str) -> bytes:
    if not isinstance(document, str):
        raise TypeError("decode expects a string")
    if len(document) > (MAX_BYTES * 40 + 256):
        raise OgCodecError("document exceeds maximum size")
    lines = document.splitlines()
    if len(lines) != 5:
        raise OgCodecError("document must contain exactly five lines")
    if lines[0] != "OG/0":
        raise OgCodecError("unsupported or missing OG version")
    if lines[1] != "kind:BYTES":
        raise OgCodecError("unsupported or missing data kind")
    if not lines[2].startswith("length:"):
        raise OgCodecError("missing length field")
    raw_length = lines[2][7:]
    if not raw_length.isascii() or not raw_length.isdecimal():
        raise OgCodecError("length must be an unsigned decimal integer")
    if len(raw_length) > 10:
        raise OgCodecError("declared length is too large")
    length = int(raw_length)
    if length > MAX_BYTES:
        raise OgCodecError(f"declared length exceeds the {MAX_BYTES}-byte limit")
    if not lines[3].startswith("payload:"):
        raise OgCodecError("missing payload field")
    if lines[4] != f"codec:{PROFILE}":
        raise OgCodecError("unsupported codec profile")

    payload = lines[3][8:]
    if length == 0:
        if payload != "empty":
            raise OgCodecError("zero-length payload must be 'empty'")
        return b""
    if payload == "empty":
        raise OgCodecError("non-empty data cannot use the empty payload marker")

    tokens = payload.split(", ")
    if len(tokens) != length:
        raise OgCodecError("payload token count does not match declared length")
    return bytes(_glyphs_to_byte(token) for token in tokens)


def _cli(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ɣơ .og lossless byte codec")
    sub = parser.add_subparsers(dest="command", required=True)
    encoder = sub.add_parser("encode", help="encode hexadecimal bytes")
    encoder.add_argument("hex_bytes", help="hexadecimal input, e.g. 0001ff")
    decoder = sub.add_parser("decode", help="decode a compact OG/0:hex test form")
    decoder.add_argument("document", help="full .og text or OG/0: followed by hex")
    args = parser.parse_args(argv)

    try:
        if args.command == "encode":
            try:
                raw = bytes.fromhex(args.hex_bytes)
            except ValueError as exc:
                raise OgCodecError("input must be an even-length hexadecimal string") from exc
            print(encode(raw))
        else:
            if args.document.startswith("OG/0:"):
                raw = bytes.fromhex(args.document[5:])
                print(raw.hex())
            else:
                print(decode(args.document).hex())
        return 0
    except (OgCodecError, TypeError, ValueError) as exc:
        print(f"og-codec: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(_cli())
