#!/usr/bin/env python3
"""Oprozal proposal -> static preflight -> quality report coordinator."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from eria_oprozal import OprozalAdvisor
from eria_oprozal_preflight import inspect_python
from eria_quality_analyzer import analyze


def git_revision(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def build_packet(root: Path, question: str, source_path: str) -> dict[str, Any]:
    revision = git_revision(root)
    advice = OprozalAdvisor().assess(
        question, source_revision=revision, source_agent="ERIA_OPROZAL_FORGE"
    )
    if advice is None:
        return {
            "schema": "eria.oprozal.forge/1.0",
            "status": "NO_DEFICIENCY_SIGNAL",
            "source_revision": revision,
            "proposal": None,
            "preflight": None,
            "quality_report": None,
        }

    faculty = advice["faculty_candidates"][0]
    proposal = {
        "proposal_id": advice["advice_id"] + "-" + faculty.lower(),
        "faculty": faculty,
        "purpose": advice["recommendation"],
        "source_signal": advice["advice_id"],
        "source_revision": revision,
        "source_authority": "NON_AUTHORITATIVE",
        "pons_scope": "eria.faculty.propose",
        "status": "REVIEW_REQUIRED",
        "action_taken": False,
        "acceptance_checks": advice["verification_steps"],
    }
    preflight = None
    report = None
    if source_path:
        preflight = inspect_python(root, source_path, revision)
        report = analyze(preflight, proposal)
    return {
        "schema": "eria.oprozal.forge/1.0",
        "status": "STATIC_REVIEW_READY" if report and report["overall"] == "STATIC_REVIEW_READY"
                  else "PROPOSAL_ONLY",
        "advice": advice,
        "proposal": proposal,
        "preflight": preflight,
        "quality_report": report,
        "pons": {
            "decision": "HOLD",
            "scope": "eria.faculty.propose",
            "reason": "No trusted PONS approval verifier was supplied to this coordinator.",
        },
        "mutation": {
            "source_write": False,
            "git_write": False,
            "execution": False,
            "report_persisted": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an Oprozal faculty review packet.")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--question", required=True)
    parser.add_argument("--source", default="", help="Optional repo-relative Python candidate for static parsing.")
    args = parser.parse_args()
    root = args.repo.resolve()
    if not root.is_dir():
        parser.error("--repo must be an existing directory")
    try:
        packet = build_packet(root, args.question, args.source)
    except (OSError, ValueError) as exc:
        print(json.dumps({"schema": "eria.oprozal.forge/1.0", "status": "HOLD",
                          "error": str(exc), "execution": False}, sort_keys=True))
        return 2
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0 if packet["status"] != "HOLD" else 2


if __name__ == "__main__":
    raise SystemExit(main())
