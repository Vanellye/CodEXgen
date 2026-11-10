#!/usr/bin/env python3
"""Read-only, bounded branch-head observer for Pantheon Branch Horizon.

The observer reads Git objects and tracked text blobs only. It never executes
repository code and never changes refs, the index, or the worktree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.2.0"
POLICY_VERSION = "branch-horizon-readonly-v1"
ROTATING_LENSES = (
    "ancestry",
    "interfaces",
    "dependencies",
    "tests_ci",
    "provenance",
    "capabilities_exchange",
)
# The seventh dimension is always active as a governing invariant, never a
# rotating task: preserve provenance, consent, receiver control, and reversibility.
SACRED_DIMENSION = "sacred"
LENSES = ROTATING_LENSES + (SACRED_DIMENSION,)
MAX_FILES = 1200
MAX_PEER_BRANCHES = 24
MAX_PEER_FILES = 300
MAX_PEER_FILE_BYTES = 128 * 1024
MAX_PEER_TOTAL_BYTES = 1024 * 1024
MAX_FILE_BYTES = 512 * 1024
MAX_TOTAL_BYTES = 8 * 1024 * 1024
TEXT_SUFFIXES = {
    ".py", ".pyi", ".h", ".hh", ".hpp", ".hxx", ".c", ".cc", ".cpp",
    ".kt", ".kts", ".java", ".js", ".jsx", ".ts", ".tsx", ".html",
    ".htm", ".json", ".toml", ".yaml", ".yml", ".xml", ".gradle",
    ".md", ".txt", ".cfg", ".ini", ".properties", ".sh", ".rs", ".go",
}
MANIFEST_NAMES = {
    "pyproject.toml", "requirements.txt", "package.json", "package-lock.json",
    "pnpm-lock.yaml", "yarn.lock", "Cargo.toml", "Cargo.lock", "pom.xml",
    "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts",
    "go.mod", "go.sum", "Gemfile", "Gemfile.lock",
}
TEST_PARTS = ("test", "tests", "spec", "specs")


def stable_lens(first_parent_depth: int) -> tuple[int, str]:
    """Successive first-parent heads rotate one slot; reruns remain identical."""
    cursor = max(0, first_parent_depth - 1)
    slot = cursor % len(ROTATING_LENSES)
    return cursor, ROTATING_LENSES[slot]


def _git(repo: Path, *args: str, binary: bool = False) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=20,
    )
    if result.returncode:
        message = result.stderr.decode("utf-8", "replace")[:500]
        raise RuntimeError(f"git {' '.join(args[:3])} failed: {message}")
    return result.stdout if binary else result.stdout


def _text(data: bytes) -> str:
    return data.decode("utf-8", "replace")


def _tree(repo: Path, head: str) -> tuple[dict[str, dict[str, str]], bool]:
    raw = _git(repo, "ls-tree", "-r", "-z", head)
    entries: dict[str, dict[str, str]] = {}
    truncated = False
    for item in raw.split(b"\0"):
        if not item:
            continue
        try:
            meta, raw_path = item.split(b"\t", 1)
            mode, kind, oid = meta.decode("ascii").split(" ")
            path = raw_path.decode("utf-8", "surrogateescape")
        except (ValueError, UnicodeDecodeError):
            continue
        if mode == "120000" or kind != "blob":
            continue
        if len(entries) >= MAX_FILES:
            truncated = True
            break
        entries[path] = {"mode": mode, "oid": oid}
    return entries, truncated


def _changed_paths(repo: Path, head: str) -> list[str]:
    raw = _git(repo, "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", "-z", head)
    return sorted({p.decode("utf-8", "surrogateescape") for p in raw.split(b"\0") if p})


def _read_blobs(repo: Path, entries: dict[str, dict[str, str]]) -> tuple[dict[str, str], list[str]]:
    contents: dict[str, str] = {}
    skipped: list[str] = []
    total = 0
    for path in sorted(entries):
        suffix = Path(path).suffix.lower()
        name = Path(path).name
        if suffix not in TEXT_SUFFIXES and name not in MANIFEST_NAMES:
            continue
        oid = entries[path]["oid"]
        size_raw = _git(repo, "cat-file", "-s", oid)
        try:
            size = int(size_raw.strip())
        except ValueError:
            skipped.append(path)
            continue
        if size > MAX_FILE_BYTES or total + size > MAX_TOTAL_BYTES:
            skipped.append(path)
            continue
        blob = _git(repo, "cat-file", "blob", oid, binary=True)
        total += len(blob)
        contents[path] = _text(blob)
    return contents, skipped


def _finding(severity: str, title: str, evidence: list[str], detail: str,
             confidence: str = "medium", limitation: str | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {
        "severity": severity, "title": title, "evidence": evidence,
        "detail": detail, "confidence": confidence,
    }
    if limitation:
        item["limitation"] = limitation
    return item


def _scan_lens(lens: str, repo: Path, head: str, depth: int,
               entries: dict[str, dict[str, str]], contents: dict[str, str],
               changed: list[str], commit: dict[str, str]) -> tuple[list[dict[str, Any]], list[str]]:
    findings: list[dict[str, Any]] = []
    inspected: list[str] = []
    if lens == "ancestry":
        parents = commit["parents"].split() if commit["parents"] else []
        inspected = ["Git commit headers", "first-parent history"]
        findings.append(_finding(
            "info", "Head ancestry recorded", [head],
            f"First-parent depth: {depth}; direct parent count: {len(parents)}; "
            f"parents: {', '.join(parents) if parents else 'none'}.",
            "high",
        ))
        if len(parents) > 1:
            findings.append(_finding("notice", "Merge commit at observed head", [head],
                                     "The observed head has multiple parents; inspect the merge context during review.", "high"))
    elif lens == "interfaces":
        inspected = [p for p in changed if p in contents]
        patterns = (
            (r"^\s*(?:export\s+)?(?:interface|class|type|function)\s+([A-Za-z_$][\w$]*)", "JS/TS declaration"),
            (r"^\s*(?:pub\s+)?(?:class|struct|enum|trait|fn)\s+([A-Za-z_]\w*)", "Rust-style declaration"),
            (r"^\s*(?:class|interface|enum|object|fun)\s+([A-Za-z_]\w*)", "Kotlin/Java declaration"),
            (r"^\s*(?:class|def)\s+([A-Za-z_]\w*)", "Python declaration"),
            (r"^\s*(?:class|struct|enum|union|typedef)\s+([A-Za-z_]\w*)", "C/C++ declaration"),
            (r"^\s*<([A-Za-z][\w:-]*)\b", "HTML element"),
        )
        count = 0
        for path in inspected:
            for line_no, line in enumerate(contents[path].splitlines(), 1):
                for pattern, label in patterns:
                    match = re.search(pattern, line)
                    if match:
                        count += 1
                        findings.append(_finding(
                            "info", f"Possible {label}: {match.group(1)}",
                            [f"{path}:{line_no}"],
                            "Lexical declaration signal only; this is not compiler-level interface or type analysis.",
                            "low",
                        ))
                        break
        if count == 0:
            findings.append(_finding("info", "No supported interface declarations detected",
                                     changed, "No matching declaration patterns were found in changed, readable text files.",
                                     "low", "Generated code, macros, multiline declarations, and unsupported languages may be missed."))
    elif lens == "dependencies":
        manifests = [p for p in contents if Path(p).name in MANIFEST_NAMES]
        inspected = manifests
        if not manifests:
            findings.append(_finding("info", "No recognized dependency manifest found",
                                     changed, "No supported manifest or lockfile was present in the tracked source snapshot.",
                                     "low", "This inventory recognizes a finite list of common manifest names."))
        for path in manifests:
            body = contents[path]
            findings.append(_finding("info", "Dependency file inventoried", [path],
                                     f"{len(body.splitlines())} text lines; SHA-256 {hashlib.sha256(body.encode()).hexdigest()}.",
                                     "high"))
            if Path(path).name == "requirements.txt":
                for n, line in enumerate(body.splitlines(), 1):
                    value = line.strip()
                    if value and not value.startswith(("#", "-")) and not re.search(r"(==|~=|>=|<=|>|<)", value):
                        findings.append(_finding("warning", "Potentially unpinned Python requirement",
                                                  [f"{path}:{n}"], value[:160], "medium"))
    elif lens == "tests_ci":
        inspected = [p for p in entries if any(part in [x.lower() for x in Path(p).parts] for part in TEST_PARTS)]
        workflows = [p for p in entries if p.startswith(".github/workflows/")]
        inspected += workflows
        changed_src = [p for p in changed if not any(part in [x.lower() for x in Path(p).parts] for part in TEST_PARTS)]
        changed_tests = [p for p in changed if any(part in [x.lower() for x in Path(p).parts] for part in TEST_PARTS)]
        findings.append(_finding(
            "info", "Test and CI coverage inventory", inspected,
            f"Tracked test/spec paths: {len([p for p in inspected if p not in workflows])}; "
            f"workflow files: {len(workflows)}; changed paths: {len(changed)}; "
            f"changed test paths: {len(changed_tests)}; other changed paths: {len(changed_src)}.",
            "medium",
        ))
        if changed_src and not changed_tests:
            findings.append(_finding("warning", "Changed source without changed test paths",
                                     changed_src, "No test/spec path changed in this commit. This is a review prompt, not proof of missing tests.",
                                     "low"))
    elif lens == "provenance":
        inspected = changed
        for path in changed:
            if path in entries:
                findings.append(_finding("info", "Changed path provenance",
                                         [path, entries[path]["oid"]],
                                         f"Git blob object: {entries[path]['oid']}; mode: {entries[path]['mode']}.",
                                         "high"))
            else:
                findings.append(_finding("info", "Path absent at observed head",
                                         [path], "The path was changed in the commit but is not present in the resulting tree (likely deletion).",
                                         "high"))
        if not changed:
            findings.append(_finding("info", "No path changes in observed commit", [head],
                                     "The observed commit has no file-path changes.", "high"))
    elif lens == "capabilities_exchange":
        inspected = [p for p in contents if p.startswith(".github/workflows/") or
                     "package" in Path(p).name.lower() or "pantheon" in Path(p).name.lower()]
        keywords = ("permissions:", "contents: write", "id-token: write",
                    "capabilities_requested", "approval", "signature", "workflow_dispatch")
        for path in inspected:
            for n, line in enumerate(contents[path].splitlines(), 1):
                if any(word in line.lower() for word in keywords):
                    findings.append(_finding("notice", "Capability or exchange policy signal",
                                              [f"{path}:{n}"], line.strip()[:200], "low",
                                              "Keyword inventory only; it does not establish effective permissions or cryptographic validity."))
        if not findings:
            findings.append(_finding("info", "No capability/exchange signals detected",
                                     inspected, "No configured policy keywords were found in inspected workflow/package/Pantheon files.",
                                     "low"))
    return findings, sorted(set(inspected))



def _peer_refs(repo: Path, current_branch: str) -> tuple[list[dict[str, str]], bool]:
    """Discover already-fetched remote branch refs; never fetch or update refs."""
    raw = _git(repo, "for-each-ref", "--format=%(refname:short) %(objectname)", "refs/remotes/origin")
    peers: list[dict[str, str]] = []
    truncated = False
    for line in _text(raw).splitlines():
        parts = line.strip().split()
        if len(parts) != 2:
            continue
        ref, sha = parts
        if ref == "origin/HEAD":
            continue
        branch = ref.removeprefix("origin/")
        if branch == current_branch:
            continue
        if len(peers) >= MAX_PEER_BRANCHES:
            truncated = True
            break
        peers.append({"branch": branch, "ref": ref, "sha": sha})
    return sorted(peers, key=lambda item: item["branch"]), truncated


def _peer_snapshot(repo: Path, ref: str) -> tuple[dict[str, dict[str, str]], dict[str, str], bool]:
    raw = _git(repo, "ls-tree", "-r", "-z", ref)
    entries: dict[str, dict[str, str]] = {}
    truncated = False
    for item in raw.split(b"\0"):
        if not item:
            continue
        try:
            meta, raw_path = item.split(b"\t", 1)
            mode, kind, oid = meta.decode("ascii").split(" ")
            path = raw_path.decode("utf-8", "surrogateescape")
        except (ValueError, UnicodeDecodeError):
            continue
        if mode == "120000" or kind != "blob":
            continue
        if len(entries) >= MAX_PEER_FILES:
            truncated = True
            break
        entries[path] = {"mode": mode, "oid": oid}

    contents: dict[str, str] = {}
    total = 0
    for path in sorted(entries):
        if Path(path).suffix.lower() not in TEXT_SUFFIXES and Path(path).name not in MANIFEST_NAMES:
            continue
        oid = entries[path]["oid"]
        size = int(_git(repo, "cat-file", "-s", oid).strip() or b"0")
        if size > MAX_PEER_FILE_BYTES or total + size > MAX_PEER_TOTAL_BYTES:
            truncated = True
            continue
        blob = _git(repo, "cat-file", "blob", oid, binary=True)
        total += len(blob)
        contents[path] = _text(blob)
    return entries, contents, truncated


def _interface_signals(contents: dict[str, str]) -> dict[str, str]:
    patterns = (
        r"^\s*(?:export\s+)?(?:interface|class|type|function)\s+([A-Za-z_$][\w$]*)",
        r"^\s*(?:pub\s+)?(?:class|struct|enum|trait|fn)\s+([A-Za-z_]\w*)",
        r"^\s*(?:class|interface|enum|object|fun)\s+([A-Za-z_]\w*)",
        r"^\s*(?:class|def)\s+([A-Za-z_]\w*)",
        r"^\s*(?:class|struct|enum|union|typedef)\s+([A-Za-z_]\w*)",
    )
    signals: dict[str, str] = {}
    for path, body in contents.items():
        if Path(path).suffix.lower() not in {
            ".py", ".pyi", ".h", ".hh", ".hpp", ".hxx", ".c", ".cc", ".cpp",
            ".kt", ".kts", ".java", ".js", ".jsx", ".ts", ".tsx", ".rs", ".go",
        }:
            continue
        for line in body.splitlines():
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    name = match.group(1)
                    signals.setdefault(name, " ".join(line.strip().split()))
                    break
    return signals


def _dependency_signals(contents: dict[str, str]) -> dict[str, str]:
    deps: dict[str, str] = {}
    for path, body in contents.items():
        name = Path(path).name
        if name == "requirements.txt":
            for line in body.splitlines():
                value = line.strip()
                if not value or value.startswith(("#", "-")):
                    continue
                match = re.match(r"([A-Za-z0-9_.-]+)(?:\[[^\]]+\])?\s*(.*)", value)
                if match:
                    deps.setdefault(match.group(1).lower().replace("_", "-"), match.group(2).strip() or "unspecified")
        elif name == "package.json":
            try:
                data = json.loads(body)
                for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
                    values = data.get(section, {})
                    if isinstance(values, dict):
                        for package, version in values.items():
                            deps.setdefault(package.lower(), str(version))
            except (ValueError, AttributeError):
                continue
        elif name == "go.mod":
            for line in body.splitlines():
                match = re.match(r"^\s*([A-Za-z0-9._/-]+)\s+(v[^\s]+)", line)
                if match:
                    deps.setdefault(match.group(1).lower(), match.group(2))
        elif name == "Cargo.toml":
            in_dependencies = False
            for line in body.splitlines():
                stripped = line.strip()
                if stripped.startswith("["):
                    in_dependencies = stripped in {
                        "[dependencies]", "[dev-dependencies]", "[build-dependencies]"
                    }
                elif in_dependencies:
                    match = re.match(r'([A-Za-z0-9_-]+)\s*=\s*["{]([^"}]+)', stripped)
                    if match:
                        deps.setdefault(match.group(1).lower().replace("_", "-"), match.group(2))
    return deps


def _compare_peer(repo: Path, head: str, peer: dict[str, str]) -> dict[str, Any]:
    entries, contents, truncated = _peer_snapshot(repo, peer["ref"])
    current_entries, current_contents, current_truncated = _peer_snapshot(repo, head)
    current_interfaces = _interface_signals(current_contents)
    peer_interfaces = _interface_signals(contents)
    shared_symbols = sorted(set(current_interfaces) & set(peer_interfaces))
    identical_symbols = [
        name for name in shared_symbols
        if current_interfaces[name] == peer_interfaces[name]
    ]
    differing_symbols = [
        name for name in shared_symbols
        if current_interfaces[name] != peer_interfaces[name]
    ]
    current_deps = _dependency_signals(current_contents)
    peer_deps = _dependency_signals(contents)
    shared_deps = sorted(set(current_deps) & set(peer_deps))
    same_deps = [name for name in shared_deps if current_deps[name] == peer_deps[name]]
    differing_deps = [name for name in shared_deps if current_deps[name] != peer_deps[name]]

    ancestry = _text(_git(repo, "rev-list", "--left-right", "--count", f"{head}...{peer['sha']}")).strip().split()
    ahead = int(ancestry[0]) if len(ancestry) > 0 else None
    behind = int(ancestry[1]) if len(ancestry) > 1 else None
    if truncated or current_truncated:
        classification = "unknown_incomplete"
    elif differing_symbols or differing_deps:
        classification = "review_required"
    elif identical_symbols or same_deps:
        classification = "shared_signals_only"
    else:
        classification = "unknown_no_shared_signals"

    return {
        "branch": peer["branch"],
        "ref": peer["ref"],
        "peer_sha": peer["sha"],
        "classification": classification,
        "ancestry": {"head_only_commits": ahead, "peer_only_commits": behind},
        "interface_signals": {
            "shared_names": shared_symbols,
            "identical_declarations": identical_symbols,
            "different_declarations": differing_symbols,
        },
        "dependency_signals": {
            "shared_names": shared_deps,
            "same_specs": same_deps,
            "different_specs": differing_deps,
            "head_specs_for_differences": {name: current_deps[name] for name in differing_deps},
            "peer_specs_for_differences": {name: peer_deps[name] for name in differing_deps},
        },
        "evidence": {
            "head_text_files_read": len(current_contents),
            "peer_text_files_read": len(contents),
            "head_truncated": current_truncated,
            "peer_truncated": truncated,
        },
        "proposal": {
            "action": "human_review_only",
            "suggested_review": (
                "Inspect declaration and dependency differences before proposing an interface adapter or dependency alignment."
                if classification == "review_required"
                else "Review shared signals as discovery leads; do not infer semantic compatibility."
            ),
            "adoption_authorized": False,
        },
        "sacred_guard": {
            "status": "preserved",
            "rules": [
                "compare exact immutable commit identities",
                "read-only observation; no branch or file mutation",
                "no automatic merge, adoption, installation, approval, or propagation",
                "retain provenance and require receiver review",
            ],
        },
    }


def _cross_branch_peering(repo: Path, branch: str, head: str) -> dict[str, Any]:
    peers, branch_limit_hit = _peer_refs(repo, branch)
    comparisons = [_compare_peer(repo, head, peer) for peer in peers]
    return {
        "enabled": True,
        "mode": "read_only",
        "peer_count": len(comparisons),
        "branch_limit_hit": branch_limit_hit,
        "limits": {
            "max_peer_branches": MAX_PEER_BRANCHES,
            "max_peer_files": MAX_PEER_FILES,
            "max_peer_file_bytes": MAX_PEER_FILE_BYTES,
            "max_peer_total_bytes": MAX_PEER_TOTAL_BYTES,
        },
        "comparisons": comparisons,
        "adoption_authorized": False,
    }


def build_report(repo: Path, branch: str, before: str, head: str) -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    commit_raw = _git(repo, "show", "-s", "--format=%H%n%P%n%an%n%aI%n%s", head)
    lines = _text(commit_raw).splitlines()
    commit = {
        "sha": lines[0] if lines else head,
        "parents": lines[1] if len(lines) > 1 else "",
        "author": lines[2] if len(lines) > 2 else "unknown",
        "authored_at": lines[3] if len(lines) > 3 else "unknown",
        "subject": lines[4] if len(lines) > 4 else "",
    }
    depth = int(_git(repo, "rev-list", "--first-parent", "--count", head).strip() or b"0")
    cursor, lens = stable_lens(depth)
    entries, tree_truncated = _tree(repo, head)
    contents, skipped = _read_blobs(repo, entries)
    changed = _changed_paths(repo, head)
    findings, inspected = _scan_lens(lens, repo, head, depth, entries, contents, changed, commit)
    peer_report = _cross_branch_peering(repo, branch, head)
    incomplete = tree_truncated or bool(skipped)
    if tree_truncated:
        findings.append(_finding("warning", "File inventory limit reached", [],
                                  f"Only the first {MAX_FILES} tracked blobs were inventoried.", "high"))
    if skipped:
        findings.append(_finding("warning", "Some files skipped by size or budget", skipped[:100],
                                  f"{len(skipped)} files were not read because per-file or total-byte limits were reached.", "high"))
    finished = datetime.now(timezone.utc).isoformat()
    return {
        "schema_version": "1.0",
        "tool_version": VERSION,
        "policy_version": POLICY_VERSION,
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "branch": branch,
        "before_sha": before,
        "head_sha": head,
        "commit": commit,
        "first_parent_depth": depth,
        "lens_cursor": cursor,
        "selected_lens": lens,
        "scan_started_at": started,
        "scan_finished_at": finished,
        "status": "incomplete" if incomplete else "complete",
        "files_in_tree": len(entries),
        "text_files_read": len(contents),
        "files_inspected": inspected,
        "changed_paths": changed,
        "findings": findings,
        "dimensions_not_inspected": [name for name in ROTATING_LENSES if name != lens],
        "sacred_dimension": {
            "name": SACRED_DIMENSION,
            "mode": "always_on_invariant",
            "principles": ["provenance", "consent", "receiver_control", "reversibility"],
            "adoption_authorized": False,
        },
        "cross_branch_peering": peer_report,
        "limits": {"max_files": MAX_FILES, "max_file_bytes": MAX_FILE_BYTES, "max_total_bytes": MAX_TOTAL_BYTES},
        "mutations_performed": [],
        "limitations": [
            "Read-only lexical inventory; no source code or build scripts were executed.",
            "Only one of six operational lenses was selected for this head; the seventh Sacred dimension is an always-on invariant.",
            "Cross-branch interface and dependency matching is lexical and does not prove semantic compatibility.",
            "Only already-fetched remote branches are compared; branch refs outside the fetched view are unknown.",
            "Static heuristics may miss language-specific constructs and semantic relationships.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Pantheon Branch Horizon report", "",
        f"- **Repository:** {report['repository']}",
        f"- **Branch:** {report['branch']}",
        f"- **Observed head:** `{report['head_sha']}`",
        f"- **Previous head:** `{report['before_sha']}`",
        f"- **Selected lens:** **{report['selected_lens']}** (cursor {report['lens_cursor']})",
        f"- **Status:** **{report['status']}**",
        f"- **Files inventoried/read:** {report['files_in_tree']} / {report['text_files_read']}",
        f"- **Scan:** {report['scan_started_at']} → {report['scan_finished_at']}",
        "", "## Findings", "",
    ]
    for item in report["findings"]:
        evidence = ", ".join(f"`{e}`" for e in item["evidence"]) or "No path evidence"
        lines += [f"### [{item['severity'].upper()}] {item['title']}",
                  f"- Evidence: {evidence}", f"- Confidence: {item['confidence']}",
                  f"- {item['detail']}"]
        if item.get("limitation"):
            lines.append(f"- Limitation: {item['limitation']}")
        lines.append("")
    lines += ["## Sacred dimension", "",
              "- Always-on invariant: provenance, consent, receiver control, and reversibility.",
              "- No proposal authorizes adoption; explicit receiver review is required.",
              "", "## Cross-branch peering", "",
              f"- Peers compared: {report['cross_branch_peering']['peer_count']}",
              f"- Mode: {report['cross_branch_peering']['mode']}",
              "- Interface and dependency matches are discovery signals, not proof of compatibility.",
              "- Differing declarations or dependency specs are flagged for human review.",
              "- No merge, adoption, installation, approval, or propagation is authorized.",
              "", "## Dimensions not inspected", ""]
    lines += [f"- {name}" for name in report["dimensions_not_inspected"]]
    lines += ["", "## Safety", "",
              "- No repository code was executed.",
              "- No Git refs, files, approvals, or branches were modified.",
              "- No merge, push, install, or propagation action was attempted.",
              "", "## Limitations", ""]
    lines += [f"- {item}" for item in report["limitations"]]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--branch", default=os.environ.get("GITHUB_REF_NAME", "local"))
    parser.add_argument("--before", default=os.environ.get("GITHUB_EVENT_BEFORE", ""))
    parser.add_argument("--head", default=os.environ.get("GITHUB_SHA", "HEAD"))
    parser.add_argument("--output-dir", default="branch-horizon-report")
    args = parser.parse_args(argv)
    try:
        report = build_report(Path(args.repo).resolve(), args.branch, args.before, args.head)
        output = Path(args.output_dir)
        output.mkdir(parents=True, exist_ok=True)
        (output / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (output / "report.md").write_text(render_markdown(report), encoding="utf-8")
        print(json.dumps({"head_sha": report["head_sha"], "lens": report["selected_lens"],
                          "status": report["status"], "output_dir": str(output)}))
        return 0
    except Exception as exc:
        print(f"branch-horizon: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
