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

try:
    from .eria_pantheon.pons import CapabilityGrant, Decision, Pons
except ImportError:  # Termux script execution with tools/ on sys.path
    from eria_pantheon.pons import CapabilityGrant, Decision, Pons


def _now():
    return datetime.now(timezone.utc).isoformat()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class PonsApprovalService:
    CAPABILITY = "repository.patch.prepare"

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
              CREATE UNIQUE INDEX IF NOT EXISTS approval_grants_one_per_request ON approval_grants(request_id);
              CREATE TABLE IF NOT EXISTS patch_approval_requests(patch_request_id TEXT PRIMARY KEY,parent_grant_id TEXT NOT NULL,patch_sha256 TEXT NOT NULL,patch_text TEXT NOT NULL,scope_json TEXT NOT NULL,created_at TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS patch_approval_grants(patch_grant_id TEXT PRIMARY KEY,patch_request_id TEXT NOT NULL,parent_grant_id TEXT NOT NULL,capability TEXT NOT NULL,patch_sha256 TEXT NOT NULL,scope_sha256 TEXT NOT NULL,scope_json TEXT NOT NULL,decision TEXT NOT NULL,approved_at TEXT NOT NULL,confirmation TEXT NOT NULL);
              CREATE UNIQUE INDEX IF NOT EXISTS patch_grants_one_per_request ON patch_approval_grants(patch_request_id);
              CREATE TRIGGER IF NOT EXISTS patch_requests_no_update BEFORE UPDATE ON patch_approval_requests BEGIN SELECT RAISE(ABORT,'PONS patch requests are append-only'); END;
              CREATE TRIGGER IF NOT EXISTS patch_requests_no_delete BEFORE DELETE ON patch_approval_requests BEGIN SELECT RAISE(ABORT,'PONS patch requests are append-only'); END;
              CREATE TRIGGER IF NOT EXISTS patch_grants_no_update BEFORE UPDATE ON patch_approval_grants BEGIN SELECT RAISE(ABORT,'PONS patch grants are append-only'); END;
              CREATE TRIGGER IF NOT EXISTS patch_grants_no_delete BEFORE DELETE ON patch_approval_grants BEGIN SELECT RAISE(ABORT,'PONS patch grants are append-only'); END;
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
            "operation": "authorize preparation of a proposed patch for review; applying any patch requires a second approval bound to the exact patch hash",
            "files": [{"path": p, "sha256": fingerprints[p]} for p in sorted(paths)],
            "limitations": [
                "No other files or paths are authorized",
                "No commit, push, merge, deployment, or database source-record mutation",
                "This grant authorizes patch preparation only; it does not authorize applying or writing any patch",
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

    PATCH_CAPABILITY = "repository.source.modify"

    def _approved_parent(self, grant_id):
        with self.connect() as db:
            row = db.execute("SELECT * FROM approval_grants WHERE grant_id=? AND decision='REVIEW_READY'", (grant_id,)).fetchone()
        if not row:
            raise ValueError("A valid parent PONS patch-preparation grant is required.")
        scope = json.loads(row["scope_json"])
        if row["capability"] != self.CAPABILITY or scope.get("capability") != self.CAPABILITY:
            raise ValueError("Parent grant does not authorize patch preparation.")
        return row, scope

    @staticmethod
    def _patch_paths(patch_text):
        if not isinstance(patch_text, str) or not patch_text.strip():
            raise ValueError("A non-empty unified diff is required.")
        if len(patch_text.encode("utf-8")) > 2 * 1024 * 1024:
            raise ValueError("Patch exceeds the 2 MiB approval limit.")
        if "GIT binary patch" in patch_text or "Binary files " in patch_text:
            raise ValueError("Binary patches are not eligible for this review gate.")
        paths = set()
        for line in patch_text.splitlines():
            if line.startswith(("--- ", "+++ ")):
                raw = line[4:].split("\t", 1)[0].strip()
                if raw == "/dev/null":
                    continue
                if raw.startswith(("a/", "b/")):
                    raw = raw[2:]
                candidate = Path(raw)
                if not raw or candidate.is_absolute() or ".." in candidate.parts or chr(92) in raw:
                    raise ValueError("Patch contains an unsafe target path.")
                paths.add(candidate.as_posix())
        if not paths:
            raise ValueError("Patch contains no verifiable unified-diff file headers.")
        return sorted(paths)

    def create_patch_request(self, parent_grant_id, patch_text):
        parent, parent_scope = self._approved_parent(parent_grant_id)
        paths = self._patch_paths(patch_text)
        allowed = {item["path"]: item["sha256"] for item in parent_scope["files"]}
        if not set(paths).issubset(allowed):
            raise ValueError("Patch expands beyond the parent grant's exact file scope.")
        self._verify_live_sources(parent_scope)
        patch_digest = hashlib.sha256(patch_text.encode("utf-8")).hexdigest()
        patch_scope = {
            "capability": self.PATCH_CAPABILITY, "parent_grant_id": parent_grant_id,
            "parent_scope_sha256": parent["scope_sha256"], "repository": str(self.root),
            "branch": parent_scope["branch"], "head_commit": parent_scope["head_commit"],
            "patch_sha256": patch_digest, "patch_paths": paths,
            "source_fingerprints": [{"path": path, "sha256": allowed[path]} for path in paths],
            "operation": "authorize only this exact patch hash; no executor or write is enabled",
            "limitations": ["Patch bytes are immutable after request creation",
                "No paths outside the parent grant are authorized",
                "No commit, push, merge, deployment, or source database mutation",
                "A source-writing executor remains disabled"],
        }
        encoded = _canonical(patch_scope)
        scope_digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        request_id, created = str(uuid.uuid4()), _now()
        with self.connect() as db:
            db.execute("INSERT INTO patch_approval_requests VALUES(?,?,?,?,?,?)",
                       (request_id, parent_grant_id, patch_digest, patch_text, encoded, created))
        return {"patch_request_id": request_id, "parent_grant_id": parent_grant_id,
            "patch_sha256": patch_digest, "patch_paths": paths, "scope": patch_scope,
            "scope_sha256": scope_digest,
            "confirmation_phrase": "AUTHORIZE PATCH " + patch_digest[:12], "status": "HOLD"}

    def approve_patch(self, patch_request_id, patch_sha256, confirmation):
        with self.connect() as db:
            row = db.execute("SELECT * FROM patch_approval_requests WHERE patch_request_id=?", (patch_request_id,)).fetchone()
            prior = db.execute("SELECT patch_grant_id FROM patch_approval_grants WHERE patch_request_id=?", (patch_request_id,)).fetchone()
        if not row:
            raise ValueError("PONS patch request not found.")
        if prior:
            raise ValueError("This exact patch request already has a grant.")
        actual = hashlib.sha256(row["patch_text"].encode("utf-8")).hexdigest()
        if actual != row["patch_sha256"] or patch_sha256 != actual:
            raise ValueError("Patch hash mismatch; PONS remains HOLD.")
        expected = "AUTHORIZE PATCH " + actual[:12]
        if not isinstance(confirmation, str) or confirmation.strip() != expected:
            raise ValueError("Exact patch-hash confirmation phrase does not match.")
        parent, parent_scope = self._approved_parent(row["parent_grant_id"])
        patch_scope = json.loads(row["scope_json"])
        if patch_scope.get("patch_sha256") != actual or patch_scope.get("parent_scope_sha256") != parent["scope_sha256"]:
            raise ValueError("Patch or parent grant scope mismatch; PONS remains HOLD.")
        self._verify_live_sources(parent_scope)
        scope_digest = hashlib.sha256(_canonical(patch_scope).encode("utf-8")).hexdigest()
        grant = CapabilityGrant(self.PATCH_CAPABILITY, scope_digest, scope_digest,
                                patch_request_id, verified_by_adapter=True)
        decision = Pons.authorize_source_write(grant, self.PATCH_CAPABILITY, scope_digest)
        if decision is not Decision.REVIEW_READY:
            raise ValueError("PONS denied patch authorization; request remains HOLD.")
        patch_grant_id, approved_at = str(uuid.uuid4()), _now()
        with self.connect() as db:
            db.execute("INSERT INTO patch_approval_grants VALUES(?,?,?,?,?,?,?,?,?,?)",
                (patch_grant_id, patch_request_id, row["parent_grant_id"], self.PATCH_CAPABILITY,
                 actual, scope_digest, row["scope_json"], decision.value, approved_at, expected))
        return {"patch_grant_id": patch_grant_id, "patch_request_id": patch_request_id,
            "parent_grant_id": row["parent_grant_id"], "decision": decision.value,
            "patch_sha256": actual, "scope_sha256": scope_digest,
            "source_modified": False, "executor_enabled": False}

    def verify_patch_grant(self, patch_grant_id, patch_text):
        with self.connect() as db:
            row = db.execute("SELECT * FROM patch_approval_grants WHERE patch_grant_id=?", (patch_grant_id,)).fetchone()
        if not row or row["decision"] != "REVIEW_READY":
            raise ValueError("No approved PONS patch grant; source write must HOLD.")
        actual = hashlib.sha256(patch_text.encode("utf-8")).hexdigest()
        if actual != row["patch_sha256"]:
            raise ValueError("Patch bytes differ from the human-approved hash; source write must HOLD.")
        parent, parent_scope = self._approved_parent(row["parent_grant_id"])
        self._verify_live_sources(parent_scope)
        patch_scope = json.loads(row["scope_json"])
        digest = hashlib.sha256(_canonical(patch_scope).encode("utf-8")).hexdigest()
        if digest != row["scope_sha256"] or patch_scope.get("patch_sha256") != actual:
            raise ValueError("Patch authorization scope verification failed; source write must HOLD.")
        return {"authorized": True, "patch_sha256": actual, "scope_sha256": digest,
            "paths": patch_scope["patch_paths"], "executor_enabled": False,
            "note": "Gate verified only. No patch was applied and no source file was written."}

    def history(self, limit=100):
        with self.connect() as db:
            requests = db.execute(
                "SELECT r.request_id,r.proposal_id,r.capability,r.scope_sha256,r.status,r.created_at, "
                "CASE WHEN EXISTS(SELECT 1 FROM approval_grants g WHERE g.request_id=r.request_id) "
                "THEN 'REVIEW_READY' ELSE r.status END AS effective_status "
                "FROM approval_requests r ORDER BY r.created_at DESC LIMIT ?",
                (max(1, min(int(limit), 200)),),
            ).fetchall()
            grants = db.execute(
                "SELECT grant_id,request_id,proposal_id,capability,scope_sha256,decision,approved_at "
                "FROM approval_grants ORDER BY approved_at DESC LIMIT ?",
                (max(1, min(int(limit), 200)),),
            ).fetchall()
            patch_requests = db.execute(
                "SELECT patch_request_id,parent_grant_id,patch_sha256,created_at FROM patch_approval_requests ORDER BY created_at DESC LIMIT ?",
                (max(1, min(int(limit), 200)),),
            ).fetchall()
            patch_grants = db.execute(
                "SELECT patch_grant_id,patch_request_id,parent_grant_id,capability,patch_sha256,scope_sha256,decision,approved_at FROM patch_approval_grants ORDER BY approved_at DESC LIMIT ?",
                (max(1, min(int(limit), 200)),),
            ).fetchall()
        return {"requests": [dict(x) for x in requests],
                "grants": [dict(x) for x in grants],
                "patch_requests": [dict(x) for x in patch_requests],
                "patch_grants": [dict(x) for x in patch_grants]}
