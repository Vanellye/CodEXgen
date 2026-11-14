#!/usr/bin/env python3
"""Exact-scope, human-confirmed PONS approval for ERIA quality proposals.

This module records one-time authorization grants only. It does not modify
repository files, invoke Git writes, or execute proposed patches.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

from eria_pantheon.pons import CapabilityGrant, Decision, Pons


def _now():
    return datetime.now(timezone.utc).isoformat()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class PonsApprovalService:
    CAPABILITY = "repository.source.modify"

    def __init__(self, quality, repository_root: Path):
        self.quality = quality
        self.root = Path(repository_root).resolve()
        self.database = self.quality.home / "pons_approvals.sqlite3"
        with self.connect() as db:
            db.executescript("""
              CREATE TABLE IF NOT EXISTS approval_requests(
                request_id TEXT PRIMARY KEY, proposal_id TEXT NOT NULL,
                capability TEXT NOT NULL, scope_json TEXT NOT NULL,
                scope_sha256 TEXT NOT NULL, status TEXT NOT NULL,
                created_at TEXT NOT NULL
              );
              CREATE TABLE IF NOT EXISTS approval_grants(
                grant_id TEXT PRIMARY KEY, request_id TEXT NOT NULL,
                proposal_id TEXT NOT NULL, capability TEXT NOT NULL,
                scope_sha256 TEXT NOT NULL, scope_json TEXT NOT NULL,
                decision TEXT NOT NULL, approved_at TEXT NOT NULL,
                confirmation TEXT NOT NULL
              );
              CREATE TRIGGER IF NOT EXISTS approval_requests_no_update
                BEFORE UPDATE ON approval_requests BEGIN
                  SELECT RAISE(ABORT,'PONS approval request history is append-only');
                END;
              CREATE TRIGGER IF NOT EXISTS approval_requests_no_delete
                BEFORE DELETE ON approval_requests BEGIN
                  SELECT RAISE(ABORT,'PONS approval request history is append-only');
                END;
              CREATE TRIGGER IF NOT EXISTS approval_grants_no_update
                BEFORE UPDATE ON approval_grants BEGIN
                  SELECT RAISE(ABORT,'PONS grants are append-only');
                END;
              CREATE TRIGGER IF NOT EXISTS approval_grants_no_delete
                BEFORE DELETE ON approval_grants BEGIN
                  SELECT RAISE(ABORT,'PONS grants are append-only');
                END;
            """)

    def connect(self):
        db = sqlite3.connect(str(self.database), timeout=15)
        db.row_factory = sqlite3.Row
        return db

    def _proposal(self, proposal_id):
        if not isinstance(proposal_id, str) or len(proposal_id) > 80:
            raise ValueError("A valid proposal ID is required.")
        with self.quality.connect() as db:
            row = db.execute(
                "SELECT proposal_path FROM quality_proposals WHERE proposal_id=?",
                (proposal_id,),
            ).fetchone()
        if not row:
            raise ValueError("Proposal not found.")
        path = Path(row["proposal_path"]).resolve()
        if self.quality.proposals not in path.parents or not path.is_file():
            raise ValueError("Proposal packet is unavailable.")
        return json.loads(path.read_text(encoding="utf-8"))

    def _scope(self, proposal):
        evidence = proposal.get("evidence", {})
        paths = proposal.get("paths", [])
        fingerprints = evidence.get("source_fingerprints", {})
        if not paths or set(paths) != set(fingerprints):
            raise ValueError("Proposal has incomplete source fingerprints.")
        if any(not isinstance(p, str) or not p or Path(p).is_absolute()
               or ".." in Path(p).parts for p in paths):
            raise ValueError("Proposal contains an unsafe source path.")
        if any(not isinstance(fingerprints[p], str) or len(fingerprints[p]) != 64
               for p in paths):
            raise ValueError("Proposal contains an invalid source fingerprint.")
        provenance = evidence.get("repository_provenance", {})
        scope = {
            "capability": self.CAPABILITY,
            "repository": str(self.root),
            "proposal_id": proposal["proposal_id"],
            "report_id": evidence.get("report_id", ""),
            "report_sha256": evidence.get("report_sha256", ""),
            "branch": provenance.get("branch", ""),
            "head_commit": provenance.get("head_commit", ""),
            "operation": "modify only the listed files under a separately reviewed patch",
            "files": [{"path": p, "sha256": fingerprints[p]} for p in sorted(paths)],
            "limitations": [
                "No other files or paths are authorized",
                "No commit, push, merge, deployment, or database source-record mutation",
                "This grant authorizes preparation/application of only a separately reviewed patch",
            ],
        }
        if not scope["branch"] or not scope["head_commit"] or not scope["report_sha256"]:
            raise ValueError("Proposal provenance is incomplete; PONS must HOLD.")
        return scope

    def create_request(self, proposal_id):
        proposal = self._proposal(proposal_id)
        scope = self._scope(proposal)
        encoded = _canonical(scope)
        digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        request_id = str(uuid.uuid4())
        created = _now()
        with self.connect() as db:
            db.execute(
                "INSERT INTO approval_requests VALUES(?,?,?,?,?,?,?)",
                (request_id, proposal_id, self.CAPABILITY, encoded, digest, "HOLD", created),
            )
        return {
            "request_id": request_id, "proposal_id": proposal_id,
            "capability": self.CAPABILITY, "scope": scope,
            "scope_sha256": digest, "confirmation_phrase": "APPROVE " + digest[:12],
            "status": "HOLD", "created_at": created,
        }

    def _verify_live_sources(self, scope):
        def git(*args):
            return subprocess.run(
                ["git", "-C", str(self.root), *args],
                check=True, capture_output=True, text=True, timeout=8,
            ).stdout.strip()
        try:
            branch = git("rev-parse", "--abbrev-ref", "HEAD")
            head = git("rev-parse", "HEAD")
        except (OSError, subprocess.SubprocessError) as exc:
            raise ValueError("Git provenance could not be verified; PONS remains HOLD.") from exc
        if branch != scope["branch"] or head != scope["head_commit"]:
            raise ValueError("Branch or HEAD changed since proposal creation; refresh and prepare a new proposal.")
        for item in scope["files"]:
            target = (self.root / item["path"]).resolve()
            if self.root not in target.parents or not target.is_file():
                raise ValueError("An approved source path is missing or escaped the repository.")
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            if digest != item["sha256"]:
                raise ValueError("Source fingerprint changed for " + item["path"] + "; PONS remains HOLD.")

    def approve(self, request_id, scope_sha256, confirmation):
        with self.connect() as db:
            row = db.execute(
                "SELECT * FROM approval_requests WHERE request_id=?",
                (request_id,),
            ).fetchone()
            prior = db.execute(
                "SELECT grant_id FROM approval_grants WHERE request_id=?",
                (request_id,),
            ).fetchone()
        if not row:
            raise ValueError("PONS request not found.")
        if prior:
            raise ValueError("This request already has a recorded approval grant.")
        if row["status"] != "HOLD" or scope_sha256 != row["scope_sha256"]:
            raise ValueError("Approval scope mismatch; PONS remains HOLD.")
        scope = json.loads(row["scope_json"])
        expected = "APPROVE " + row["scope_sha256"][:12]
        if not isinstance(confirmation, str) or confirmation.strip() != expected:
            raise ValueError("Exact-scope confirmation phrase does not match.")
        self._verify_live_sources(scope)
        grant = CapabilityGrant(
            capability=self.CAPABILITY,
            requested_scope=row["scope_sha256"],
            approved_scope=row["scope_sha256"],
            approval_reference=request_id,
            verified_by_adapter=True,
        )
        decision = Pons.authorize_source_write(
            grant, self.CAPABILITY, row["scope_sha256"]
        )
        if decision is not Decision.REVIEW_READY:
            raise ValueError("PONS denied the grant; request remains HOLD.")
        grant_id = str(uuid.uuid4())
        approved_at = _now()
        with self.connect() as db:
            db.execute(
                "INSERT INTO approval_grants VALUES(?,?,?,?,?,?,?,?,?)",
                (grant_id, request_id, row["proposal_id"], self.CAPABILITY,
                 row["scope_sha256"], row["scope_json"], decision.value,
                 approved_at, expected),
            )
        return {
            "grant_id": grant_id, "request_id": request_id,
            "proposal_id": row["proposal_id"], "decision": decision.value,
            "scope_sha256": row["scope_sha256"], "approved_at": approved_at,
            "source_modified": False,
            "note": "Exact-scope authorization recorded. No source file was modified or patch executed.",
        }

    def history(self, limit=100):
        with self.connect() as db:
            requests = db.execute(
                "SELECT request_id,proposal_id,capability,scope_sha256,status,created_at "
                "FROM approval_requests ORDER BY created_at DESC LIMIT ?",
                (max(1, min(int(limit), 200)),),
            ).fetchall()
            grants = db.execute(
                "SELECT grant_id,request_id,proposal_id,capability,scope_sha256,decision,approved_at "
                "FROM approval_grants ORDER BY approved_at DESC LIMIT ?",
                (max(1, min(int(limit), 200)),),
            ).fetchall()
        return {"requests": [dict(x) for x in requests],
                "grants": [dict(x) for x in grants]}
