#!/usr/bin/env python3
"""Conversation adapter for ERIA/PANTHEON; local inspection and audit only."""
from __future__ import annotations

import json
import shlex
from typing import Any

from .aei import AeiError, inspect_file
from .ai import AiiConversation
from .pons import BridgeEnvelope, Pons
from .storage import AeiStorage


class ERIAPantheonInterface:
    def __init__(self, repository: Any) -> None:
        self.repository = repository
        self.bridge = Pons()
        self.bridge.register(AiiConversation, lambda: AiiConversation(self.repository.root))
        self.bridge.register(AeiStorage, lambda: AeiStorage(self.repository.root))

    def status(self) -> str:
        state = self.bridge.describe()
        state["repository"] = str(self.repository.root)
        state["conversation_engine"] = "connected"
        try:
            import eria_ttt_bypass  # noqa: F401
            state["code_bypass_module"] = "available"
        except ImportError:
            state["code_bypass_module"] = "missing"
        return "ERIA/PANTHEON integration status\n" + "\n".join(
            f"{key}: {value}" for key, value in state.items()
        )

    def handle(self, command: str) -> str:
        low = command.strip().lower()
        if low in {"integration.status", "bridge.status", "pons.status"}:
            return self.status()
        if low.startswith("code.bypass "):
            return self._code_bypass(command.strip()[len("code.bypass "):])
        if low.startswith("aei.compile "):
            return self._aei_compile(command.strip()[len("aei.compile "):])
        if low.startswith(("aei.inspect ", "aei.translate ")):
            prefix = "aei.inspect " if low.startswith("aei.inspect ") else "aei.translate "
            return self._aei_inspect(command.strip()[len(prefix):])
        if low.startswith("ai.ask "):
            return self._ai_ask(command.strip()[len("ai.ask "):])
        if low.startswith("repository.ask "):
            return self.repository.ask(command.strip()[len("repository.ask "):])
        return (
            "Supported commands: integration.status, bridge.status, "
            "repository.ask <question>, "
            "aei.inspect <repo-relative-path>, "
            "aei.translate <repo-relative-path> (read-only), "
            "aei.compile <repo-relative-path> (store derived copy), "
            "ai.ask <repo-relative-path> --question <text>, "
            "code.bypass <repo-relative-path> --reason <text>"
        )

    def _aei_compile(self, arguments: str) -> str:
        try:
            tokens = shlex.split(arguments)
        except ValueError as exc:
            return f"HOLD: invalid Æị compile command quoting: {exc}"
        if len(tokens) != 1:
            return "HOLD: provide exactly one repository-relative source path."
        try:
            result = self.bridge.resolve(AeiStorage).compile(tokens[0])
        except (AeiError, OSError, ValueError) as exc:
            return json.dumps({"translator": "Æị", "status": "HOLD", "error": str(exc)},
                              ensure_ascii=False, indent=2)
        return json.dumps(result, ensure_ascii=False, indent=2)

    def _aei_inspect(self, arguments: str) -> str:
        try:
            tokens = shlex.split(arguments)
        except ValueError as exc:
            return f"HOLD: invalid Æị command quoting: {exc}"
        if len(tokens) != 1:
            return "HOLD: provide exactly one repository-relative file path."
        try:
            result = inspect_file(self.repository.root, tokens[0])
        except (AeiError, OSError) as exc:
            return f"HOLD: Æị inspection failed: {exc}"
        return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)

    def _ai_ask(self, arguments: str) -> str:
        try:
            tokens = shlex.split(arguments)
        except ValueError as exc:
            return f"HOLD: invalid Âï command quoting: {exc}"
        if "--question" not in tokens:
            return "HOLD: ai.ask requires --question <text>."
        index = tokens.index("--question")
        if index != 1 or len(tokens) <= index + 1:
            return "HOLD: use ai.ask <repo-relative-path> --question <text>."
        path = tokens[0]
        question = " ".join(tokens[index + 1:])
        try:
            result = self.bridge.resolve(AiiConversation).ask(path, question)
        except (AeiError, OSError, ValueError) as exc:
            return json.dumps({"translator": "Âï", "status": "HOLD", "error": str(exc)},
                              ensure_ascii=False, indent=2)
        return json.dumps(result, ensure_ascii=False, indent=2)

    def _code_bypass(self, arguments: str) -> str:
        try:
            tokens = shlex.split(arguments)
        except ValueError as exc:
            return f"HOLD: invalid command quoting: {exc}"
        if not tokens:
            return "HOLD: provide a repository-relative source path."
        source_name = tokens[0]
        reason = ""
        if "--reason" in tokens:
            idx = tokens.index("--reason")
            reason = " ".join(tokens[idx + 1:]).strip()
        if not reason:
            return "HOLD: --reason is required for an auditable code bypass."

        path = (self.repository.root / source_name).resolve()
        root = self.repository.root.resolve()
        if path == root or root not in path.parents:
            return "HOLD: source path escapes repository root."
        if not path.is_file():
            return "HOLD: source is not a regular file."
        if path.stat().st_size > 1_000_000:
            return "HOLD: source exceeds the 1 MB inspection limit."
        raw = path.read_bytes()
        if b"\x00" in raw[:8192]:
            return "HOLD: binary source is not classified as text code."

        try:
            from eria_ttt_bypass import process_payload
            result = process_payload(
                raw, content_kind="code", bypass_code=True, reason=reason,
                translator=lambda value: (_ for _ in ()).throw(
                    AssertionError("translator must not run")),
                transmitter=lambda value: (_ for _ in ()).throw(
                    AssertionError("transmitter must not run")),
                source_name=source_name,
            )
        except (ImportError, OSError, ValueError, TypeError) as exc:
            return f"HOLD: bypass/audit failed closed: {exc}"

        envelope = BridgeEnvelope.from_bytes(
            raw, source_name, repository=str(root),
            bypass_status=result.status, audit_path=result.audit_path,
        )
        return (
            f"{result.status}\nsource: {source_name}\n"
            f"source_sha256: {envelope.source_sha256}\n"
            f"source_authority: {envelope.source_authority}\n"
            "translator_invoked: false\ntransmitter_invoked: false\n"
            f"audit: {result.audit_path}\nrepository_mutated: false"
        )
