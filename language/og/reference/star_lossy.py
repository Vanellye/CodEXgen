"""Ɣơ/L1 lossy zero-removal transform. It deliberately has no decoder."""
PREFIX = "Ɣơ/L1:"
ONE = "k"

def encode_bytes_lossy(data: bytes) -> str:
    # Keep one period-delimited group per source byte. Empty groups represent
    # bytes containing no one-bits. Bit positions are intentionally discarded.
    groups = []
    for byte in data:
        groups.append(ONE * byte.bit_count())
    return PREFIX + ".".join(groups)

def encode_text_lossy(text: str) -> str:
    return encode_bytes_lossy(text.encode("utf-8"))
