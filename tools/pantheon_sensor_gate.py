#!/usr/bin/env python3
"""PANTHEON RAW sensor policy gate.

Offline-only utility. It does not access microphone/accelerometer hardware.
It can inspect policy and append an approval REQUEST to an audit log.
An approval request is not activation or permission to collect data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
POLICY = ROOT / "config" / "pantheon-raw-sensor-policy.json"


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_policy() -> dict:
    with POLICY.open("r", encoding="utf-8") as stream:
        data = json.load(stream)
    if data.get("status") != "proposal_only":
        raise ValueError("Unexpected policy status; refusing to proceed.")
    if data.get("safety", {}).get("fail_closed") is not True:
        raise ValueError("fail_closed must remain true.")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inspect", action="store_true",
                        help="inspect policy; does not access hardware")
    parser.add_argument("--request-approval", action="store_true",
                        help="record an approval request; does not activate sensors")
    parser.add_argument("--operator", help="operator identifier for audit trail")
    parser.add_argument("--sensor", choices=("microphone", "accelerometer"))
    parser.add_argument("--purpose", help="specific measurement purpose")
    parser.add_argument("--duration-seconds", type=int)
    args = parser.parse_args()

    try:
        policy = load_policy()
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2

    policy_hash = sha256(POLICY)
    print(f"Policy: {policy['schema']}")
    print(f"Policy SHA-256: {policy_hash}")
    print("Mode: proposal_only / fail_closed")
    print("Hardware access: NOT IMPLEMENTED")
    print("Sensor acquisition: DISABLED")

    if args.request_approval:
        if not all((args.operator, args.sensor, args.purpose,
                    args.duration_seconds)):
            parser.error("--request-approval requires --operator, --sensor, "
                         "--purpose, and --duration-seconds")
        if args.duration_seconds < 1 or args.duration_seconds > 60:
            print("BLOCKED: approval requests are limited to 1–60 seconds "
                  "in this proposal stage.", file=sys.stderr)
            return 2

        audit_rel = pathlib.PurePosixPath(
            policy["provenance"]["audit_path"]
        )
        if audit_rel.is_absolute() or ".." in audit_rel.parts:
            print("BLOCKED: unsafe audit path.", file=sys.stderr)
            return 2

        audit_path = ROOT.joinpath(*audit_rel.parts)
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "event": "sensor_approval_requested",
            "status": "pending_human_review",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "operator": args.operator,
            "sensor": args.sensor,
            "purpose": args.purpose,
            "requested_duration_seconds": args.duration_seconds,
            "policy_sha256": policy_hash,
            "source_revision": os.environ.get("ERIA_SOURCE_REVISION"),
            "hardware_accessed": False,
            "activation": False
        }
        with audit_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True) + "\n")
        print(f"Approval request recorded: {audit_path}")
        print("No sensor was activated. Human review remains required.")
    elif args.inspect:
        print("Inspection complete. No hardware was accessed.")
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
