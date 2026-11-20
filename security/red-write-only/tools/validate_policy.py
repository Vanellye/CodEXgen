"""Pure policy checks for ERIA Red Write-Only Ethical Tools.

This module performs no filesystem access, network access, shell execution,
secret inspection, or mutation. It validates proposed output paths only.
"""
from pathlib import PurePosixPath

ALLOWED_PREFIXES = ("reports/", "evidence-manifests/", "proposals/")
ALLOWED_OPERATIONS = {
    "create_new_report",
    "create_new_evidence_manifest",
    "create_new_remediation_proposal",
}

def authorize_output(operation: str, path: str, *, exists: bool = False,
                     is_symlink: bool = False) -> tuple[bool, str]:
    if operation not in ALLOWED_OPERATIONS:
        return False, "operation_not_allowed"
    if not isinstance(path, str) or not path:
        return False, "invalid_path"
    if path.startswith("/") or path.startswith("~"):
        return False, "absolute_path_denied"
    if "\\" in path:
        return False, "backslash_path_denied"
    parts = path.split("/")
    if any(part in ("", ".", "..") for part in parts):
        return False, "unsafe_path_segment"
    if not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
        return False, "output_root_not_allowed"
    if is_symlink:
        return False, "symlink_target_denied"
    if exists:
        return False, "create_only_existing_target_denied"
    return True, "allow_new_scoped_artifact"
