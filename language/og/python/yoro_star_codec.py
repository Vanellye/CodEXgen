"""Python adapter for the shared Ɣơ/2 byte vectors."""
from pathlib import Path

PREFIX = "Ɣơ/2:"

def encode_bytes(data: bytes) -> str:
    return PREFIX + ".".join("".join("k" if (byte >> bit) & 1 else "☆" for bit in range(7, -1, -1)) for byte in data)

def decode_bytes(text: str) -> bytes:
    if not text.startswith(PREFIX):
        raise ValueError("Unsupported Ɣơ profile")
    body = text[len(PREFIX):]
    if not body:
        return b""
    groups = body.split(".")
    if any(len(group) != 8 or any(c not in "☆k" for c in group) for group in groups):
        raise ValueError("Each byte must contain exactly eight ☆/k symbols")
    return bytes(int("".join("1" if c == "k" else "0" for c in group), 2) for group in groups)

def validate_vectors(path: str | Path) -> int:
    count = 0
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        name, hex_bytes, expected = line.split("|")
        raw = bytes.fromhex(hex_bytes)
        assert encode_bytes(raw) == expected, f"encode mismatch: {name}"
        assert decode_bytes(expected) == raw, f"decode mismatch: {name}"
        count += 1
    return count

if __name__ == "__main__":
    import sys
    print("Python Ɣơ/2 vectors passed:", validate_vectors(sys.argv[1]))
