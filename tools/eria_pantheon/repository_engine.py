"""Repository-wide ERIA acquisition and quality orchestration.

Acquires evidence from the checked-out repository without mutating it. Execution
plans are proposals: this module never invokes discovered project commands.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

SKIP_DIRS = {
    ".git", ".gradle", ".idea", ".venv", "venv", "__pycache__",
    "node_modules", "vendor", "build", "dist", ".eria", ".pytest_cache",
}
MAX_FILES = 20_000
MAX_FILE_BYTES = 5 * 1024 * 1024
SENSITIVE_PATH = re.compile(
    r"(^|[/_.-])(\.env(?:\.|$)|secrets?|credentials?|id_rsa|"
    r"id_ed25519|keystore|\.pem|\.p12|\.jks)([/_.-]|$)", re.I
)
TEXT_SUFFIXES = {
    ".py", ".sh", ".bash", ".kt", ".kts", ".java", ".c", ".h", ".hpp",
    ".cpp", ".rs", ".go", ".js", ".jsx", ".ts", ".tsx", ".html", ".css",
    ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".gradle", ".sql", ".xml", ".properties", ".ptn",
}
MANIFEST_NAMES = {
    "pyproject.toml", "requirements.txt", "setup.py", "setup.cfg",
    "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
    "Cargo.toml", "Cargo.lock", "go.mod", "go.sum", "pom.xml",
    "build.gradle", "build.gradle.kts", "settings.gradle",
    "settings.gradle.kts", "gradlew", "Makefile", "CMakeLists.txt",
    "Dockerfile", "tox.ini", "pytest.ini",
}
TEST_DIRS = {"test", "tests", "__tests__", "spec", "specs"}
TEST_NAME = re.compile(r"(^test_.*\.py$|.*_test\.py$|.*Test\.(kt|java)$|.*\.spec\.[jt]sx?$)", re.I)
SECRET_VALUE = re.compile(
    r"(?i)(?:api[_-]?key|password|passwd|secret|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"
)


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True, capture_output=True, text=True, timeout=8,
    )
    return result.stdout.strip()


def _safe_root(repository: str | Path) -> Path:
    root = Path(repository).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Repository root must be a directory.")
    return root


def acquire_repository(repository: str | Path) -> dict[str, Any]:
    """Build a bounded, provenance-linked inventory of the checked-out tree."""
    root = _safe_root(repository)
    try:
        commit = _git(root, "rev-parse", "HEAD")
        branch = _git(root, "branch", "--show-current")
        dirty = bool(_git(root, "status", "--porcelain"))
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("A readable Git worktree is required for provenance.") from exc

    files: list[dict[str, Any]] = []
    skipped_sensitive = 0
    skipped_large = 0
    truncated = False
    for directory, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(
            name for name in dirnames
            if name not in SKIP_DIRS and not name.startswith(".")
            and not (Path(directory) / name).is_symlink()
        )
        for filename in sorted(filenames):
            path = Path(directory) / filename
            if path.is_symlink():
                continue
            relative = path.relative_to(root).as_posix()
            if SENSITIVE_PATH.search(relative):
                skipped_sensitive += 1
                continue
            try:
                stat = path.stat()
            except OSError:
                continue
            if not path.is_file():
                continue
            if stat.st_size > MAX_FILE_BYTES:
                skipped_large += 1
                continue
            try:
                raw = path.read_bytes()
            except OSError:
                continue
            suffix = path.suffix.lower()
            is_text = suffix in TEXT_SUFFIXES or filename in MANIFEST_NAMES
            digest = hashlib.sha256(raw).hexdigest()
            record = {
                "path": relative, "size_bytes": len(raw), "sha256": digest,
                "kind": "text" if is_text else "binary_or_unclassified",
                "manifest": filename in MANIFEST_NAMES,
                "test_candidate": (
                    any(part.lower() in TEST_DIRS for part in Path(relative).parts)
                    or bool(TEST_NAME.match(filename))
                ),
            }
            if is_text:
                try:
                    content = raw.decode("utf-8-sig", errors="strict")
                except UnicodeDecodeError:
                    record["kind"] = "binary_or_unclassified"
                else:
                    record["line_count"] = content.count("\n") + (1 if content else 0)
                    if SECRET_VALUE.search(content):
                        record["review_flag"] = "credential_like_literal; value not retained"
            files.append(record)
            if len(files) >= MAX_FILES:
                truncated = True
                break
        if truncated:
            break

    files.sort(key=lambda item: item["path"])
    return {
        "engine": "ERIA Repository Engineering Orchestrator",
        "mode": "repository_wide_read_only_acquisition",
        "repository": str(root),
        "git": {"branch": branch or "(detached)", "commit": commit, "dirty": dirty},
        "limits": {
            "max_files": MAX_FILES, "max_file_bytes": MAX_FILE_BYTES,
            "truncated": truncated, "skipped_sensitive_paths": skipped_sensitive,
            "skipped_large_files": skipped_large,
        },
        "files": files,
        "summary": {
            "file_count": len(files),
            "text_count": sum(item["kind"] == "text" for item in files),
            "manifest_count": sum(item["manifest"] for item in files),
            "test_candidate_count": sum(item["test_candidate"] for item in files),
            "extensions": _counts(Path(item["path"]).suffix.lower() or "(no extension)" for item in files),
        },
        "authority": "NON_AUTHORITATIVE",
        "source_mutations": False,
        "git_mutations": False,
    }


def _counts(values):
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return [{"value": key, "count": counts[key]} for key in sorted(counts)]


def quality_analysis(inventory: dict[str, Any]) -> dict[str, Any]:
    """Produce repository-wide quality coverage and missing-evidence findings."""
    files = inventory["files"]
    paths = {item["path"] for item in files}
    manifests = [item["path"] for item in files if item["manifest"]]
    tests = [item["path"] for item in files if item["test_candidate"]]
    workflows = sorted(path for path in paths if path.startswith(".github/workflows/"))
    findings = []
    if not tests:
        findings.append({"class": "UNKNOWN", "severity": "HIGH",
                         "finding": "No test candidates were discovered in the bounded inventory."})
    if not workflows:
        findings.append({"class": "UNKNOWN", "severity": "MEDIUM",
                         "finding": "No GitHub Actions workflow files were discovered."})
    if inventory["git"]["dirty"]:
        findings.append({"class": "FACT", "severity": "MEDIUM",
                         "finding": "The checked-out worktree contains uncommitted changes; results are not a clean-commit baseline."})
    if inventory["limits"]["truncated"]:
        findings.append({"class": "UNKNOWN", "severity": "HIGH",
                         "finding": "Inventory reached its file cap; repository coverage is incomplete."})
    return {
        "coverage": {
            "inventory_files": len(files), "manifests": manifests,
            "test_candidates": tests, "workflow_files": workflows,
        },
        "findings": findings,
        "classification": "FACT/UNKNOWN; no heuristic is treated as a verdict",
        "limitations": [
            "This pass inventories paths and metadata; it does not prove tests pass.",
            "Dependencies are identified from manifest presence, not installed or resolved.",
            "Security review requires source-specific analyzers and human triage.",
        ],
    }


def execution_plan(inventory: dict[str, Any]) -> dict[str, Any]:
    """Return candidate quality commands without executing repository code."""
    paths = {item["path"] for item in inventory["files"]}
    commands = []
    if "pyproject.toml" in paths or "pytest.ini" in paths or any(p.startswith("tests/") and p.endswith(".py") for p in paths):
        commands.append({"id": "python-tests", "argv": ["python", "-m", "pytest", "-q"],
                         "risk": "EXECUTES_REPOSITORY_TEST_CODE", "requires": "isolated_runner_and_explicit_approval"})
    if "gradlew" in paths:
        commands.append({"id": "android-debug-build", "argv": ["./gradlew", "assembleDebug"],
                         "risk": "EXECUTES_GRADLE_BUILD_LOGIC", "requires": "isolated_runner_and_explicit_approval"})
    if "Makefile" in paths:
        commands.append({"id": "make-check-review", "argv": ["make", "check"],
                         "risk": "EXECUTES_PROJECT_DEFINED_TARGET", "requires": "target_review_and_explicit_approval"})
    return {
        "commands": commands,
        "executed": False,
        "execution_state": "HOLD",
        "reason": "The repository itself is untrusted input; test/build scripts can execute arbitrary code.",
        "required_controls": [
            "ephemeral isolated workspace with no secrets and no write access to the source checkout",
            "network disabled unless a dependency source is explicitly approved",
            "resource/time limits and captured stdout/stderr",
            "exact base commit and command recorded before execution",
            "human approval for the proposed command set",
        ],
    }


def synthesize(inventory: dict[str, Any], quality: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    """Combine evidence without upgrading inferred claims into verified facts."""
    return {
        "repository": inventory["repository"],
        "revision": inventory["git"],
        "acquisition": inventory["summary"],
        "quality": quality["coverage"],
        "findings": quality["findings"],
        "execution": {
            "state": plan["execution_state"], "candidate_count": len(plan["commands"]),
            "commands": plan["commands"],
        },
        "next_stage": "review execution plan, provision isolated runner, then run approved checks",
        "authority": "NON_AUTHORITATIVE",
        "synthesis_is_not_source_truth": True,
    }


def run_repository_review(repository: str | Path) -> dict[str, Any]:
    inventory = acquire_repository(repository)
    quality = quality_analysis(inventory)
    plan = execution_plan(inventory)
    return {
        "inventory": inventory,
        "quality": quality,
        "execution_plan": plan,
        "synthesis": synthesize(inventory, quality, plan),
    }


def to_json(repository: str | Path) -> str:
    return json.dumps(run_repository_review(repository), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    print(to_json(args.repository))
