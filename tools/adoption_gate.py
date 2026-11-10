#!/usr/bin/env python3
"""Fail-closed eligibility gate for Pantheon Divergence Garden adoption.

This tool is intended to run from the trusted default-branch checkout. Candidate
files are read from a separate, exact-SHA checkout and are never executed here.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

POLICY_VERSION = "divergence-adoption-v1"
OPT_IN_PREFIX = "divergence/auto/"
ALLOWED_PATHS = {
    "tools/branch_horizon.py",
    "PANTHEON_BRANCH_HORIZON.md",
}
MAX_CHANGED_FILES = 2
MAX_TOTAL_CHANGES = 500


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args],
        text=True,
        stderr=subprocess.PIPE,
    ).strip()


def evaluate_candidate(
    trusted_repo: Path,
    candidate_repo: Path,
    branch: str,
    head_sha: str,
    branch_head_sha: str,
    base_ref: str = "origin/main",
) -> dict[str, Any]:
    reasons: list[str] = []
    if not branch.startswith(OPT_IN_PREFIX):
        reasons.append("branch_not_explicitly_opted_in")
    if not head_sha or head_sha != branch_head_sha:
        reasons.append("branch_head_does_not_match_observed_sha")

    try:
        git(candidate_repo, "rev-parse", "--verify", f"{base_ref}^{{commit}}")
        git(candidate_repo, "merge-base", "--is-ancestor", base_ref, head_sha)
    except (subprocess.CalledProcessError, FileNotFoundError):
        reasons.append("candidate_is_not_based_on_current_target")

    try:
        raw = git(candidate_repo, "diff", "--name-status", f"{base_ref}...{head_sha}")
        entries = [line.split("\t", 1) for line in raw.splitlines() if line]
        if not entries:
            reasons.append("no_changes_to_adopt")
        if len(entries) > MAX_CHANGED_FILES:
            reasons.append("changed_file_limit_exceeded")
        for entry in entries:
            if len(entry) != 2:
                reasons.append("unsupported_diff_record")
                continue
            status, path = entry
            if status not in {"M", "A"}:
                reasons.append(f"non_additive_change:{path}")
            if path not in ALLOWED_PATHS:
                reasons.append(f"path_not_allowlisted:{path}")
        numstat = git(candidate_repo, "diff", "--numstat", f"{base_ref}...{head_sha}")
        total = 0
        for line in numstat.splitlines():
            fields = line.split("\t")
            if len(fields) != 3 or not fields[0].isdigit() or not fields[1].isdigit():
                reasons.append("binary_or_unparseable_diff")
                continue
            total += int(fields[0]) + int(fields[1])
        if total > MAX_TOTAL_CHANGES:
            reasons.append("change_budget_exceeded")
    except subprocess.CalledProcessError:
        reasons.append("diff_inspection_failed")

    for path in ALLOWED_PATHS:
        candidate_file = candidate_repo / path
        if path == "tools/branch_horizon.py" and not candidate_file.is_file():
            reasons.append("branch_horizon_tool_missing")
        if path == "PANTHEON_BRANCH_HORIZON.md" and not candidate_file.is_file():
            # Documentation is optional; it is checked only if changed.
            pass

    return {
        "policy_version": POLICY_VERSION,
        "eligible": not reasons,
        "branch": branch,
        "head_sha": head_sha,
        "target": base_ref,
        "reasons": reasons,
        "limits": {
            "allowed_paths": sorted(ALLOWED_PATHS),
            "max_changed_files": MAX_CHANGED_FILES,
            "max_total_changes": MAX_TOTAL_CHANGES,
        },
        "adoption_mode": "pull_request_with_github_auto_merge",
        "direct_target_mutation": False,
        "force_push": False,
        "branch_protection_bypass": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--branch-head", required=True)
    parser.add_argument("--github-output")
    args = parser.parse_args()

    report = evaluate_candidate(
        Path.cwd(), Path(args.candidate), args.branch, args.head,
        args.branch_head, args.base,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as output:
            output.write(f"eligible={str(report['eligible']).lower()}\n")
            output.write(f"reason={';'.join(report['reasons']) or 'all_gates_passed'}\n")
    return 0 if report["eligible"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
