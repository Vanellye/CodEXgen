#!/usr/bin/env python3
"""Email only independently qualified READY_TO_OPEN operables; never launches them."""
from __future__ import annotations
from email.message import EmailMessage
import json
import os
from pathlib import Path
import smtplib
import ssl
import sys
from gamma_ops.readiness import ready_records

def main() -> int:
    root = Path.cwd()
    registry_path = root / "Ɣơ/operations/registry/operables.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    ready = [item for item in ready_records(registry, repository_root=root)
             if item.get("notify_when_ready") is True]
    if not ready:
        print("NOTIFY_SKIPPED: no operable currently qualifies as READY_TO_OPEN")
        return 0

    recipient = os.getenv("OPERABLE_NOTIFY_TO", "").strip()
    host = os.getenv("OPERABLE_SMTP_HOST", "").strip()
    port_text = os.getenv("OPERABLE_SMTP_PORT", "").strip()
    username = os.getenv("OPERABLE_SMTP_USER", "")
    password = os.getenv("OPERABLE_SMTP_PASSWORD", "")
    sender = os.getenv("OPERABLE_SMTP_FROM", "").strip()
    if not all((recipient, host, port_text, username, password, sender)):
        print("NOTIFY_HOLD: ready record exists, but email configuration is incomplete")
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
        "A reviewable ERIA operable has met the repository READY_TO_OPEN checks.",
        "",
        f"Repository: {repo}",
        f"Commit: {sha}",
        f"Workflow: {run_url}",
        "",
    ]
    for item in ready:
        lines.extend([
            f"Operable: {item.get('operable_id')}",
            f"Name: {item.get('name')}",
            f"Artifact: {item.get('artifact_path')}",
            f"Source: {item.get('source_ref')}",
            "",
        ])
    lines.append("READY_TO_OPEN is permission to inspect the artifact only. It is not merge, deployment, trading, or financial execution authority.")

    message = EmailMessage()
    message["Subject"] = f"ERIA operable ready to open ({len(ready)})"
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
    print(f"NOTIFY_SENT: {len(ready)} operable(s) sent to configured recipient")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
