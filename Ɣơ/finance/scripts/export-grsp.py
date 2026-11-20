#!/usr/bin/env python3
"""Deterministic versioned GRSP audit export; never overwrites its source ledger."""
import hashlib
import json
import sys
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit("usage: export-grsp.py INPUT.jsonl OUTPUT.GRSP")

source, target = map(Path, sys.argv[1:])
if source.resolve(strict=True) == target.resolve(strict=False):
    raise SystemExit("HOLD: GRSP output must not resolve to the source ledger")
if target.exists() and target.is_symlink():
    raise SystemExit("HOLD: refusing to replace a symlink target")

raw = source.read_bytes()
records = [json.loads(line) for line in raw.splitlines() if line.strip()]
envelope = {
    "format": "GRSP",
    "version": 1,
    "mode": "AUDIT_EXPORT_ONLY",
    "source_sha256": hashlib.sha256(raw).hexdigest(),
    "record_count": len(records),
    "records": records,
}
target.write_text(
    json.dumps(envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
print(f"wrote {target} ({len(records)} records); source ledger preserved")
