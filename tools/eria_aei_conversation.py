#!/usr/bin/env python3
"""ERIA Æi Conversational Intelligence Layer.

Transparent, evidence-grounded conversation shell over the read-only
repository inspector and Æ translator. Deterministic local orchestration;
not a claim of an embedded general-purpose language model.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from typing import Optional

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from eria_repository_conversation import Conversation, Repository, RepoError
from eria_database_translator import canonical_envelope, read_bytes
from eria_aei_platform_db import PlatformDatabase

class ÆiConversation:
    def __init__(self, repository: str = "."):
        self.repository = Repository(repository)
        self.repo_chat = Conversation(self.repository)
        self.session_facts = []

    @staticmethod
    def intent(question: str) -> str:
        q = question.lower()
        groups = {
            "translate": ("translate", "decode", "convert", "interpret"),
            "summarize": ("summarize", "summary", "overview"),
            "explain": ("explain", "what does", "how does", "meaning"),
            "compare": ("compare", "difference", "versus", " vs "),
            "evidence": ("evidence", "prove", "verified", "source")
        }
        for name, terms in groups.items():
            if any(term in q for term in terms):
                return name
        return "ask"

    @staticmethod
    def path_from_question(question: str) -> Optional[str]:
        match = re.search(r"(?:^|\s)file:([^\s]+)", question)
        return match.group(1) if match else None

    def respond(self, question: str) -> dict:
        q = question.strip()
        if not q:
            return {"status": "needs_input", "message": "Ask a repository or source question."}
        intent = self.intent(q)
        rel = self.path_from_question(q)
        if rel:
            root = self.repository.root
            candidate = (root / rel).resolve()
            if root != candidate and root not in candidate.parents:
                raise ValueError("Requested path escapes repository root.")
            envelope = canonical_envelope(candidate, read_bytes(candidate))
            source, content = envelope["source"], envelope["content"]
            self.session_facts.append({
                "path": rel, "sha256": source["sha256"], "format": source["format"]
            })
            answer = (
                f"Inspected {rel}: format={source['format']}, "
                f"size={source['size_bytes']} bytes, SHA-256={source['sha256']}. "
                f"Content category={content['kind']}. "
                "This establishes file identity and structure, not the truth "
                "of claims inside the file."
            )
            if intent == "translate":
                answer += " The source remains unchanged; use eria_database_translator.py to create a separate export."
            return {
                "status": "answered", "intent": intent, "answer": answer,
                "evidence": [{"path": rel, "sha256": source["sha256"],
                              "format": source["format"], "classification": "OBSERVED"}],
                "limits": ["No source mutation", "No code execution",
                           "No external model inference"]
            }
        low = q.lower()
        if any(term in low for term in ("database status", "platform database status", "sqlite status")):
            try:
                status = PlatformDatabase().status()
                return {"status": "answered", "intent": "database_status",
                        "answer": json.dumps(status, ensure_ascii=False, indent=2),
                        "evidence": [{"database": status["database"],
                                      "integrity": status["integrity"],
                                      "classification": "OBSERVED"}],
                        "limits": ["Database opened read-only", "No SQL writes exposed"]}
            except Exception as exc:
                return {"status": "unavailable", "intent": "database_status",
                        "answer": str(exc), "evidence": [],
                        "limits": ["No database changes were made"]}
        if any(term in low for term in ("registered source urls", "source url list", "show source urls")):
            try:
                urls = PlatformDatabase().source_urls()
                return {"status": "answered", "intent": "source_urls",
                        "answer": json.dumps(urls, ensure_ascii=False, indent=2),
                        "evidence": [{"record_count": len(urls),
                                      "classification": "OBSERVED"}],
                        "limits": ["Read-only query", "Results reflect current local database"]}
            except Exception as exc:
                return {"status": "unavailable", "intent": "source_urls",
                        "answer": str(exc), "evidence": [],
                        "limits": ["No database changes were made"]}
        if any(term in low for term in ("translation artifacts", "artifact summary", "derived artifacts")):
            try:
                summary = PlatformDatabase().artifact_summary()
                return {"status": "answered", "intent": "artifact_summary",
                        "answer": json.dumps(summary, ensure_ascii=False, indent=2),
                        "evidence": [{"record_count": summary["count"],
                                      "classification": "OBSERVED"}],
                        "limits": ["Read-only query", "No artifact records were modified"]}
            except Exception as exc:
                return {"status": "unavailable", "intent": "artifact_summary",
                        "answer": str(exc), "evidence": [],
                        "limits": ["No database changes were made"]}
        answer = self.repo_chat.ask(q)
        return {
            "status": "answered", "intent": intent, "answer": answer,
            "evidence": [],
            "limits": [
                "Repository responses use read-only inspection and text matches.",
                "Claims are not marked VERIFIED without independent evidence.",
                "This layer is deterministic, not a hosted or trained LLM."
            ]
        }

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repository", nargs="?", default=".")
    ap.add_argument("-q", "--question")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        agent = ÆiConversation(args.repository)
    except RepoError as exc:
        print(f"ERIA Æi: {exc}", file=sys.stderr)
        return 2
    def emit(question):
        result = agent.respond(question)
        print(json.dumps(result, ensure_ascii=False, indent=2)
              if args.json else result.get("answer", result.get("message", "")))
    if args.question:
        emit(args.question)
        return 0
    print("ERIA Æi Conversational Intelligence")
    print(f"Repository: {agent.repository.root}")
    print("Read-only, evidence-grounded mode. Type quit to exit.")
    while True:
        try:
            question = input("Æi> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in {"quit", "exit"}:
            break
        if question:
            emit(question)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
