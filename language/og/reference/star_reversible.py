"""Ɣơ/2 reversible star-bit encoding. Pure byte transformation; no I/O or execution."""
PREFIX = "Ɣơ/2:"
ZERO = "☆"
ONE = "k"

def encode_bytes(data: bytes) -> str:
    groups = []
    for byte in data:
        groups.append("".join(ONE if (byte >> shift) & 1 else ZERO for shift in range(7, -1, -1)))
    return PREFIX + ".".join(groups)

def decode_bytes(encoded: str) -> bytes:
    if not encoded.startswith(PREFIX):
        raise ValueError("missing Ɣơ/2 prefix")
    payload = encoded[len(PREFIX):]
    if payload == "":
        return b""
    groups = payload.split(".")
    out = bytearray()
    for index, group in enumerate(groups):
        if len(group) != 8:
            raise ValueError(f"group {index} must contain exactly 8 symbols")
        if any(symbol not in (ZERO, ONE) for symbol in group):
            raise ValueError(f"group {index} contains an invalid symbol")
        value = 0
        for symbol in group:
            value = (value << 1) | (1 if symbol == ONE else 0)
        out.append(value)
    return bytes(out)

def encode_text(text: str) -> str:
    return encode_bytes(text.encode("utf-8"))

def decode_text(encoded: str) -> str:
    return decode_bytes(encoded).decode("utf-8")
