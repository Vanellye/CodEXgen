#!/usr/bin/env python3
"""Email only newly qualified READY_TO_OPEN operables; never launches them."""
from __future__ import annotations
import argparse
import hashlib
from email.message import EmailMessage
import json
import os
from pathlib import Path
import smtplib
import ssl
from gamma_ops.readiness import ready_records

def _identity(item: dict, root: Path) -> tuple[str, str, str]:
    artifact = (root / item["artifact_path"]).resolve(strict=True)
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    review = item["review"]
    return (str(item.get("operable_id")), digest, str(review.get("review_ref")))

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Notify on newly READY_TO_OPEN operables")
    parser.add_argument("--previous-registry", default=None)
    args = parser.parse_args(argv)
    root = Path.cwd()
    registry_path = root / "Ɣơ/operations/registry/operables.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    current = [item for item in ready_records(registry, repository_root=root)
               if item.get("notify_when_ready") is True]

    previous = set()
    if args.previous_registry:
        prior_path = Path(args.previous_registry)
        if prior_path.is_file():
            prior = json.loads(prior_path.read_text(encoding="utf-8"))
            previous = {_identity(item, root) for item in ready_records(prior, repository_root=root)}
    newly_ready = [item for item in current if _identity(item, root) not in previous]
    if not newly_ready:
        print("NOTIFY_SKIPPED: no newly READY_TO_OPEN operable")
        return 0

    recipient = os.getenv("OPERABLE_NOTIFY_TO", "").strip()
    host = os.getenv("OPERABLE_SMTP_HOST", "").strip()
    port_text = os.getenv("OPERABLE_SMTP_PORT", "").strip()
    username = os.getenv("OPERABLE_SMTP_USER", "")
    password = os.getenv("OPERABLE_SMTP_PASSWORD", "")
    sender = os.getenv("OPERABLE_SMTP_FROM", "").strip()
    if not all((recipient, host, port_text, username, password, sender)):
        print("NOTIFY_HOLD: newly ready record exists, but email configuration is incomplete")
        return 0
    try:
        port = int(port_text)
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        print("NOTIFY_HOLD: OPERABLE_SMTP_PORT is invalid")
        return 2

    repo = os.getenv("GITHUB_REPOSITORY", "Vanellye/CodEXgen")
    sha = os.getenv("GITHUB_SHA", "unknown")
    run_url = os.getenv("GITHUB_SERVER_URL", "https://github.com") + "/" + repo + "/actions/runs/" + os.getenv("GITHUB_RUN_ID", "")
    lines = [
        "A new ERIA operable has passed READY_TO_OPEN qualification.",
        "",
        f"Repository: {repo}",
        f"Commit: {sha}",
        f"Workflow: {run_url}",
        "",
    ]
    for item in newly_ready:
        lines.extend([
            f"Operable: {item.get('operable_id')}",
            f"Name: {item.get('name')}",
            f"Artifact: {item.get('artifact_path')}",
            f"Source: {item.get('source_ref')}",
            f"Review: {item.get('review', {}).get('review_ref')}",
            "",
        ])
    lines.append("READY_TO_OPEN permits inspection only. It does not grant merge, deployment, execution, trading, or financial authority.")

    message = EmailMessage()
    message["Subject"] = f"ERIA new operable ready to open ({len(newly_ready)})"
    message["From"] = sender
    message["To"] = recipient
    message.set_content("\n".join(lines))
    try:
        with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context(), timeout=20) as smtp:
            smtp.login(username, password)
            smtp.send_message(message)
    except Exception as exc:
        print(f"NOTIFY_FAILED: SMTP delivery failed ({type(exc).__name__}); credentials redacted")
        return 1
    print(f"NOTIFY_SENT: {len(newly_ready)} newly ready operable(s) sent")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
