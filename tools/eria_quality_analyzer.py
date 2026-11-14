#!/usr/bin/env python3
"""Evidence-aware quality gates for Oprozal static preflight results."""
from __future__ import annotations
import hashlib
import json
from typing import Any

SCHEMA = "eria.quality.report/1.0"


def analyze(preflight: dict[str, Any], proposal: dict[str, Any]) -> dict[str, Any]:
    """Evaluate only the claims supported by the supplied preflight evidence."""
    valid_schema = preflight.get("schema") == "eria.oprozal.preflight/1.0"
    digest = preflight.get("source_sha256", "")
    valid_digest = (isinstance(digest, str) and len(digest) == 64
                    and all(ch in "0123456789abcdef" for ch in digest))
    revision = preflight.get("source_revision", "")
    source_bound = bool(preflight.get("source_path")) and revision not in ("", None, "unknown")
    parse_pass = preflight.get("checks", {}).get("python_ast_parse") == "PASS"
    path_pass = preflight.get("checks", {}).get("path_containment") == "PASS"
    no_execution_claim = preflight.get("execution_performed") is False
    no_write_claim = preflight.get("source_write_performed") is False
    gates = {
        "result_schema": "PASS" if valid_schema else "FAIL",
        "source_digest": "PASS" if valid_digest else "FAIL",
        "source_revision": "PASS" if source_bound else "FAIL",
        "path_containment": "PASS" if path_pass else "FAIL",
        "python_syntax": "PASS" if parse_pass else "FAIL",
        "execution_boundary": "PASS" if no_execution_claim else "FAIL",
        "source_write_boundary": "PASS" if no_write_claim else "FAIL",
        "pons_authorization": "HOLD",
        "semantic_correctness": "NOT_ASSESSED",
        "runtime_behavior": "NOT_ASSESSED",
    }
    passed = sum(value == "PASS" for value in gates.values())
    applicable = sum(value in ("PASS", "FAIL") for value in gates.values())
    required = [value for key, value in gates.items()
                if key not in ("pons_authorization", "semantic_correctness", "runtime_behavior")]
    overall = "STATIC_REVIEW_READY" if applicable and all(x == "PASS" for x in required) else "STATIC_CHECKS_FAILED"
    report = {
        "schema": SCHEMA,
        "proposal_id": proposal.get("proposal_id", "unknown"),
        "faculty": proposal.get("faculty", "unknown"),
        "source_path": preflight.get("source_path", "unknown"),
        "source_sha256": digest,
        "source_revision": revision or "unknown",
        "source_authority": "NON_AUTHORITATIVE",
        "preflight_status": preflight.get("status", "UNKNOWN"),
        "gates": gates,
        "static_gate_count": {"passed": passed, "applicable": applicable},
        "overall": overall,
        "authorization": {
            "pons_scope": proposal.get("pons_scope", "eria.faculty.propose"),
            "decision": "HOLD", "human_approval_required": True,
            "source_write_enabled": False, "execution_enabled": False,
            "merge_enabled": False,
        },
        "limitations": [
            "AST parsing does not prove semantic correctness.",
            "No candidate code was imported or executed.",
            "No OS-level sandbox execution was attempted.",
            "PONS approval was not inferred from this report.",
        ],
    }
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    report["report_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return report
