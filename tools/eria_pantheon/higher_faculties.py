"""Higher Faculty source-code translation pipeline for ERIA.

Discovery -> Antithesis -> Verification -> Creation.
Read-only, deterministic first pass. It creates candidate explanations only;
it never executes, compiles, transmits, or modifies source files.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from .aei import AeiError, inspect_file

VERSION = "higher-faculty-0.1.0"
CODE_SUFFIXES = {
    ".py", ".sh", ".kt", ".kts", ".java", ".c", ".h", ".hpp", ".cpp",
    ".rs", ".go", ".js", ".ts", ".sql", ".gradle",
}
PATTERNS = (
    ("dependency declaration", re.compile(r"^\s*(?:#include\b|import\s|from\s)"),
     "This line declares a header or module dependency."),
    ("class declaration", re.compile(r"^\s*(?:class\s|.*\bclass\s+\w+)"),
     "This line appears to declare a class, a named type that groups data and behavior."),
    ("struct declaration", re.compile(r"^\s*(?:struct\s|.*\bstruct\s+\w+)"),
     "This line appears to declare a structure, a named aggregate data type."),
    ("interface declaration", re.compile(r"^\s*(?:interface\s|.*\binterface\s+\w+)"),
     "This line appears to declare an interface contract."),
    ("function or method", re.compile(r"^\s*(?:def\s+\w+|fun\s+\w+|(?:[\w:<>&*]+\s+)+\w+\s*\([^;]*\)\s*(?:\{|$))"),
     "This line may declare a callable function or method; its body must be reviewed to establish behavior."),
    ("return statement", re.compile(r"^\s*return\b"),
     "This line returns a value or exits the current function."),
    ("conditional", re.compile(r"^\s*(?:if|elif|else if)\b"),
     "This line selects a conditional execution path."),
    ("loop", re.compile(r"^\s*(?:for|while)\b"),
     "This line begins a repeated execution path."),
    ("SQL operation", re.compile(r"\b(?:SELECT|INSERT|UPDATE|DELETE)\b", re.I),
     "This line contains a recognizable SQL operation; its target and effects require query-context review."),
)
REVIEW_PATTERNS = (
    ("unfinished_marker", re.compile(r"\b(?:TODO|FIXME|XXX|NotImplemented)\b", re.I),
     "An unfinished-work marker needs human review."),
    ("dynamic_execution", re.compile(r"\b(?:eval|exec)\s*\("),
     "Dynamic code execution is present; inspect its input and trust boundary."),
    ("process_or_shell", re.compile(r"\b(?:subprocess\.|Popen\s*\(|os\.system\s*\()"),
     "A process or shell operation is present; inspect authorization and argument handling."),
    ("network_operation", re.compile(r"\b(?:requests\.|urlopen\s*\(|fetch\s*\(|Socket\b)"),
     "A possible network operation is present; inspect destination and data handling."),
    ("database_mutation", re.compile(r"\b(?:INSERT\s+INTO|UPDATE\s+\w+|DELETE\s+FROM|DROP\s+TABLE)\b", re.I),
     "A database mutation statement is present; inspect transaction and authorization controls."),
)


def translate_file(repository: str | Path, relative_path: str) -> dict[str, Any]:
    root = Path(repository).expanduser().resolve(strict=True)
    if not relative_path or Path(relative_path).is_absolute():
        raise AeiError("A repository-relative source path is required.")
    suffix = Path(relative_path).suffix.lower()
    if suffix not in CODE_SUFFIXES:
        raise AeiError("Higher Faculty translation accepts recognized source-code extensions only.")

    inspected = inspect_file(root, relative_path, max_bytes=1_000_000)
    source_path = (root / relative_path).resolve(strict=True)
    if root not in source_path.parents or not source_path.is_file():
        raise AeiError("Source path is outside the selected repository.")
    raw = source_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != inspected.source_sha256:
        raise AeiError("Source changed during inspection; retry against a stable revision.")
    try:
        source_text = raw.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as exc:
        raise AeiError("Source is not valid UTF-8; bytes were not translated.") from exc

    lines = source_text.splitlines()
    discoveries = []
    review_flags = []
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("//", "/*", "*")):
            continue
        for construct, pattern, explanation in PATTERNS:
            if pattern.search(line):
                discoveries.append({
                    "line": number,
                    "construct": construct,
                    "source_text": line[:500],
                    "explanation": explanation,
                    "evidence_class": "INTERPRETATION",
                    "confidence": 0.55,
                })
                break
        for flag, pattern, message in REVIEW_PATTERNS:
            if pattern.search(line):
                review_flags.append({
                    "line": number,
                    "flag": flag,
                    "source_text": line[:500],
                    "review_question": message,
                })

    # Verification is deliberately limited to stable-byte provenance checks.
    verified = hashlib.sha256(raw).hexdigest() == inspected.source_sha256
    pipeline = [
        {"stage": "Discovery", "status": "COMPLETE",
         "detail": "Recognized bounded source constructs and retained line references."},
        {"stage": "Antithesis", "status": "REVIEW_REQUIRED" if review_flags else "NO_FLAGS_DETECTED",
         "detail": "Flagged potential risk or unfinished-work markers; absence of flags is not proof of correctness."},
        {"stage": "Verification", "status": "SOURCE_INTEGRITY_VERIFIED" if verified else "HOLD",
         "detail": "Compared the exact source-byte digest with Æị inspection metadata. Compilation and runtime behavior were not verified."},
        {"stage": "Creation", "status": "CANDIDATE_TRANSLATIONS_CREATED",
         "detail": "Created line-anchored English interpretations; original source remains untouched."},
    ]
    return {
        "translator": "Æị Higher Faculties",
        "version": VERSION,
        "status": "REVIEW_REQUIRED" if verified else "HOLD",
        "pipeline": pipeline,
        "source": {
            "path": inspected.source_path,
            "format": inspected.format,
            "size_bytes": len(raw),
            "sha256": digest,
            "authority": "NON_AUTHORITATIVE",
        },
        "translation": {
            "authority": "NON_AUTHORITATIVE",
            "evidence_class": "INTERPRETATION",
            "findings": discoveries,
            "finding_count": len(discoveries),
        },
        "antithesis": {
            "flags": review_flags,
            "flag_count": len(review_flags),
        },
        "verification": {
            "source_digest_matches": verified,
            "compilation": "NOT_PERFORMED",
            "runtime_tests": "NOT_PERFORMED",
            "semantic_correctness": "NOT_ESTABLISHED",
        },
        "preservation": {
            "source_bytes_modified": False,
            "source_file_written": False,
            "git_history_modified": False,
            "database_source_records_modified": False,
        },
        "pons": {
            "service_state": "ON",
            "authorization": "UNCHANGED",
            "execution_enabled": False,
            "translation_is_not_an_execution_grant": True,
        },
        "review_flags": [
            "Lexical recognition is not a full parser or semantic analysis.",
            "Candidate explanations require human review before indexing as accepted documentation.",
            "PONS capability approval remains separate from inspection and translation.",
        ],
    }
