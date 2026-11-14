#!/usr/bin/env python3
"""ERIA GitHub Conversation Data Translator (read-only GitHub retrieval).

This is a local Termux agent that retrieves public/repository-permitted GitHub
conversation and repository content through GitHub REST API endpoints. It keeps
retrieved evidence separate from its generated explanation and never writes to
GitHub, changes branches, executes repository code, or fetches secrets.

GitHub access uses a user-supplied token from the environment when required.
Never place a token in source code or command-line arguments.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any


VERSION = "1.0.0"
API_ROOT = "https://api.github.com"
MAX_RESPONSE_BYTES = 2_000_000
USER_AGENT = "ERIA-GitHub-Conversation-Translator/1.0"


class GitHubReadError(RuntimeError):
    pass


@dataclass
class Evidence:
    kind: str
    url: str
    retrieved_unix: float
    sha256: str
    payload: Any


@dataclass
class Translation:
    schema: str
    repository: str
    request: str
    answer: str
    evidence: list[Evidence]
    limitations: list[str]
    engine_version: str = VERSION


def digest_json(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False,
                     separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class GitHubReader:
    def __init__(self, token: str | None = None, timeout: int = 20):
        self.token = token
        self.timeout = timeout

    def get(self, path: str) -> Any:
        if not path.startswith("/"):
            raise GitHubReadError("Only relative GitHub API paths are accepted.")
        if ".." in path.split("/"):
            raise GitHubReadError("Path traversal rejected.")
        url = API_ROOT + path
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": USER_AGENT,
        }
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise GitHubReadError("Response exceeded the 2 MB safety limit.")
                try:
                    payload = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise GitHubReadError("GitHub returned a non-JSON or invalid UTF-8 response.") from exc
                return Evidence(
                    kind="github_api",
                    url=url,
                    retrieved_unix=time.time(),
                    sha256=hashlib.sha256(raw).hexdigest(),
                    payload=payload,
                )
        except urllib.error.HTTPError as exc:
            if exc.code == 401:
                raise GitHubReadError("GitHub authentication failed; verify ERIA_GITHUB_TOKEN.") from exc
            if exc.code == 403:
                raise GitHubReadError("GitHub denied access or rate limit was reached.") from exc
            if exc.code == 404:
                raise GitHubReadError("GitHub resource was not found or is not accessible.") from exc
            raise GitHubReadError(f"GitHub API returned HTTP {exc.code}.") from exc
        except urllib.error.URLError as exc:
            raise GitHubReadError(f"Network request failed: {exc.reason}") from exc


def repo_path(repository: str, suffix: str = "") -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise GitHubReadError("Repository must be owner/name.")
    return "/repos/" + repository + suffix


def clean_text(value: Any, limit: int = 12000) -> str:
    if value is None:
        return ""
    text = str(value)
    text = re.sub(r"(?i)(token|password|secret|authorization)\s*[:=]\s*[^\s,;]+",
                  r"\1=[REDACTED]", text)
    return text[:limit]


def summarize_issue(issue: dict[str, Any]) -> dict[str, Any]:
    return {
        "number": issue.get("number"),
        "title": clean_text(issue.get("title"), 500),
        "state": issue.get("state"),
        "created_at": issue.get("created_at"),
        "updated_at": issue.get("updated_at"),
        "html_url": issue.get("html_url"),
        "body": clean_text(issue.get("body")),
        "user": (issue.get("user") or {}).get("login"),
        "pull_request": bool(issue.get("pull_request")),
    }


def summarize_comment(comment: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": comment.get("id"),
        "created_at": comment.get("created_at"),
        "updated_at": comment.get("updated_at"),
        "html_url": comment.get("html_url"),
        "user": (comment.get("user") or {}).get("login"),
        "body": clean_text(comment.get("body"), 8000),
    }


def fetch_issue_conversation(reader: GitHubReader, repository: str,
                             issue_number: int) -> list[Evidence]:
    base = repo_path(repository, f"/issues/{issue_number}")
    issue_evidence = reader.get(base)
    comments_evidence = reader.get(base + "/comments?per_page=100")
    issue_payload = issue_evidence.payload
    comments_payload = comments_evidence.payload
    if not isinstance(issue_payload, dict) or not isinstance(comments_payload, list):
        raise GitHubReadError("Unexpected issue conversation response shape.")
    issue_evidence.payload = summarize_issue(issue_payload)
    comments_evidence.payload = [summarize_comment(c) for c in comments_payload
                                 if isinstance(c, dict)]
    return [issue_evidence, comments_evidence]


def fetch_repo_metadata(reader: GitHubReader, repository: str) -> Evidence:
    evidence = reader.get(repo_path(repository))
    data = evidence.payload
    if not isinstance(data, dict):
        raise GitHubReadError("Unexpected repository response shape.")
    allowed = ("full_name", "description", "default_branch", "html_url",
               "visibility", "archived", "created_at", "updated_at",
               "language", "stargazers_count", "forks_count")
    evidence.payload = {key: data.get(key) for key in allowed}
    return evidence


def fetch_file(reader: GitHubReader, repository: str, file_path: str,
               ref: str | None = None) -> Evidence:
    if file_path.startswith("/") or ".." in file_path.split("/"):
        raise GitHubReadError("Unsafe repository file path.")
    encoded = urllib.parse.quote(file_path, safe="/")
    query = "?ref=" + urllib.parse.quote(ref, safe="") if ref else ""
    evidence = reader.get(repo_path(repository, "/contents/" + encoded + query))
    data = evidence.payload
    if not isinstance(data, dict) or data.get("type") != "file":
        raise GitHubReadError("Requested path is not a regular repository file.")
    if data.get("encoding") != "base64":
        raise GitHubReadError("Unsupported GitHub file encoding.")
    import base64
    try:
        decoded = base64.b64decode(data.get("content", ""), validate=False)
        text = decoded.decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise GitHubReadError("File is not valid UTF-8 text.") from exc
    if len(decoded) > MAX_RESPONSE_BYTES:
        raise GitHubReadError("Repository file exceeds the 2 MB safety limit.")
    evidence.payload = {
        "path": data.get("path"),
        "sha": data.get("sha"),
        "size": data.get("size"),
        "html_url": data.get("html_url"),
        "content": clean_text(text, MAX_RESPONSE_BYTES),
        "content_sha256": hashlib.sha256(decoded).hexdigest(),
    }
    return evidence


def translate_evidence(repository: str, request: str,
                       evidence: list[Evidence]) -> Translation:
    """Evidence-grounded structured summary; not a claim of AI translation."""
    sections: list[str] = []
    limitations = [
        "This engine structures retrieved GitHub data; it does not infer unobserved facts.",
        "Natural-language translation into another language requires a separately configured provider.",
        "Repository files are treated as untrusted data and are never executed.",
        "The GitHub connector here is read-only; this engine cannot commit, push, merge or edit GitHub.",
    ]
    for item in evidence:
        payload = item.payload
        if item.url.endswith("/comments?per_page=100"):
            comments = payload if isinstance(payload, list) else []
            sections.append(f"Conversation comments retrieved: {len(comments)}")
            for comment in comments:
                sections.append(
                    f"- Comment {comment.get('id')} by {comment.get('user')} "
                    f"({comment.get('created_at')}): {comment.get('body', '')[:1200]}"
                )
        elif "/issues/" in item.url:
            sections.append("ISSUE/PULL REQUEST")
            for key in ("number", "title", "state", "created_at", "updated_at", "html_url", "user", "body"):
                if payload.get(key) is not None:
                    sections.append(f"{key}: {payload[key]}")
        elif "/contents/" in item.url:
            sections.append("REPOSITORY FILE")
            sections.append(f"path: {payload.get('path')}")
            sections.append(f"blob_sha: {payload.get('sha')}")
            sections.append(f"content_sha256: {payload.get('content_sha256')}")
            sections.append("content:")
            sections.append(payload.get("content", "")[:12000])
        else:
            sections.append("REPOSITORY METADATA")
            sections.append(json.dumps(payload, ensure_ascii=False, indent=2))
    answer = "\n".join(sections) if sections else "No evidence retrieved."
    return Translation(
        schema="eria.github-conversation.v1",
        repository=repository,
        request=request,
        answer=answer,
        evidence=evidence,
        limitations=limitations,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only ERIA GitHub conversation-data translator"
    )
    parser.add_argument("--repo", required=True, help="GitHub repository owner/name")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--issue", type=int, help="Read issue or pull request conversation")
    group.add_argument("--repo-info", action="store_true", help="Read repository metadata")
    group.add_argument("--file", help="Read a repository text file")
    parser.add_argument("--ref", help="Branch, tag or commit for --file")
    parser.add_argument("--output", help="Write a new JSON result file; refuses overwrite")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    token = os.environ.get("ERIA_GITHUB_TOKEN")
    reader = GitHubReader(token=token)
    request = (f"issue conversation #{args.issue}" if args.issue else
               f"repository metadata for {args.repo}" if args.repo_info else
               f"file {args.file} at {args.ref or 'default branch'}")
    try:
        if args.issue:
            evidence = fetch_issue_conversation(reader, args.repo, args.issue)
        elif args.repo_info:
            evidence = [fetch_repo_metadata(reader, args.repo)]
        else:
            evidence = [fetch_file(reader, args.repo, args.file, args.ref)]
        result = translate_evidence(args.repo, request, evidence)
    except (GitHubReadError, OSError) as exc:
        print(f"ERIA GITHUB TRANSLATOR HOLD: {exc}", file=sys.stderr)
        return 2

    rendered = json.dumps(asdict(result), ensure_ascii=False,
                          indent=2 if args.pretty or args.output else None)
    if args.output:
        output_path = os.path.abspath(args.output)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        try:
            fd = os.open(output_path, flags, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(rendered + "\n")
        except FileExistsError:
            print("ERIA HOLD: output already exists; refusing overwrite.", file=sys.stderr)
            return 2
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
