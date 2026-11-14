#!/usr/bin/env python3
"""Oprozal hybrid advisory mindframe: deterministic, proposal-only deficiency reactions."""
from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any


GAP_RULES = (
    ("RUNTIME_LATENCY", ("lag", "slow", "latency", "timeout", "unresponsive")),
    ("BUILD_FAILURE", ("build failed", "compile error", "compilation failed", "gradle failed")),
    ("TEST_COVERAGE_GAP", ("untested", "no tests", "missing test", "coverage gap")),
    ("DEPENDENCY_RISK", ("dependency conflict", "incompatible dependency", "version conflict")),
    ("SECURITY_CONCERN", ("vulnerability", "security flaw", "exposed secret", "credential leak")),
    ("MISSING_EVIDENCE", ("no evidence", "missing evidence", "unknown source", "unverified")),
    ("MISSING_CAPABILITY", ("missing capability", "lack of capability", "cannot support", "not implemented")),
    ("CONTRADICTION", ("contradiction", "conflicting result", "inconsistent")),
    ("STORAGE_PRESSURE", ("storage full", "out of space", "disk pressure", "memory exhausted")),
)


FACULTIES = {
    "RUNTIME_LATENCY": ["PERFORMANCE_PROFILING", "TEST_GENERATION"],
    "BUILD_FAILURE": ["BUILD_DIAGNOSTICS", "TEST_GENERATION"],
    "TEST_COVERAGE_GAP": ["TEST_GENERATION", "INDEPENDENT_CRITIQUE"],
    "DEPENDENCY_RISK": ["DEPENDENCY_COMPATIBILITY", "SECURITY_REVIEW"],
    "SECURITY_CONCERN": ["SECURITY_REVIEW", "PROVENANCE_AUDIT"],
    "MISSING_EVIDENCE": ["EVIDENCE_GAP_ANALYSIS", "PROVENANCE_AUDIT"],
    "MISSING_CAPABILITY": ["SYNTHESIS_PLANNING", "TEST_GENERATION"],
    "CONTRADICTION": ["INDEPENDENT_CRITIQUE", "EVIDENCE_GAP_ANALYSIS"],
    "STORAGE_PRESSURE": ["PERFORMANCE_PROFILING", "PROVENANCE_AUDIT"],
    "UNKNOWN": ["CONVERSATION_EXPLANATION", "EVIDENCE_GAP_ANALYSIS"],
}


GUIDANCE = {
    "RUNTIME_LATENCY": (
        "A delay is reported, but its cause is not established.",
        "Capture stage-level timings and profile CPU, I/O, memory, and queue wait before optimizing.",
        ["Record workload and baseline latency.", "Profile each runtime stage.", "Compare a candidate against the same workload."]
    ),
    "BUILD_FAILURE": (
        "A build or compilation failure is reported.",
        "Preserve the complete log and isolate the first causal error before proposing a repair.",
        ["Record source revision and toolchain.", "Identify the earliest causal error.", "Run the smallest relevant test, then the full suite."]
    ),
    "TEST_COVERAGE_GAP": (
        "The described behavior may lack adequate regression coverage.",
        "Draft focused tests for normal behavior, invalid input, and failure paths.",
        ["Define observable expected behavior.", "Add success and failure-path tests.", "Run tests against baseline and candidate."]
    ),
    "DEPENDENCY_RISK": (
        "A dependency compatibility or supply-chain concern is reported.",
        "Prepare a version compatibility and provenance review before changing dependencies.",
        ["Record current and proposed versions.", "Check platform compatibility.", "Run license and vulnerability checks."]
    ),
    "SECURITY_CONCERN": (
        "A security concern is reported and remains unverified.",
        "Use read-only inspection and synthetic fixtures; do not execute generated code or inspect secrets.",
        ["Define the threat model.", "Inspect the affected boundary read-only.", "Record evidence and limitations."]
    ),
    "MISSING_EVIDENCE": (
        "A conclusion may lack source-backed evidence.",
        "Request the missing source and retain the claim as unverified until supported.",
        ["Attach source references.", "Record revision and digest where available.", "Reassess after evidence is supplied."]
    ),
    "MISSING_CAPABILITY": (
        "A requested capability is not represented in the current implementation.",
        "Draft a bounded faculty contract with explicit inputs, outputs, permissions, and acceptance tests.",
        ["Define the smallest useful capability.", "Specify data and permission boundaries.", "Add acceptance tests."]
    ),
    "CONTRADICTION": (
        "The request describes conflicting or inconsistent findings.",
        "Preserve both claims and seek independent evidence-based reconciliation.",
        ["Link each claim to its source.", "Compare revision, timestamp, and test conditions.", "Keep disagreement open if evidence is inconclusive."]
    ),
    "STORAGE_PRESSURE": (
        "A storage or memory capacity problem is reported.",
        "Measure current usage and growth before proposing capacity changes; do not delete historical records.",
        ["Measure usage and growth.", "Identify retention and backup needs.", "Validate capacity estimates without modifying records."]
    ),
    "UNKNOWN": (
        "The reported deficiency does not match a known category.",
        "Ask for a reproducible symptom and avoid inferring a cause.",
        ["Clarify the observed behavior.", "Attach a reproducible example.", "Classify only after review."]
    ),
}


def classify(question: str) -> str | None:
    text = question.lower()
    for gap, terms in GAP_RULES:
        if any(term in text for term in terms):
            return gap
    if re.search(r"\b(missing|lack|lacks|lagging|lag|delay|failed|failure)\b", text):
        return "UNKNOWN"
    return None


class OprozalAdvisor:
    """Independent deterministic advisory baseline; no code execution or writes."""

    def assess(self, question: str, source_revision: str = "unknown",
               source_agent: str = "CONVERSATION") -> dict[str, Any] | None:
        gap = classify(question)
        if gap is None:
            return None
        diagnosis, recommendation, checks = GUIDANCE[gap]
        return {
            "schema": "eria.oprozal.advice/1.0",
            "advice_id": "oprozal-" + uuid.uuid4().hex,
            "mindframe": "OPROZAL",
            "architecture": "HYBRID_INDEPENDENT_AND_SHARED_ADVISORY",
            "source_agent": source_agent,
            "gap": gap,
            "severity": "MEDIUM",
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "source_revision": source_revision,
            "source_authority": "NON_AUTHORITATIVE",
            "diagnosis": diagnosis,
            "recommendation": recommendation,
            "faculty_candidates": FACULTIES[gap],
            "verification_steps": checks,
            "confidence": "PROVISIONAL" if gap != "UNKNOWN" else "LOW",
            "pons": {
                "scope": "eria.faculty.propose",
                "status": "HOLD",
                "human_approval_required": True,
            },
            "execution": {
                "proposal_only": True,
                "code_generated": False,
                "code_executed": False,
                "repository_mutated": False,
                "git_mutated": False,
            },
        }

    @staticmethod
    def render(advice: dict[str, Any]) -> str:
        lines = [
            "",
            "## Oprozal advisory (proposal only)",
            f"- **Detected gap:** {advice['gap']}",
            f"- **Diagnosis:** {advice['diagnosis']}",
            f"- **Recommendation:** {advice['recommendation']}",
            f"- **Faculty candidates:** {', '.join(advice['faculty_candidates'])}",
            f"- **Confidence:** {advice['confidence']}",
            f"- **PONS:** {advice['pons']['status']} — {advice['pons']['scope']}",
            "- **Verification:**",
        ]
        lines.extend(f"  - {step}" for step in advice["verification_steps"])
        lines.append("- **Execution:** no code execution or repository/Git writes.")
        return "\n".join(lines)
