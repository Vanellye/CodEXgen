"""Âï: evidence-grounded conversational analysis over Æị Higher Faculties.

This module is deterministic and repository-local. It analyzes source plus the
fresh Higher Faculty result; it is not an LLM, compiler, or security oracle.
All recommendations are proposals, never source mutations.
"""
from __future__ import annotations

import ast
import hashlib
import re
from pathlib import Path
from typing import Any

from .aei import AeiError, inspect_file
from .higher_faculties import CODE_SUFFIXES, SENSITIVE_PATH, translate_file

STOP_WORDS = {
    "a", "an", "and", "are", "about", "can", "could", "does", "do",
    "explain", "find", "for", "from", "give", "how", "i", "in", "is",
    "it", "me", "of", "on", "or", "please", "show", "tell", "the",
    "this", "to", "what", "which", "with", "would", "you", "your",
}
SKIP_DIRS = {
    ".git", ".idea", ".gradle", ".venv", "venv", "__pycache__",
    "node_modules", "build", "dist", "storage", ".eria",
}
MAX_SCAN_FILES = 600
MAX_SOURCE_BYTES = 1_000_000

SECURITY_RULES = (
    ("dynamic_execution", re.compile(r"\\b(?:eval|exec)\\s*\\("),
     "HIGH", "Dynamic code execution can turn untrusted strings into executable instructions.",
     "Remove dynamic evaluation where possible; otherwise constrain inputs, isolate execution, and add explicit authorization."),
    ("shell_execution", re.compile(r"\\b(?:os\\.system|subprocess\\.(?:run|Popen|call)|Runtime\\.getRuntime\\(\\)\\.exec)"),
     "HIGH", "Shell or process execution can expose command-injection and privilege-boundary risks.",
     "Prefer argument arrays without a shell, validate each argument, constrain executable paths, and enforce least privilege."),
    ("network_access", re.compile(r"\\b(?:requests\\.(?:get|post|put|delete)|urlopen\\s*\\(|fetch\\s*\\(|Socket\\s*\\()"),
     "MEDIUM", "Network access introduces destination, authentication, transport, and data-exfiltration concerns.",
     "Constrain destinations, validate TLS, apply timeouts, avoid sending secrets, and record permitted transfers."),
    ("sql_mutation", re.compile(r"\\b(?:INSERT\\s+INTO|UPDATE\\s+\\w+|DELETE\\s+FROM|DROP\\s+TABLE)\\b", re.I),
     "MEDIUM", "Database mutation can alter or destroy records if authorization and transaction boundaries are weak.",
     "Use parameterized statements, least-privilege connections, explicit transactions, backups, and immutable audit events."),
    ("embedded_secret_marker", re.compile(r"(?i)(?:api[_-]?key|password|secret|token)\\s*=\\s*['\"][^'\"]{8,}['\"]"),
     "HIGH", "A hard-coded credential-like assignment may expose a secret in source control.",
     "Move credentials to a managed secret provider, rotate exposed values, and prevent secret-bearing files from entering inspection artifacts."),
    ("unsafe_deserialization", re.compile(r"\\b(?:pickle\\.loads|yaml\\.load\\s*\\(|ObjectInputStream)"),
     "HIGH", "Deserializing untrusted data can enable object construction or code-execution paths.",
     "Use safe, schema-constrained formats and safe loaders; authenticate data and validate its shape before use."),
)

DEPENDENCY_PATTERNS = (
    re.compile(r"^\\s*import\\s+([\\w.]+)"),
    re.compile(r"^\\s*from\\s+([\\w.]+)\\s+import\\s+"),
    re.compile(r"^\\s*#include\\s*[<\"]([^>\"]+)[>\"]"),
    re.compile(r"^\\s*using\\s+([\\w:]+)"),
    re.compile(r"^\\s*require\\s*\\(?\\s*['\"]([^'\"]+)"),
)

FUNCTION_PATTERNS = (
    re.compile(r"^\\s*(?:async\\s+)?def\\s+(\\w+)\\s*\\("),
    re.compile(r"^\\s*(?:fun|function)\\s+(\\w+)\\s*\\("),
    re.compile(r"^\\s*(?:export\\s+)?(?:async\\s+)?function\\s+(\\w+)\\s*\\("),
    re.compile(r"^\\s*(?:[\\w:<>&*]+\\s+)+(\\w+)\\s*\\([^;]*\\)\\s*(?:\\{|$)"),
)
CLASS_PATTERNS = (
    re.compile(r"^\\s*class\\s+(\\w+)"),
    re.compile(r"^\\s*(?:struct|interface)\\s+(\\w+)"),
)


