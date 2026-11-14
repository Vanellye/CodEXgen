"""Read-only GitHub Actions evidence reader for ERIA.

Only queries one pinned repository, branch, and workflow. GET requests only;
never dispatches, reruns, cancels, downloads, or mutates workflows.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

REPOSITORY = "Vanellye/CodEXgen"
BRANCH = "feature/eria-higher-faculty-inspection-2026-11-14"
WORKFLOW = "eria-isolated-runner-validation.yml"
API_ROOT = "https://api.github.com"
MAX_RESPONSE = 1_000_000


class GitHubActionsReadError(RuntimeError):
    pass


def _get(path: str) -> dict:
    if not path.startswith("/repos/" + REPOSITORY + "/"):
        raise GitHubActionsReadError("GitHub API path is outside the configured repository.")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ERIA-read-only-evidence-reader",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(API_ROOT + path, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            raw = response.read(MAX_RESPONSE + 1)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise GitHubActionsReadError("Workflow or run not found (or repository access is unavailable).") from exc
        if exc.code in (401, 403):
            raise GitHubActionsReadError("GitHub denied read access; check the optional read-only GITHUB_TOKEN and rate limit.") from exc
        raise GitHubActionsReadError("GitHub API request failed with HTTP " + str(exc.code)) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise GitHubActionsReadError("GitHub Actions is unreachable: " + type(exc).__name__) from exc
    if len(raw) > MAX_RESPONSE:
        raise GitHubActionsReadError("GitHub response exceeded the 1 MB safety limit.")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GitHubActionsReadError("GitHub returned invalid JSON.") from exc
    if not isinstance(value, dict):
        raise GitHubActionsReadError("GitHub returned an unexpected response shape.")
    return value


def inspect_validation() -> dict:
    workflow = urllib.parse.quote(WORKFLOW, safe="")
    branch = urllib.parse.quote(BRANCH, safe="")
    data = _get(
        "/repos/" + REPOSITORY + "/actions/workflows/" + workflow
        + "/runs?branch=" + branch + "&per_page=10"
    )
    runs = []
    for item in data.get("workflow_runs", []):
        if item.get("path") != ".github/workflows/" + WORKFLOW:
            continue
        run_id = item.get("id")
        artifacts = []
        if isinstance(run_id, int):
            artifact_data = _get(
                "/repos/" + REPOSITORY + "/actions/runs/" + str(run_id) + "/artifacts?per_page=20"
            )
            for artifact in artifact_data.get("artifacts", []):
                artifacts.append({
                    "id": artifact.get("id"),
                    "name": artifact.get("name"),
                    "size_in_bytes": artifact.get("size_in_bytes"),
                    "expired": artifact.get("expired"),
                    "created_at": artifact.get("created_at"),
                    "expires_at": artifact.get("expires_at"),
                })
        runs.append({
            "id": run_id,
            "run_number": item.get("run_number"),
            "event": item.get("event"),
            "status": item.get("status"),
            "conclusion": item.get("conclusion"),
            "head_branch": item.get("head_branch"),
            "head_sha": item.get("head_sha"),
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
            "html_url": item.get("html_url"),
            "artifacts": artifacts,
        })
    return {
        "repository": REPOSITORY,
        "branch": BRANCH,
        "workflow": WORKFLOW,
        "workflow_url": "https://github.com/" + REPOSITORY + "/actions/workflows/" + WORKFLOW,
        "runs": runs,
        "run_count": len(runs),
        "read_only": True,
        "execution_triggered": False,
        "artifact_downloaded": False,
        "signature_note": (
            "Artifact metadata only. Existing runner HMAC signatures cannot be independently "
            "verified outside the runner because the HMAC key is not included (and must not be uploaded)."
        ),
    }
