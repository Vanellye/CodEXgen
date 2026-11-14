"""Âï: evidence-grounded conversation over Æị read-only inspections.

This is a deterministic retrieval/answer layer, not an LLM. Every factual
answer is tied to a fresh Æị inspection and carries source-path/hash evidence.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .aei import AeiError, inspect_file

STOP_WORDS = {
    "a", "an", "and", "are", "about", "can", "could", "does", "do",
    "explain", "find", "for", "from", "give", "how", "i", "in", "is",
    "it", "me", "of", "on", "or", "please", "show", "tell", "the",
    "this", "to", "what", "which", "with", "would", "you", "your",
}
SENSITIVE_NAME = re.compile(
    r"(^|[/_.-])(.env|secrets?|credentials?|private[_-]?key|id_rsa)([/_.-]|$)",
    re.IGNORECASE,
)


def _walk(value: Any, pointer: str = "$"):
    if isinstance(value, dict):
        for key, child in value.items():
            escaped = str(key).replace("~", "~0").replace("/", "~1")
            yield from _walk(child, pointer + "/" + escaped)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, pointer + "/" + str(index))
    else:
        yield pointer, value


def _summary(result) -> str:
    data = result.data
    parts = [
        f"Æị inspected {result.source_path} as {result.format}.",
        f"Inspection status: {result.status}.",
        f"File size: {result.size_bytes} bytes.",
    ]
    if result.format == "SQLite":
        tables = data.get("tables", [])
        names = [table.get("table") for table in tables]
        parts.append(f"SQLite tables found: {data.get('table_count', len(tables))}.")
        if names:
            parts.append("Tables: " + ", ".join(str(name) for name in names) + ".")
    elif result.format == "CSV":
        parts.append("Columns: " + ", ".join(data.get("columns") or []) + ".")
        parts.append(f"Preview rows: {len(data.get('rows_preview', []))}.")
    elif result.format == "JSON":
        parts.append(
            f"JSON top-level type: {data.get('top_level_type')}; "
            f"top-level item count: {data.get('item_count')}."
        )
    elif "line_count" in data:
        parts.append(f"Text lines: {data['line_count']}.")
    if result.limitations:
        parts.append("Limitations: " + " ".join(result.limitations))
    return " ".join(parts)


class AiiConversation:
    """Answer questions only from a fresh Æị inspection of the named file."""

    def __init__(self, repository: str | Path):
        self.root = Path(repository).expanduser().resolve(strict=True)
        if not self.root.is_dir():
            raise AeiError("Selected repository root is not a directory.")

    def ask(self, relative_path: str, question: str) -> dict[str, Any]:
        question = question.strip()
        if not question:
            raise AeiError("Enter a question for Âï.")
        if len(question) > 2000:
            raise AeiError("Question exceeds the 2,000-character limit.")
        if SENSITIVE_NAME.search(relative_path):
            raise AeiError("Âï will not conversationally inspect credential-like paths.")
        result = inspect_file(self.root, relative_path)
        source = {
            "path": result.source_path,
            "sha256": result.source_sha256,
            "format": result.format,
            "size_bytes": result.size_bytes,
            "authority": result.source_authority,
        }
        low = question.casefold()
        if any(term in low for term in ("summary", "summarize", "overview", "describe this file")):
            answer = _summary(result)
            evidence = [{"pointer": "$", "basis": "Æị inspection metadata and parsed structure"}]
        else:
            terms = [
                token.casefold() for token in re.findall(r"[^\W_]+", question, re.UNICODE)
                if len(token) > 1 and token.casefold() not in STOP_WORDS
            ]
            matches = []
            for pointer, value in _walk(result.data):
                rendered = str(value)
                searchable = (pointer + " " + rendered).casefold()
                if terms and any(term in searchable for term in terms):
                    matches.append({
                        "pointer": pointer,
                        "value": rendered[:500],
                    })
                    if len(matches) >= 8:
                        break
            if matches:
                answer = (
                    f"Æị found {len(matches)} matching evidence item(s) in "
                    f"{result.source_path}. These are source-derived matches, "
                    "not independent verification or inferred facts."
                )
                evidence = matches
            else:
                answer = (
                    "I cannot answer that from the inspected file. Æị found no "
                    "matching evidence for the question; provide a more specific "
                    "term or inspect another source."
                )
                evidence = []
        return {
            "translator": "Âï",
            "engine": "ERIA/PANTHEON",
            "mode": "evidence_grounded_retrieval",
            "status": "answered" if evidence else "insufficient_evidence",
            "answer": answer,
            "source": source,
            "evidence": evidence,
            "limitations": [
                "Âï is a deterministic retrieval layer, not a generative language model.",
                "Answers are limited to the freshly inspected file and its parsed preview.",
                "Source and derived authority remain NON_AUTHORITATIVE.",
                "No source files or databases are modified.",
            ],
        }
