"""PONS-11 command-grant policy validator; does not execute processes or mint grants.

A trusted approval service must sign grants and provide the verifier/revocation
check. This module validates a narrow, unprivileged command capability only.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
import time
from typing import Callable, Sequence


MAX_GRANT_SECONDS = 11 * 60


@dataclass(frozen=True)
class CommandSpec:
    executable: str
    arguments: tuple[str, ...]


@dataclass(frozen=True)
class PONS11Grant:
    grant_id: str
    actor: str
    approval_ref: str
    issued_at: int
    expires_at: int
    commands: tuple[CommandSpec, ...]
    working_directories: tuple[str, ...]
    human_approved: bool
    revoked: bool
    root: bool
    deployment: bool
    may_modify_main: bool
    signature: str


@dataclass(frozen=True)
class GrantDecision:
    allowed: bool
    reason: str


def _safe_absolute_directory(path: str) -> bool:
    if not isinstance(path, str) or not path.startswith("/") or "\x00" in path:
        return False
    parsed = PurePosixPath(path)
    return ".." not in parsed.parts and str(parsed) == path.rstrip("/") or path == "/"


def validate_grant(
    grant: PONS11Grant | None,
    *,
    requested_executable: str,
    requested_arguments: Sequence[str],
    working_directory: str,
    trusted_executables: Sequence[str],
    trusted_working_directories: Sequence[str],
    signature_verifier: Callable[[PONS11Grant], bool],
    now: int | None = None,
) -> GrantDecision:
    """Validate one exact invocation against an authentic, time-limited grant."""
    if grant is None:
        return GrantDecision(False, "grant_missing")
    if not callable(signature_verifier):
        return GrantDecision(False, "trusted_verifier_required")
    if not grant.grant_id or not grant.actor or not grant.approval_ref:
        return GrantDecision(False, "grant_audit_identity_missing")
    if not grant.human_approved:
        return GrantDecision(False, "human_approval_missing")
    if grant.revoked:
        return GrantDecision(False, "grant_revoked")
    if grant.root:
        return GrantDecision(False, "root_privilege_prohibited")
    if grant.deployment:
        return GrantDecision(False, "deployment_prohibited")
    if grant.may_modify_main:
        return GrantDecision(False, "main_modification_prohibited")
    current = int(time.time()) if now is None else now
    if grant.expires_at <= current:
        return GrantDecision(False, "grant_expired")
    if grant.issued_at > current or grant.expires_at <= grant.issued_at:
        return GrantDecision(False, "grant_time_invalid")
    if grant.expires_at - grant.issued_at > MAX_GRANT_SECONDS:
        return GrantDecision(False, "grant_duration_exceeds_11_minutes")
    if not grant.commands or not grant.working_directories:
        return GrantDecision(False, "grant_scope_empty")
    if requested_executable not in trusted_executables:
        return GrantDecision(False, "executable_not_trusted")
    if not requested_executable.startswith("/") or "\x00" in requested_executable:
        return GrantDecision(False, "executable_path_invalid")
    invocation = CommandSpec(requested_executable, tuple(requested_arguments))
    if invocation not in grant.commands:
        return GrantDecision(False, "command_or_arguments_not_allowlisted")
    if not _safe_absolute_directory(working_directory):
        return GrantDecision(False, "working_directory_invalid")
    if working_directory not in grant.working_directories:
        return GrantDecision(False, "working_directory_out_of_scope")
    if working_directory not in trusted_working_directories:
        return GrantDecision(False, "working_directory_not_trusted")
    try:
        verified = bool(signature_verifier(grant))
    except Exception:
        verified = False
    if not verified:
        return GrantDecision(False, "signature_or_revocation_verification_failed")
    return GrantDecision(True, "pons11_authorized_exact_invocation")


def audit_decision(audit_sink: Callable[[dict], None], grant: PONS11Grant | None,
                   decision: GrantDecision, executable: str,
                   arguments: Sequence[str], working_directory: str) -> None:
    """Send a decision record to a host-provisioned append-only audit sink."""
    if not callable(audit_sink):
        raise TypeError("trusted append-only audit sink required")
    audit_sink({
        "event": "pons11.command_authorization",
        "grant_id": grant.grant_id if grant else None,
        "approval_ref": grant.approval_ref if grant else None,
        "allowed": decision.allowed,
        "reason": decision.reason,
        "executable": executable,
        "arguments": list(arguments),
        "working_directory": working_directory,
    })
