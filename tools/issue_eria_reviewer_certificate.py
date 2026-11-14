#!/usr/bin/env python3
"""Offline tool: issue a root-signed Ed25519 AVS reviewer certificate."""
from __future__ import annotations

import argparse
import base64
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from eria_pantheon.reviewer_identity import canonical_json


def read_b64(path: str) -> bytes:
    return base64.b64decode(Path(path).read_text(encoding="utf-8").strip(), validate=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root-private-b64", required=True, help="Offline trust-root private key file")
    parser.add_argument("--reviewer-public-b64", required=True, help="Reviewer's raw Ed25519 public key file")
    parser.add_argument("--reviewer-id", required=True)
    parser.add_argument("--key-id", required=True)
    parser.add_argument("--issuer", required=True)
    parser.add_argument("--valid-days", type=int, default=90)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if not 1 <= args.valid_days <= 365:
        parser.error("--valid-days must be between 1 and 365")
    root = Ed25519PrivateKey.from_private_bytes(read_b64(args.root_private_b64))
    public_key = read_b64(args.reviewer_public_b64)
    if len(public_key) != 32:
        parser.error("Reviewer public key must decode to 32 bytes")
    now = datetime.now(timezone.utc)
    body = {
        "reviewer_id": args.reviewer_id,
        "key_id": args.key_id,
        "public_key": base64.b64encode(public_key).decode("ascii"),
        "role": "evidence_reviewer",
        "issuer": args.issuer,
        "not_before": now.isoformat(),
        "expires_at": (now + timedelta(days=args.valid_days)).isoformat(),
        "permissions": ["avs:evidence:submit"],
    }
    certificate = dict(body)
    certificate["root_signature"] = base64.b64encode(root.sign(canonical_json(body))).decode("ascii")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(certificate, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    output.chmod(0o644)
    print(f"Issued public reviewer certificate: {output}")
    print(f"Reviewer: {args.reviewer_id} | key: {args.key_id} | expires: {body['expires_at']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
