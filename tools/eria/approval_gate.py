#!/usr/bin/env python3
"""Fail-closed verifier for a human GitHub PR approval on the exact head SHA.

This checks review evidence; GitHub branch protection remains responsible for
reviewer write permission, required review counts, and merge enforcement.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def has_current_human_approval(
    reviews: Iterable[dict[str, Any]], head_sha: str, pr_author: str = ""
) -> tuple[bool, str]:
    if not head_sha or not pr_author:
        return False, "Missing pull-request head SHA or author identity."

    latest_by_reviewer: dict[str, dict[str, Any]] = {}
    for review in reviews:
        user = review.get("user") or {}
        login = user.get("login")
        if not isinstance(login, str) or not login.strip():
            continue
        previous = latest_by_reviewer.get(login)
        submitted = review.get("submitted_at") or ""
        previous_submitted = (previous or {}).get("submitted_at") or ""
        if previous is None or submitted >= previous_submitted:
            latest_by_reviewer[login] = review

    for login, review in latest_by_reviewer.items():
        user = review.get("user") or {}
        # Unknown account type is not proof of a human identity.
        if user.get("type") != "User":
            continue
        if login.casefold() == (pr_author or "").casefold():
            continue
        if review.get("state") != "APPROVED":
            continue
        if review.get("commit_id") != head_sha:
            continue
        if not review.get("submitted_at"):
            continue
        return True, f"Current-SHA approval recorded by human reviewer {login}."

    return False, (
        "Blocked: no non-author human APPROVED review is bound to the exact "
        f"PR head SHA {head_sha}. Missing, stale, dismissed, bot, and unknown "
        "review identities do not satisfy this gate."
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviews", required=True, type=Path)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--pr-author", required=True)
    args = parser.parse_args()

    try:
        reviews = json.loads(args.reviews.read_text(encoding="utf-8"))
        if not isinstance(reviews, list):
            raise ValueError("reviews payload must be a JSON array")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"BLOCKED: cannot verify review evidence: {exc}", file=sys.stderr)
        return 2

    approved, message = has_current_human_approval(
        reviews, args.head_sha, args.pr_author
    )
    print(message)
    return 0 if approved else 1


if __name__ == "__main__":
    raise SystemExit(main())
