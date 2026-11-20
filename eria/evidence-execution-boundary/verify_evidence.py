#!/usr/bin/env python3
"""Offline, read-only ERIA evidence verifier. It never performs the action described."""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")
ACTIONS = {
    "ci", "merge", "deployment", "release",
    "external_dispatch", "hardware_activation", "biological_intervention",
}
CONSEQUENTIAL = ACTIONS - {"ci"}


def fail(message):
    raise ValueError(message)


def required(mapping, key, where):
    value = mapping.get(key) if isinstance(mapping, dict) else None
    if value is None or value == "":
        fail(f"missing {where}.{key}")
    return value


def valid_time(value, field):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError, AttributeError):
        fail(f"invalid {field}; timezone-aware ISO-8601 required")
    if parsed.tzinfo is None:
        fail(f"invalid {field}; timezone is required")


def valid_https(value, field):
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        fail(f"{field} must be an absolute HTTPS URL")


def verify(record, expected_sha, policy):
    if not isinstance(record, dict):
        fail("record must be a JSON object")
    if record.get("schema_version") != "1.0":
        fail("unsupported or missing schema_version")
    action = required(record, "action_type", "record")
    if action not in ACTIONS:
        fail("unsupported action_type")
    subject_sha = required(record, "subject_sha", "record")
    if not SHA40.fullmatch(subject_sha):
        fail("subject_sha must be a full 40-character commit SHA")
    if expected_sha and subject_sha.lower() != expected_sha.lower():
        fail("subject_sha does not match the expected commit SHA")

    evidence = required(record, "evidence", "record")
    if not isinstance(evidence, dict):
        fail("evidence must be an object")
    for key in ("event_id", "status", "source_url", "observed_at", "issuer", "actor"):
        required(evidence, key, "evidence")
    if evidence["status"] != "confirmed":
        fail("evidence.status must be confirmed")
    valid_https(evidence["source_url"], "evidence.source_url")
    valid_time(evidence["observed_at"], "evidence.observed_at")

    trusted = policy.get("trusted_issuers", [])
    if evidence["issuer"] not in trusted:
        fail("evidence issuer is not in policy trusted_issuers")

    if action == "ci":
        if evidence.get("conclusion") != "success":
            fail("CI conclusion must be success")
        if evidence.get("workflow_sha", "").lower() != subject_sha.lower():
            fail("CI workflow_sha must match subject_sha")
    elif action == "merge":
        if evidence.get("pr_merged") is not True:
            fail("merge evidence must explicitly state pr_merged=true")
        merge_sha = evidence.get("merge_commit_sha", "")
        if not SHA40.fullmatch(merge_sha):
            fail("merge_commit_sha must be a full commit SHA")
    elif action == "deployment":
        if evidence.get("deployment_status") != "success":
            fail("deployment_status must be success")
        if evidence.get("deployed_sha", "").lower() != subject_sha.lower():
            fail("deployed_sha must match subject_sha")
        required(evidence, "environment", "evidence")
    elif action == "release":
        if evidence.get("published") is not True:
            fail("release must explicitly state published=true")
        required(evidence, "release_tag", "evidence")
    elif action == "external_dispatch":
        required(evidence, "dispatch_id", "evidence")
        required(evidence, "destination", "evidence")
    elif action == "hardware_activation":
        required(evidence, "device_id", "evidence")
        required(evidence, "attestation_id", "evidence")
    elif action == "biological_intervention":
        required(evidence, "protocol_id", "evidence")
        required(evidence, "protocol_version", "evidence")
        required(evidence, "ethics_approval_id", "evidence")
        required(evidence, "attestation_id", "evidence")

    if action in CONSEQUENTIAL and policy.get("requirements", {}).get(
        "human_approval_for_consequential_actions", True
    ):
        approval = required(record, "approval", "record")
        if not isinstance(approval, dict):
            fail("approval must be an object")
        for key in ("kind", "approver_id", "approved_action", "approved_sha",
                    "approved_at", "approval_ref"):
            required(approval, key, "approval")
        if approval["kind"] != "human":
            fail("approval.kind must be human")
        if approval["approved_action"] != action:
            fail("approval is not bound to this exact action")
        if approval["approved_sha"].lower() != subject_sha.lower():
            fail("approval is not bound to this exact subject_sha")
        if approval["approver_id"] == evidence["actor"]:
            fail("approver must be distinct from the recorded actor")
        valid_time(approval["approved_at"], "approval.approved_at")
        valid_https(approval["approval_ref"], "approval.approval_ref")

    return {
        "accepted": True,
        "action_type": action,
        "subject_sha": subject_sha.lower(),
        "mode": "verify-only",
        "execution_performed": False,
        "note": "Record passed structural policy checks only; upstream authenticity is not established."
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", help="path to a JSON evidence record")
    parser.add_argument("--expected-sha", default="", help="required exact commit SHA")
    parser.add_argument("--policy", default=str(Path(__file__).with_name("policy.json")))
    args = parser.parse_args()
    try:
        record = json.loads(Path(args.record).read_text(encoding="utf-8"))
        policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))
        result = verify(record, args.expected_sha, policy)
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"accepted": False, "execution_performed": False,
                          "reason": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