def _read_source(root: Path, relative_path: str) -> tuple[Path, bytes, str, str]:
    if not relative_path or Path(relative_path).is_absolute() or SENSITIVE_PATH.search(relative_path):
        raise AeiError("A non-sensitive repository-relative source path is required.")
    inspected = inspect_file(root, relative_path, max_bytes=MAX_SOURCE_BYTES)
    path = (root / relative_path).resolve(strict=True)
    if root not in path.parents or not path.is_file():
        raise AeiError("Source path escapes the selected repository.")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != inspected.source_sha256:
        raise AeiError("Source changed during Âï analysis; retry against a stable revision.")
    try:
        text = raw.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as exc:
        raise AeiError("Source is not valid UTF-8; binary source is not analyzed.") from exc
    return path, raw, text, digest


def _python_symbols(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    functions: list[dict[str, Any]] = []
    classes: list[dict[str, Any]] = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return functions, classes

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            functions.append({
                "name": node.name, "line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
                "docstring": ast.get_docstring(node) or "",
                "async": False,
                "calls": sorted({
                    child.func.id if isinstance(child.func, ast.Name)
                    else child.func.attr if isinstance(child.func, ast.Attribute)
                    else ""
                    for child in ast.walk(node) if isinstance(child, ast.Call)
                } - {""}),
                "returns": sorted({
                    ast.unparse(child.value)[:160]
                    for child in ast.walk(node)
                    if isinstance(child, ast.Return) and child.value is not None
                })[:8],
            })
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            self.visit_FunctionDef(node)
            functions[-1]["async"] = True

        def visit_ClassDef(self, node):
            classes.append({"name": node.name, "line": node.lineno,
                            "end_line": getattr(node, "end_lineno", node.lineno),
                            "bases": [ast.unparse(base) for base in node.bases]})
            self.generic_visit(node)

    Visitor().visit(tree)
    return functions, classes


def _symbols(text: str, suffix: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if suffix == ".py":
        return _python_symbols(text)
    functions: list[dict[str, Any]] = []
    classes: list[dict[str, Any]] = []
    for number, line in enumerate(text.splitlines(), 1):
        for pattern in FUNCTION_PATTERNS:
            match = pattern.search(line)
            if match:
                functions.append({"name": match.group(1), "line": number,
                                  "docstring": "", "calls": [], "returns": [],
                                  "analysis": "lexical declaration candidate"})
                break
        for pattern in CLASS_PATTERNS:
            match = pattern.search(line)
            if match:
                classes.append({"name": match.group(1), "line": number,
                                "analysis": "lexical declaration candidate"})
                break
    return functions, classes


def _dependencies(text: str) -> list[dict[str, Any]]:
    found = []
    seen = set()
    for number, line in enumerate(text.splitlines(), 1):
        for pattern in DEPENDENCY_PATTERNS:
            match = pattern.search(line)
            if match:
                name = match.group(1).strip()
                if name and name not in seen:
                    found.append({"name": name, "line": number,
                                  "source_line": line.strip()[:300],
                                  "kind": "declared import/include"})
                    seen.add(name)
                break
    return found


def _security(text: str) -> list[dict[str, Any]]:
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        for key, pattern, severity, implication, recommendation in SECURITY_RULES:
            if pattern.search(line):
                findings.append({
                    "rule": key, "line": number, "severity": severity,
                    "source_excerpt": line.strip()[:300],
                    "implication": implication,
                    "recommended_control": recommendation,
                    "evidence_class": "STATIC_PATTERN",
                })
    return findings


def _repository_conflicts(root: Path, target: Path, symbol_names: set[str]) -> list[dict[str, Any]]:
    if not symbol_names:
        return []
    matches = []
    scanned = 0
    for path in root.rglob("*"):
        if scanned >= MAX_SCAN_FILES or len(matches) >= 40:
            break
        if not path.is_file() or path.suffix.lower() not in CODE_SUFFIXES:
            continue
        try:
            relative = path.relative_to(root)
        except ValueError:
            continue
        if any(part in SKIP_DIRS or part.startswith(".") for part in relative.parts):
            continue
        if SENSITIVE_PATH.search(relative.as_posix()) or path == target:
            continue
        try:
            if path.stat().st_size > MAX_SOURCE_BYTES:
                continue
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError):
            continue
        scanned += 1
        funcs, classes = _symbols(text, path.suffix.lower())
        for kind, symbols in (("function", funcs), ("class", classes)):
            for symbol in symbols:
                if symbol["name"] in symbol_names:
                    matches.append({
                        "symbol": symbol["name"], "kind": kind,
                        "path": relative.as_posix(), "line": symbol["line"],
                        "relationship": "same-name candidate; semantic equivalence not established",
                    })
                    if len(matches) >= 40:
                        break
    return matches


def _purpose(function: dict[str, Any]) -> dict[str, Any]:
    doc = function.get("docstring", "").strip()
    calls = function.get("calls", [])
    returns = function.get("returns", [])
    if doc:
        basis = "Python docstring"
        purpose = doc
    else:
        basis = "name and static body features"
        purpose = (
            f"The name `{function['name']}` suggests its responsibility, "
            "but the repository evidence does not contain an explicit docstring."
        )
    return {
        "name": function["name"], "line": function["line"],
        "purpose": purpose, "basis": basis,
        "calls": calls, "return_expressions": returns,
        "confidence": "DOCUMENTED" if doc else "INFERRED_FROM_STRUCTURE",
    }


class AiiConversation:
    """Âï answers from fresh source inspection and Higher Faculty results."""

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
            "path": result.source_path, "sha256": result.source_sha256,
            "format": result.format, "size_bytes": result.size_bytes,
            "authority": result.source_authority,
        }
        low = question.casefold()
        if any(term in low for term in ("summary", "summarize", "overview", "describe this file")):
            answer = _summary(result)
            evidence = [{"pointer": "$", "basis": "Æị inspection metadata and parsed structure"}]
        else:
            terms = [token.casefold() for token in re.findall(r"[^\\W_]+", question, re.UNICODE)
                     if len(token) > 1 and token.casefold() not in STOP_WORDS]
            matches = []
            for pointer, value in _walk(result.data):
                rendered = str(value)
                searchable = (pointer + " " + rendered).casefold()
                if terms and any(term in searchable for term in terms):
                    matches.append({"pointer": pointer, "value": rendered[:500]})
                    if len(matches) >= 8:
                        break
            answer = (f"Æị found {len(matches)} matching evidence item(s) in {result.source_path}."
                      if matches else "I cannot answer that from the inspected file.")
            evidence = matches
        return {
            "translator": "Âï", "engine": "ERIA/PANTHEON",
            "mode": "evidence_grounded_retrieval",
            "status": "answered" if evidence else "insufficient_evidence",
            "answer": answer, "source": source, "evidence": evidence,
            "limitations": [
                "This is deterministic retrieval, not a generative language model.",
                "Source and derived authority remain NON_AUTHORITATIVE.",
                "No source files or databases are modified.",
            ],
        }

    def ask_higher_faculty(self, relative_path: str, question: str,
                           comparison_path: str | None = None) -> dict[str, Any]:
        question = question.strip()
        if not question or len(question) > 2000:
            raise AeiError("Question must contain 1 to 2,000 characters.")
        translation = translate_file(self.root, relative_path)
        path, raw, source_text, digest = _read_source(self.root, relative_path)
        functions, classes = _symbols(source_text, path.suffix.lower())
        dependencies = _dependencies(source_text)
        security = _security(source_text)
        function_names = {item["name"] for item in functions}
        class_names = {item["name"] for item in classes}
        low = question.casefold()

        purpose = [_purpose(item) for item in functions]
        if not purpose and classes:
            purpose = [{"name": item["name"], "line": item["line"],
                        "purpose": "Class/type declaration found; inspect its methods and callers to establish responsibility.",
                        "basis": "static declaration", "confidence": "STRUCTURAL_ONLY"}
                       for item in classes]
        conflicts = _repository_conflicts(self.root, path, function_names | class_names)

        if comparison_path:
            other_path, other_raw, other_text, other_hash = _read_source(self.root, comparison_path)
            comparison = {
                "path": comparison_path,
                "sha256": other_hash,
                "same_bytes": digest == other_hash,
                "same_symbol_names": sorted(function_names & {
                    item["name"] for item in _symbols(other_text, other_path.suffix.lower())[0]
                }),
                "source_diff": {
                    "only_in_primary": sorted(set(source_text.splitlines()) - set(other_text.splitlines()))[:80],
                    "only_in_comparison": sorted(set(other_text.splitlines()) - set(source_text.splitlines()))[:80],
                },
            }
        else:
            comparison = None

        recommendations = []
        if security:
            for item in security:
                recommendations.append({
                    "priority": item["severity"], "line": item["line"],
                    "proposal": item["recommended_control"],
                    "basis": item["rule"], "requires_human_review": True,
                })
        if not security:
            recommendations.append({
                "priority": "REVIEW", "proposal": "Add or confirm tests for boundary conditions, error paths, and authorization before changing implementation.",
                "basis": "No matching static security patterns; this is not proof of safety.",
                "requires_human_review": True,
            })

        if any(term in low for term in ("why", "purpose", "exist", "responsibility")):
            selected = {"function_purpose": purpose}
            answer = "Function and type responsibilities were extracted from declarations, docstrings, calls, and return expressions. Where documentation is absent, purpose is explicitly marked as an inference."
        elif any(term in low for term in ("depend", "import", "include", "library", "require")):
            selected = {"dependencies": dependencies}
            answer = "These are dependencies explicitly declared in the inspected source. Transitive dependencies and runtime-loaded modules are not inferred."
        elif any(term in low for term in ("conflict", "duplicate", "overlap", "implementation", "same function")):
            selected = {"conflicting_implementations": conflicts}
            answer = "Same-name declarations in other repository files are candidate conflicts only; matching names do not prove equivalent behavior or a true conflict."
        elif any(term in low for term in ("security", "secure", "vulnerab", "risk", "threat")):
            selected = {"security_implications": security}
            answer = "Security observations are static pattern matches with line references, not confirmed vulnerabilities or a complete security audit."
        elif any(term in low for term in ("improve", "better", "optim", "refactor", "proposal")):
            selected = {"improvement_proposals": recommendations}
            answer = "These are reviewable improvement proposals. Âï has not edited, compiled, or executed the source."
        elif any(term in low for term in ("compare", "translation", "english", "original", "versus", "vs")):
            selected = {"source_translation_comparison": {
                "source_sha256": digest,
                "translation_findings": translation["translation"]["findings"],
                "finding_count": translation["translation"]["finding_count"],
                "translation_authority": translation["translation"]["authority"],
                "note": "Each candidate interpretation retains its original source line and excerpt. Translation is not a replacement for source.",
            }}
            answer = "The English interpretations are paired with original line numbers and excerpts. They are non-authoritative and may be incomplete."
        else:
            selected = {
                "function_purpose": purpose, "dependencies": dependencies,
                "conflicting_implementations": conflicts,
                "security_implications": security,
                "improvement_proposals": recommendations,
                "source_translation_comparison": {
                    "source_sha256": digest,
                    "translation_findings": translation["translation"]["findings"],
                    "finding_count": translation["translation"]["finding_count"],
                    "translation_authority": translation["translation"]["authority"],
                },
            }
            answer = "Here is the Higher Faculty evidence profile for the selected source. Ask a focused follow-up to inspect one dimension in depth."

        return {
            "translator": "Âï", "engine": "ERIA/PANTHEON",
            "mode": "higher_faculty_evidence_analysis",
            "status": "answered",
            "answer": answer,
            "source": {"path": relative_path, "sha256": digest,
                       "size_bytes": len(raw), "authority": "NON_AUTHORITATIVE"},
            "higher_faculty": translation,
            "analysis": selected,
            "comparison": comparison,
            "pons": {"service_state": "ON", "authorization": "UNCHANGED",
                     "execution_enabled": False, "write_enabled": False},
            "limitations": [
                "Âï uses deterministic static analysis and retrieval, not an LLM.",
                "Purpose without documentation is an inference, not an established design intent.",
                "Dependencies list direct declarations only; transitive/runtime dependencies are not resolved.",
                "Same-name symbols are candidates for review, not proof of conflicting behavior.",
                "Security rules are incomplete static heuristics, not a vulnerability verdict.",
                "Improvement proposals are not applied to source.",
                "Compilation, tests, and runtime behavior are not verified by this analysis.",
            ],
        }


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
