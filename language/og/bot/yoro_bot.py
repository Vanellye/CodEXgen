"""Small local Ɣơ bot: deterministic transforms only; never executes encoded content."""
from __future__ import annotations
import argparse
from pathlib import Path

STAR_PREFIX = "Ɣơ/2:"
LOSSY_PREFIX = "Ɣơ/L1:"

def encode_reversible(data: bytes) -> str:
    groups = []
    for byte in data:
        groups.append("".join("k" if (byte >> shift) & 1 else "☆" for shift in range(7, -1, -1)))
    return STAR_PREFIX + ".".join(groups)

def encode_lossy(data: bytes) -> str:
    return LOSSY_PREFIX + ".".join("k" * byte.bit_count() for byte in data)

def transform(data: bytes, profile: str) -> str:
    if profile == "reversible":
        return encode_reversible(data)
    if profile == "lossy":
        return encode_lossy(data)
    raise ValueError("profile must be reversible or lossy")

def main() -> int:
    parser = argparse.ArgumentParser(description="Encode a local file with a Ɣơ profile.")
    parser.add_argument("--profile", choices=("reversible", "lossy"), required=True)
    parser.add_argument("--input", required=True, help="input file path")
    parser.add_argument("--output", help="optional output text path; otherwise print to stdout")
    args = parser.parse_args()
    data = Path(args.input).read_bytes()
    result = transform(data, args.profile)
    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
    else:
        print(result)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
