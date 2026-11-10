"""Read-only verification for signed Pantheon package bundles."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_VERSION = 1
MAX_MANIFEST_BYTES = 2 * 1024 * 1024
MAX_PUBLIC_KEY_BYTES = 64 * 1024
MAX_FILES = 1024
MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")


class PackageVerificationError(ValueError):
    """The package is malformed, altered, or not signed by the pinned key."""


def canonical_manifest_bytes(manifest: dict[str, Any]) -> bytes:
    try:
        rendered = json.dumps(
            manifest, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise PackageVerificationError(f"manifest is not canonical JSON data: {exc}") from exc
    return (rendered + "\n").encode("utf-8")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PackageVerificationError(f"duplicate manifest key: {key}")
        result[key] = value
    return result


def _safe_relative_path(value: Any) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise PackageVerificationError("file paths must be non-empty POSIX relative paths")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise PackageVerificationError(f"unsafe package path: {value}")
    if path.as_posix() != value:
        raise PackageVerificationError(f"non-canonical package path: {value}")
    return path


def _load_manifest(bundle: Path) -> tuple[dict[str, Any], bytes]:
    manifest_path = bundle / "manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise PackageVerificationError("manifest.json is missing or unsafe")
    try:
        if manifest_path.stat().st_size > MAX_MANIFEST_BYTES:
            raise PackageVerificationError("manifest.json exceeds the configured size limit")
        raw = manifest_path.read_bytes()
        manifest = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageVerificationError(f"cannot read manifest.json: {exc}") from exc
    if not isinstance(manifest, dict):
        raise PackageVerificationError("manifest root must be an object")
    if raw != canonical_manifest_bytes(manifest):
        raise PackageVerificationError("manifest.json is not in canonical serialization")
    return manifest, raw


def _validate_manifest(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    required = {"schema_version", "package_id", "version", "source", "files"}
    if set(manifest) != required:
        raise PackageVerificationError("manifest fields do not match package schema")
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != SCHEMA_VERSION:
        raise PackageVerificationError(f"schema_version must equal {SCHEMA_VERSION}")
    for field in ("package_id", "version"):
        if not isinstance(manifest[field], str) or not IDENTIFIER_RE.fullmatch(manifest[field]):
            raise PackageVerificationError(f"{field} must be a stable identifier")
    if not isinstance(manifest["source"], dict):
        raise PackageVerificationError("source provenance must be an object")
    source = manifest["source"]
    if set(source) != {"repository", "ref", "commit"}:
        raise PackageVerificationError("source provenance requires repository, ref, and commit")
    for field, value in source.items():
        if not isinstance(value, str) or not value.strip():
            raise PackageVerificationError(f"source.{field} must be non-empty text")
    if not re.fullmatch(r"[0-9a-f]{40,64}", source["commit"]):
        raise PackageVerificationError("source.commit must be a full Git object ID")
    files = manifest["files"]
    if not isinstance(files, list) or not files:
        raise PackageVerificationError("files must be a non-empty list")
    if len(files) > MAX_FILES:
        raise PackageVerificationError("file count exceeds the configured limit")
    seen: set[str] = set()
    paths: list[str] = []
    for index, item in enumerate(files):
        if not isinstance(item, dict) or set(item) != {"path", "size_bytes", "sha256"}:
            raise PackageVerificationError(f"files[{index}] has invalid fields")
        path = _safe_relative_path(item["path"]).as_posix()
        if path in seen:
            raise PackageVerificationError(f"duplicate package path: {path}")
        seen.add(path)
        paths.append(path)
        if type(item["size_bytes"]) is not int or item["size_bytes"] < 0:
            raise PackageVerificationError(f"files[{index}].size_bytes must be non-negative")
        if item["size_bytes"] > MAX_FILE_BYTES:
            raise PackageVerificationError(f"files[{index}] exceeds the per-file size limit")
        if not isinstance(item["sha256"], str) or not SHA256_RE.fullmatch(item["sha256"]):
            raise PackageVerificationError(f"files[{index}].sha256 must be lowercase SHA-256")
    if paths != sorted(paths):
        raise PackageVerificationError("files must be sorted by canonical path")
    return files


def _verify_signature(bundle: Path, public_key: Path) -> None:
    signature = bundle / "manifest.sig"
    manifest = bundle / "manifest.json"
    if not signature.is_file() or signature.is_symlink():
        raise PackageVerificationError("manifest.sig is missing or unsafe")
    command = [
        "openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(public_key),
        "-rawin", "-in", str(manifest), "-sigfile", str(signature),
    ]
    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PackageVerificationError(f"signature verifier could not run: {exc}") from exc
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace")[:300]
        raise PackageVerificationError(f"manifest signature verification failed: {detail}")


def verify_bundle(
    bundle_dir: str | Path,
    trusted_public_key_path: str | Path,
    expected_key_sha256: str,
) -> dict[str, Any]:
    """Verify a bundle against an externally pinned Ed25519 public-key digest.

    The function is read-only: it never extracts, installs, executes, or adopts
    package contents. The trusted public key must be supplied out-of-band.
    """
    bundle = Path(bundle_dir).resolve(strict=True)
    key_input = Path(trusted_public_key_path)
    if key_input.is_symlink():
        raise PackageVerificationError("trusted public key must not be a symbolic link")
    key_path = key_input.resolve(strict=True)
    if not bundle.is_dir():
        raise PackageVerificationError("bundle path must be a directory")
    if not key_path.is_file():
        raise PackageVerificationError("trusted public key must be a regular file")
    if not isinstance(expected_key_sha256, str) or not SHA256_RE.fullmatch(expected_key_sha256):
        raise PackageVerificationError("expected key digest must be lowercase SHA-256")

    if key_path.stat().st_size > MAX_PUBLIC_KEY_BYTES:
        raise PackageVerificationError("trusted public key exceeds the configured size limit")
    key_digest = hashlib.sha256(key_path.read_bytes()).hexdigest()
    if key_digest != expected_key_sha256:
        raise PackageVerificationError("trusted public key digest does not match pinned digest")

    manifest, _ = _load_manifest(bundle)
    files = _validate_manifest(manifest)
    _verify_signature(bundle, key_path)

    expected_paths = {"manifest.json", "manifest.sig"}
    total_bytes = 0
    for item in files:
        relative = _safe_relative_path(item["path"])
        current = bundle
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                raise PackageVerificationError(f"symbolic link is not accepted: {relative.as_posix()}")
        target = current.resolve(strict=True)
        try:
            target.relative_to(bundle)
        except ValueError as exc:
            raise PackageVerificationError(f"package path escapes bundle: {relative.as_posix()}") from exc
        if not target.is_file():
            raise PackageVerificationError(f"package payload is not a regular file: {relative.as_posix()}")
        actual_size = target.stat().st_size
        if actual_size > MAX_FILE_BYTES:
            raise PackageVerificationError(f"payload exceeds the per-file size limit: {relative.as_posix()}")
        total_bytes += actual_size
        if total_bytes > MAX_TOTAL_BYTES:
            raise PackageVerificationError("package exceeds the total payload size limit")
        if actual_size != item["size_bytes"]:
            raise PackageVerificationError(f"size mismatch: {relative.as_posix()}")
        data = target.read_bytes()
        if len(data) != item["size_bytes"]:
            raise PackageVerificationError(f"size mismatch: {relative.as_posix()}")
        if hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise PackageVerificationError(f"SHA-256 mismatch: {relative.as_posix()}")
        expected_paths.add(relative.as_posix())

    actual_paths: set[str] = set()
    for root, directories, filenames in os.walk(bundle, followlinks=False):
        root_path = Path(root)
        for name in list(directories):
            path = root_path / name
            if path.is_symlink():
                raise PackageVerificationError(f"directory symlink is not accepted: {path.relative_to(bundle)}")
        for name in filenames:
            path = root_path / name
            if path.is_symlink():
                raise PackageVerificationError(f"file symlink is not accepted: {path.relative_to(bundle)}")
            actual_paths.add(path.relative_to(bundle).as_posix())
    if actual_paths != expected_paths:
        extras = sorted(actual_paths - expected_paths)
        missing = sorted(expected_paths - actual_paths)
        raise PackageVerificationError(f"bundle file inventory mismatch; extra={extras}, missing={missing}")

    return {
        "status": "verified",
        "package_id": manifest["package_id"],
        "version": manifest["version"],
        "source": manifest["source"],
        "file_count": len(files),
        "trusted_key_sha256": key_digest,
        "signature_valid": True,
        "contents_executed": False,
        "installed": False,
        "adoption_authorized": False,
    }
