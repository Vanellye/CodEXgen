#!/usr/bin/env python3
"""Connect ERIA quality reports to Æị inspection and Âï conversation.

All artifacts are stored outside the checkout under ~/.eria/qualitative.
The bridge is read-only with respect to repository source and Git history.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from eria_quality_mixer import scan


def now():
    return datetime.now(timezone.utc).isoformat()


class QualityBridge:
    def __init__(self, repository_root: Path, source_database: Path,
                 storage_root: Path | None = None):
        self.root = Path(repository_root).expanduser().resolve()
        self.source_database = Path(source_database).expanduser().resolve()
        self.home = Path(storage_root or (Path.home() / ".eria" / "qualitative")).expanduser().resolve()
        self.reports = self.home / "reports"
        self.proposals = self.home / "proposals"
        self.reports.mkdir(parents=True, exist_ok=True)
        self.proposals.mkdir(parents=True, exist_ok=True)
        self.database = self.home / "qualitative.sqlite3"
        self._init_db()

    def connect(self):
        db = sqlite3.connect(str(self.database), timeout=20)
        db.row_factory = sqlite3.Row
        return db

    def _init_db(self):
        with self.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS quality_reports(
              report_id TEXT PRIMARY KEY, generated_at TEXT NOT NULL,
              repository TEXT NOT NULL, branch TEXT NOT NULL, head_commit TEXT NOT NULL,
              report_path TEXT NOT NULL, report_sha256 TEXT NOT NULL,
              file_count INTEGER NOT NULL, finding_count INTEGER NOT NULL,
              candidate_count INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS quality_findings(
              report_id TEXT NOT NULL, finding_key TEXT NOT NULL,
              rule TEXT NOT NULL, severity TEXT NOT NULL, path TEXT NOT NULL,
              line INTEGER NOT NULL, message TEXT NOT NULL,
              PRIMARY KEY(report_id,finding_key)
            );
            CREATE INDEX IF NOT EXISTS idx_quality_findings_report_severity
              ON quality_findings(report_id,severity,path);
            CREATE TABLE IF NOT EXISTS quality_candidates(
              report_id TEXT NOT NULL, symbol TEXT NOT NULL, paths_json TEXT NOT NULL,
              rank_score REAL NOT NULL, rationale TEXT NOT NULL,
              PRIMARY KEY(report_id,symbol)
            );
            CREATE TABLE IF NOT EXISTS quality_proposals(
              proposal_id TEXT PRIMARY KEY, report_id TEXT NOT NULL,
              title TEXT NOT NULL, symbol TEXT NOT NULL, paths_json TEXT NOT NULL,
              evidence_json TEXT NOT NULL, status TEXT NOT NULL,
              created_at TEXT NOT NULL, proposal_path TEXT NOT NULL
            );
            CREATE TRIGGER IF NOT EXISTS quality_reports_no_update
              BEFORE UPDATE ON quality_reports BEGIN
                SELECT RAISE(ABORT,'quality report history is append-only');
              END;
            CREATE TRIGGER IF NOT EXISTS quality_reports_no_delete
              BEFORE DELETE ON quality_reports BEGIN
                SELECT RAISE(ABORT,'quality report history is append-only');
              END;
            CREATE TRIGGER IF NOT EXISTS quality_findings_no_update
              BEFORE UPDATE ON quality_findings BEGIN
                SELECT RAISE(ABORT,'quality findings are append-only');
              END;
            CREATE TRIGGER IF NOT EXISTS quality_findings_no_delete
              BEFORE DELETE ON quality_findings BEGIN
                SELECT RAISE(ABORT,'quality findings are append-only');
              END;
            """)

    def _source_comparisons(self):
        if not self.source_database.exists():
            return []
        try:
            with sqlite3.connect(str(self.source_database), timeout=5) as db:
                tables = {r[0] for r in db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'")}
                if not {"pull_files"}.issubset(tables):
                    return []
                rows = db.execute("""
                  SELECT path,source,sha256,source_commit,status
                  FROM pull_files WHERE status='present'
                  ORDER BY path,source
                """).fetchall()
        except sqlite3.Error:
            return []
        grouped = {}
        for path, source, digest, commit, status in rows:
            grouped.setdefault(path, {})[source] = {
                "sha256": digest, "commit": commit, "status": status}
        return [{"path": p, "local": v["local"], "github": v["github"],
                 "same_content": v["local"]["sha256"] == v["github"]["sha256"]}
                for p, v in sorted(grouped.items())
                if "local" in v and "github" in v
                and v["local"]["sha256"] != v["github"]["sha256"]]

    @staticmethod
    def _rank(report):
        file_scores = {f["path"]: f.get("static_score", 0) for f in report.get("files", [])}
        finding_counts = {}
        for finding in report.get("findings", []):
            key = finding["path"]
            finding_counts[key] = finding_counts.get(key, 0) + (
                {"high": 25, "medium": 10, "low": 2}.get(finding.get("severity"), 0))
        ranked = []
        for item in report.get("mix_candidates", []):
            paths = sorted(set(item.get("candidate_paths", [])))
            scores = [file_scores.get(p, 0) for p in paths]
            mean = sum(scores) / len(scores) if scores else 0
            overlap_bonus = min(15, max(0, len(paths) - 1) * 5)
            risk_penalty = sum(finding_counts.get(p, 0) for p in paths) / max(1, len(paths))
            score = round(max(0, min(100, mean * 0.75 + overlap_bonus - risk_penalty)), 2)
            ranked.append({"symbol": item.get("symbol", ""), "candidate_paths": paths,
                           "rank_score": score,
                           "rationale": "Weighted heuristic: 75% mean static score, up to 15 points for independent implementations, minus severity-weighted finding burden. Not a correctness verdict."})
        return sorted(ranked, key=lambda x: (-x["rank_score"], x["symbol"]))

    def refresh(self):
        report = scan(self.root)
        report["source_comparisons"] = self._source_comparisons()
        report["quality_bridge"] = {
            "storage_root": str(self.home),
            "source_comparison_count": len(report["source_comparisons"]),
            "ranking": "heuristic_triage_only",
            "write_policy": "proposal_only; source changes require separate explicit approval",
        }
        raw = (json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode()
        digest = hashlib.sha256(raw).hexdigest()
        report_id = str(uuid.uuid4())
        stamp = now()
        prov = report.get("provenance", {})
        filename = self.reports / (stamp.replace(":", "").replace("+", "_") + "-" + report_id[:8] + ".json")
        filename.write_bytes(raw)
        ranked = self._rank(report)
        findings = report.get("findings", [])
        with self.connect() as db:
            db.execute("""INSERT INTO quality_reports VALUES(?,?,?,?,?,?,?,?,?,?)""", (
                report_id, report.get("generated_at", stamp), str(self.root),
                prov.get("branch", ""), prov.get("head_commit", ""), str(filename),
                digest, report.get("summary", {}).get("files_assessed", 0),
                len(findings), len(ranked)))
            for i, item in enumerate(findings):
                key = hashlib.sha256(json.dumps(item, sort_keys=True).encode()).hexdigest()
                db.execute("INSERT OR IGNORE INTO quality_findings VALUES(?,?,?,?,?,?,?)", (
                    report_id, key, item.get("rule", ""), item.get("severity", "unknown"),
                    item.get("path", ""), int(item.get("line", 0)), item.get("message", "")))
            for item in ranked:
                db.execute("INSERT INTO quality_candidates VALUES(?,?,?,?,?)", (
                    report_id, item["symbol"], json.dumps(item["candidate_paths"]),
                    item["rank_score"], item["rationale"]))
        report["report_id"] = report_id
        report["report_sha256"] = digest
        report["report_path"] = str(filename)
        return report

    def latest(self):
        with self.connect() as db:
            row = db.execute("SELECT * FROM quality_reports ORDER BY generated_at DESC LIMIT 1").fetchone()
        if not row:
            return None
        path = Path(row["report_path"])
        if not path.is_file():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        data["report_id"] = row["report_id"]
        data["report_sha256"] = row["report_sha256"]
        data["report_path"] = str(path)
        return data

    def summary(self):
        report = self.latest()
        if report is None:
            return {"ready": False, "storage_root": str(self.home),
                    "message": "No qualitative report stored yet. Run a refresh."}
        summary = report.get("summary", {})
        return {"ready": True, "report_id": report["report_id"],
                "generated_at": report.get("generated_at"),
                "provenance": report.get("provenance", {}),
                "storage_root": str(self.home), "report_path": report["report_path"],
                "report_sha256": report["report_sha256"], "summary": summary,
                "source_comparison_count": len(report.get("source_comparisons", [])),
                "ranked_candidates": len(self._rank(report))}

    def findings(self, severity: str = "", path: str = "", limit: int = 100):
        report = self.latest()
        if report is None:
            return []
        allowed = {"", "high", "medium", "low"}
        if severity not in allowed:
            raise ValueError("severity must be high, medium, or low")
        result = [x for x in report.get("findings", [])
                  if (not severity or x.get("severity") == severity)
                  and (not path or path.lower() in x.get("path", "").lower())]
        return result[:max(1, min(int(limit), 500))]

    def candidates(self, limit: int = 100):
        report = self.latest()
        if report is None:
            return []
        return self._rank(report)[:max(1, min(int(limit), 250))]

    def prepare_proposal(self, symbol: str):
        report = self.latest()
        if report is None:
            raise ValueError("Refresh the quality report before preparing a proposal.")
        item = next((x for x in self._rank(report) if x["symbol"] == symbol), None)
        if item is None:
            raise ValueError("Candidate symbol is not present in the latest report.")
        by_path = {x["path"]: x for x in report.get("files", [])}
        evidence = {
            "report_id": report["report_id"], "report_sha256": report["report_sha256"],
            "repository_provenance": report.get("provenance", {}),
            "candidate": item,
            "source_fingerprints": {p: by_path.get(p, {}).get("sha256", "") for p in item["candidate_paths"]},
            "related_findings": [f for f in report.get("findings", [])
                                 if f.get("path") in item["candidate_paths"]],
            "comparison": "Inspect interfaces, call sites, tests, dependency contracts and behavior before selecting a canonical implementation.",
            "approval_boundary": "REVIEW_REQUIRED; no source file, Git ref, commit, or SQLite source record has been changed.",
        }
        proposal_id = str(uuid.uuid4())
        payload = {"proposal_id": proposal_id, "title": "Review synthesis candidate: " + symbol,
                   "symbol": symbol, "paths": item["candidate_paths"],
                   "status": "REVIEW_REQUIRED", "created_at": now(), "evidence": evidence,
                   "recommended_next_steps": [
                       "Æị: inspect each implementation and compare interfaces and dependencies",
                       "Âï: explain purpose, conflicts, security implications and behavioral differences",
                       "Verification: run relevant tests in an isolated environment",
                       "Human approval: authorize a narrowly scoped patch before any repository write",
                   ]}
        destination = self.proposals / (proposal_id + ".json")
        destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        with self.connect() as db:
            db.execute("INSERT INTO quality_proposals VALUES(?,?,?,?,?,?,?,?,?)", (
                proposal_id, report["report_id"], payload["title"], symbol,
                json.dumps(item["candidate_paths"]), json.dumps(evidence, ensure_ascii=False),
                payload["status"], payload["created_at"], str(destination)))
        return payload

    def conversation_context(self, question: str):
        if not re.search(r"quality|finding|risk|duplicate|conflict|implement|synth|compare|assessment|security|score|candidate", question, re.I):
            return ""
        report = self.latest()
        if report is None:
            return "QUALITY BRIDGE: No qualitative assessment is stored yet. Use the quality refresh control first."
        ranked = self._rank(report)
        high = [f for f in report.get("findings", []) if f.get("severity") == "high"]
        medium = [f for f in report.get("findings", []) if f.get("severity") == "medium"]
        selected = high[:12] + medium[:8]
        lines = [
            "QUALITATIVE EVIDENCE FOR Æị INSPECTION AND Âï CONVERSATION",
            "Report: " + report["report_id"] + " | SHA-256: " + report["report_sha256"],
            "Branch: " + report.get("provenance", {}).get("branch", "unknown") +
            " | HEAD: " + report.get("provenance", {}).get("head_commit", "unknown"),
            "Files assessed: " + str(report.get("summary", {}).get("files_assessed", 0)),
            "Findings: " + json.dumps(report.get("summary", {}).get("findings", {})),
            "High/medium evidence: " + json.dumps(selected, ensure_ascii=False),
            "Top synthesis candidates: " + json.dumps(ranked[:10], ensure_ascii=False),
            "Source divergences (local vs GitHub): " + json.dumps(report.get("source_comparisons", [])[:20], ensure_ascii=False),
            "Interpretation rule: findings are static heuristics, not proof. Preserve source bytes and provenance. Do not claim tests passed unless separately evidenced.",
            "Write boundary: prepare proposals only; no repository writes or Git operations are authorized by this report.",
        ]
        return "\n".join(lines)


    def answer(self, question: str):
        """Deterministic evidence explanation for quality-related Âï questions."""
        if not re.search(r"quality|finding|risk|duplicate|conflict|implement|synth|compare|assessment|security|score|candidate|why .*function|dependencies", question, re.I):
            return None
        report = self.latest()
        if report is None:
            return "Qualitative assessment is not stored yet. Use Refresh Quality to create the first report."
        ranked = self._rank(report)
        lines = [
            "Âï QUALITATIVE REVIEW (evidence-backed; heuristic, not a certification)",
            "Report " + report["report_id"] + " · " + report["report_sha256"],
            "Repository: " + report.get("provenance", {}).get("branch", "unknown") +
            " @ " + report.get("provenance", {}).get("head_commit", "unknown"),
            "Assessed " + str(report.get("summary", {}).get("files_assessed", 0)) +
            " files; findings: " + json.dumps(report.get("summary", {}).get("findings", {})),
        ]
        tokens = [x for x in re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", question.lower())
                  if x not in {"why", "this", "function", "does", "exist", "what", "which",
                               "dependencies", "require", "identify", "conflicting",
                               "implementations", "explain", "security", "implications",
                               "propose", "improved", "implementation", "compare",
                               "original", "source", "with", "translation"}]
        matches = [x for x in ranked if any(t in x["symbol"].lower() for t in tokens)]
        if not matches:
            matches = ranked[:5]
        if re.search(r"compare|conflict|duplicate|implementation|synth", question, re.I):
            lines.append("Ranked shared-symbol candidates:")
            for item in matches[:8]:
                lines.append("- " + item["symbol"] + " · heuristic rank " +
                             str(item["rank_score"]) + "/100 · " +
                             ", ".join(item["candidate_paths"]))
        if re.search(r"why|purpose|exist|function|dependencies", question, re.I):
            lines.append("Function-purpose/dependency evidence:")
            for item in matches[:6]:
                lines.append("- " + item["symbol"] + " is declared in " +
                             ", ".join(item["candidate_paths"]) +
                             ". Static assessment establishes overlap, not intended purpose, call graph, or runtime dependencies; Æị must inspect declarations, imports, call sites and tests.")
        findings = report.get("findings", [])
        relevant = [f for f in findings if not tokens or
                    any(t in (f.get("path", "") + " " + f.get("message", "")).lower() for t in tokens)]
        if not relevant:
            relevant = sorted(findings, key=lambda f: {"high": 0, "medium": 1, "low": 2}.get(f.get("severity"), 3))[:10]
        if re.search(r"finding|risk|security|assessment|quality", question, re.I):
            lines.append("Relevant static findings:")
            for f in relevant[:12]:
                lines.append("- [" + f.get("severity", "unknown").upper() + " " +
                             f.get("rule", "") + "] " + f.get("path", "") + ":" +
                             str(f.get("line", 0)) + " — " + f.get("message", ""))
        if report.get("source_comparisons"):
            lines.append("Local/GitHub source divergences: " +
                         str(len(report["source_comparisons"])) +
                         " paths have different SHA-256 snapshots; inspect each provenance pair before choosing a source.")
        lines.append("Next controlled step: create a REVIEW_REQUIRED proposal for a ranked symbol. No source write, Git mutation, or approval is implied.")
        return "\\n".join(lines)

    def proposal_history(self, limit: int = 50):
        with self.connect() as db:
            rows = db.execute("SELECT proposal_id,title,symbol,status,created_at,proposal_path "
                              "FROM quality_proposals ORDER BY created_at DESC LIMIT ?",
                              (max(1, min(int(limit), 200)),)).fetchall()
        return [dict(r) for r in rows]
