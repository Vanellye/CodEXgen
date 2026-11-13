#!/usr/bin/env python3
"""Deterministic, proposal-only ERIA event-to-invention brief generator."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "shared" / "eria-invention-events" / "events.json"


def load_payload() -> dict:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        return {}
    try:
        value = json.loads(Path(event_path).read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def build_brief(event_name: str, payload: dict, catalog: dict, repo: str, ref: str, sha: str) -> str:
    events = catalog.get("events", {})
    spec = events.get(event_name)
    if not isinstance(spec, dict):
        spec = {
            "label": "Unclassified forge event",
            "inventions": [
                "Classify the event and document why it matters to the current integration.",
                "Propose a read-only observation or test before any implementation.",
                "Route the proposal to a human reviewer with source revision attached."
            ]
        }

    action = str(payload.get("action", ""))
    if event_name == "workflow_run":
        run = payload.get("workflow_run", {})
        if isinstance(run, dict):
            conclusion = str(run.get("conclusion") or "unknown")
            workflow_name = str(run.get("name") or "unnamed workflow")
        else:
            conclusion, workflow_name = "unknown", "unnamed workflow"
    else:
        conclusion, workflow_name = "n/a", "n/a"

    dial = int(catalog.get("invention_basis_dial", 0))
    ideas = list(spec.get("inventions", []))[:max(0, min(3, dial))]
    lines = [
        "# ERIA Invention Pulse",
        "",
        f"- **Event:** {event_name} / {spec.get('label', 'Event')}",
        f"- **Action:** {action or 'not supplied'}",
        f"- **Repository:** {repo or 'unknown'}",
        f"- **Ref:** {ref or 'unknown'}",
        f"- **Source revision:** {sha or 'unknown'}",
        f"- **Invention basis dial:** {dial}/3",
    ]
    if event_name == "workflow_run":
        lines += [f"- **Workflow:** {workflow_name}", f"- **Conclusion:** {conclusion}"]
    lines += ["", "## Invention seeds"]
    lines += [f"{i}. {idea}" for i, idea in enumerate(ideas, 1)]
    lines += [
        "",
        "## Required next gate",
        "Turn a selected seed into a scoped proposal with acceptance tests, threat review, provenance, and rollback notes.",
        "",
        "**Boundary:** This pulse creates suggestions only. It does not edit source, commit, push, open or merge PRs, deploy, publish, access secrets, execute generated code, dispatch external actions, or activate hardware or biological interventions.",
        "",
        "Human review and explicit authorization are required before implementation."
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    try:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        if catalog.get("schema") != "ERIA-INVENTION-EVENTS":
            raise ValueError("unexpected catalog schema")
        event_name = os.environ.get("GITHUB_EVENT_NAME", "workflow_dispatch")
        payload = load_payload()
        brief = build_brief(
            event_name, payload, catalog,
            os.environ.get("GITHUB_REPOSITORY", ""),
            os.environ.get("GITHUB_REF", ""),
            os.environ.get("GITHUB_SHA", "")
        )
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary, "a", encoding="utf-8") as handle:
                handle.write(brief)
        else:
            sys.stdout.write(brief)
        return 0
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"ERIA invention pulse failed closed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
