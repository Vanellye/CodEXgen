"""Read-only TACS collection, deterministic metadata serialization, and signature verification.

This module never creates, updates, deletes, or moves Git refs. It does not export to
removable media. Git is invoked with argument arrays (never a shell) and read-only
subcommands only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

SCHEMA_VERSION = 1
COLLECTOR_VERSION = "tacs-readonly/1.0"
TOKEN_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,63}$")


class TacsError(ValueError):
    """Invalid TACS input or an unverifiable repository state."""


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize JSON deterministically using NFC strings and stable key ordering."""
    def normalize(item: Any) -> Any:
        if isinstance(item, str):
            return unicodedata.normalize("NFC", item)
        if isinstance(item, list):
            return [normalize(v) for v in item]
        if isinstance(item, tuple):
            return [normalize(v) for v in item]
        if isinstance(item, dict):
            if not all(isinstance(k, str) for k in item):
                raise TacsError("JSON object keys must be strings")
            return {unicodedata.normalize("NFC", k): normalize(v) for k, v in item.items()}
        if isinstance(item, float):
            raise TacsError("floating-point values are not allowed; use integer or rational fields")
        if item is None or isinstance(item, (bool, int)):
            return item
        raise TacsError("unsupported JSON value: " + type(item).__name__)

    normalized = normalize(value)
    try:
        rendered = json.dumps(
            normalized, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise TacsError(str(exc)) from exc
    return (rendered + "\n").encode("utf-8")


def _git(repo: Path, *args: str) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="strict",
        )
    except FileNotFoundError as exc:
        raise TacsError("git executable was not found") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip()
        raise TacsError("git " + " ".join(args) + " failed: " + detail) from exc
    return proc.stdout


def _safe_remote_identity(remote: str) -> str:
    remote = remote.strip()
    # SCP-style remotes such as git@github.com:owner/repo.git.
    match = re.match(r"^(?:[^@/]+@)?([^:/]+):(.+)$", remote)
    if match and "://" not in remote:
        host, path = match.groups()
        return "https://" + host.lower() + "/" + (path[:-4] if path.endswith(".git") else path)
    parsed = urlsplit(remote)
    if parsed.scheme and parsed.hostname:
        path = parsed.path.rstrip("/")
        if path.endswith(".git"):
            path = path[:-4]
        # Drop userinfo, query, and fragment so credentials never enter the manifest.
        return urlunsplit((parsed.scheme.lower(), parsed.hostname.lower(), path, "", ""))
    raise TacsError("origin remote is not a recognized URL; refusing to serialize it")


def _repository_identity(repo: Path) -> dict[str, str]:
    try:
        remote = _git(repo, "remote", "get-url", "origin").strip()
    except TacsError:
        remote = ""
    if remote:
        return {"kind": "remote", "url": _safe_remote_identity(remote)}
    root = Path(_git(repo, "rev-parse", "--show-toplevel").strip())
    return {"kind": "local", "name": root.name}


def _parse_annotated_tag(repo: Path, tag_object_id: str) -> dict[str, Any]:
    raw = _git(repo, "cat-file", "-p", tag_object_id)
    header, separator, message = raw.partition("\n\n")
    if not separator:
        raise TacsError("annotated tag object has no header/message separator: " + tag_object_id)
    fields: dict[str, str] = {}
    for line in header.splitlines():
        key, sep, value = line.partition(" ")
        if sep and key in {"object", "type", "tag", "tagger"}:
            fields[key] = value
    required = {"object", "type", "tag"}
    if not required.issubset(fields):
        raise TacsError("annotated tag object is missing required headers: " + tag_object_id)
    signature_present = (
        "-----BEGIN PGP SIGNATURE-----" in message
        or "-----BEGIN SSH SIGNATURE-----" in message
    )
    return {
        "tag_object_target": fields["object"],
        "declared_target_type": fields["type"],
        "embedded_tag_name": fields["tag"],
        "tagger": fields.get("tagger"),
        "message": message.rstrip("\n"),
        "signature_present": signature_present,
    }


def collect_tags(repository: str | os.PathLike[str]) -> dict[str, Any]:
    """Collect all refs/tags without changing refs, index, worktree, or repository config."""
    repo = Path(repository).expanduser().resolve()
    try:
        _git(repo, "rev-parse", "--git-dir")
    except TacsError as exc:
        raise TacsError("not a Git repository: " + str(repo)) from exc
    identity = _repository_identity(repo)
    listing = _git(
        repo, "for-each-ref",
        "--format=%(refname)%09%(objectname)%09%(objecttype)",
        "refs/tags",
    )
    records: list[dict[str, Any]] = []
    for line in listing.splitlines():
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            raise TacsError("unexpected for-each-ref output; refusing partial collection")
        refname, tag_object_id, object_type = parts
        if not refname.startswith("refs/tags/"):
            raise TacsError("unexpected non-tag ref in tag enumeration")
        try:
            target_id = _git(repo, "rev-parse", refname + "^{}").strip()
        except TacsError as exc:
            raise TacsError("cannot peel tag " + refname + ": " + str(exc)) from exc
        target_type = _git(repo, "cat-file", "-t", target_id).strip()
        if object_type == "tag":
            annotation = _parse_annotated_tag(repo, tag_object_id)
            direct_target_type = _git(repo, "cat-file", "-t", annotation["tag_object_target"]).strip()
            if direct_target_type != annotation["declared_target_type"]:
                raise TacsError("annotated tag target type mismatch: " + refname)
            kind = "annotated"
        else:
            annotation = None
            kind = "lightweight"
            if tag_object_id != target_id:
                raise TacsError("lightweight tag unexpectedly resolves to a different object")
        record: dict[str, Any] = {
            "ref": refname,
            "kind": kind,
            "tag_object_id": tag_object_id,
            "direct_target_object_id": (
                annotation["tag_object_target"] if annotation else tag_object_id
            ),
            "target_object_id": target_id,
            "target_object_type": target_type,
            "annotation": annotation,
        }
        record["record_sha256"] = hashlib.sha256(canonical_json_bytes(record)).hexdigest()
        records.append(record)
    records.sort(key=lambda item: item["ref"])
    return {
        "schema_version": SCHEMA_VERSION,
        "collector": COLLECTOR_VERSION,
        "repository": identity,
        "tags": records,
    }


def validate_language_cadence(value: Any) -> dict[str, Any]:
    """Validate and normalize the versioned invented-language/cadence document."""
    if not isinstance(value, dict) or value.get("schema_version") != SCHEMA_VERSION:
        raise TacsError("metadata schema_version must be integer 1")
    language = value.get("language")
    cadence = value.get("cadence")
    if not isinstance(language, dict) or language.get("schema_version") != SCHEMA_VERSION:
        raise TacsError("language.schema_version must be integer 1")
    if not isinstance(cadence, dict) or cadence.get("schema_version") != SCHEMA_VERSION:
        raise TacsError("cadence.schema_version must be integer 1")
    tokens = language.get("tokens")
    phases = cadence.get("phases")
    if not isinstance(tokens, list) or not isinstance(phases, list):
        raise TacsError("language.tokens and cadence.phases must be arrays")
    normalized_tokens = []
    seen: set[str] = set()
    required_token_fields = {"token_id", "glyph", "pronunciation", "gloss", "role"}
    for token in tokens:
        if not isinstance(token, dict) or set(token) != required_token_fields:
            raise TacsError("each token must contain exactly token_id, glyph, pronunciation, gloss, role")
        token_id = token["token_id"]
        if not isinstance(token_id, str) or not TOKEN_ID_RE.fullmatch(token_id):
            raise TacsError("token_id must be a stable ASCII identifier")
        if token_id in seen:
            raise TacsError("duplicate token_id: " + token_id)
        seen.add(token_id)
        for key in required_token_fields - {"token_id"}:
            if not isinstance(token[key], str) or not token[key].strip():
                raise TacsError("token field must be a non-empty string: " + key)
        normalized_tokens.append(token)
    normalized_tokens.sort(key=lambda item: item["token_id"])

    normalized_phases = []
    phase_indices: set[int] = set()
    for phase in phases:
        if not isinstance(phase, dict) or set(phase) != {"index", "token_ids", "beats"}:
            raise TacsError("each cadence phase must contain exactly index, token_ids, beats")
        index, token_ids, beats = phase["index"], phase["token_ids"], phase["beats"]
        if isinstance(index, bool) or not isinstance(index, int) or index < 0:
            raise TacsError("phase index must be a non-negative integer")
        if index in phase_indices:
            raise TacsError("duplicate cadence phase index")
        phase_indices.add(index)
        if isinstance(beats, bool) or not isinstance(beats, int) or beats < 0:
            raise TacsError("phase beats must be a non-negative integer")
        if not isinstance(token_ids, list) or any(not isinstance(t, str) or t not in seen for t in token_ids):
            raise TacsError("phase token_ids must refer to known language tokens")
        normalized_phases.append({"index": index, "token_ids": token_ids, "beats": beats})
    normalized_phases.sort(key=lambda item: item["index"])
    if normalized_phases and [p["index"] for p in normalized_phases] != list(range(len(normalized_phases))):
        raise TacsError("cadence phase indices must be contiguous from zero")

    tempo = cadence.get("tempo")
    if tempo is not None:
        if not isinstance(tempo, dict) or set(tempo) != {"numerator", "denominator", "unit"}:
            raise TacsError("tempo must be null or a rational {numerator, denominator, unit}")
        numerator, denominator = tempo["numerator"], tempo["denominator"]
        if (isinstance(numerator, bool) or not isinstance(numerator, int) or numerator <= 0
                or isinstance(denominator, bool) or not isinstance(denominator, int) or denominator <= 0
                or tempo["unit"] != "bpm"):
            raise TacsError("tempo requires positive integer numerator/denominator and unit 'bpm'")
    return {
        "schema_version": SCHEMA_VERSION,
        "language": {"schema_version": SCHEMA_VERSION, "tokens": normalized_tokens},
        "cadence": {"schema_version": SCHEMA_VERSION, "phases": normalized_phases, "tempo": tempo},
    }


def serialize_language_cadence(value: Any) -> tuple[bytes, str]:
    """Return canonical UTF-8 JSON bytes and their SHA-256 digest."""
    payload = canonical_json_bytes(validate_language_cadence(value))
    return payload, hashlib.sha256(payload).hexdigest()


def verify_ed25519_signature(
    manifest_path: str | os.PathLike[str],
    signature_path: str | os.PathLike[str],
    public_key_path: str | os.PathLike[str],
    openssl: str = "openssl",
) -> bool:
    """Verify an Ed25519 detached signature over the exact manifest bytes.

    Uses OpenSSL's public-key verification only. No private key is accepted or read.
    """
    manifest = Path(manifest_path)
    signature = Path(signature_path)
    public_key = Path(public_key_path)
    for path in (manifest, signature, public_key):
        if not path.is_file():
            raise TacsError("verification input is not a readable file: " + str(path))
    command = [
        openssl, "pkeyutl", "-verify", "-pubin", "-inkey", str(public_key),
        "-rawin", "-in", str(manifest), "-sigfile", str(signature),
    ]
    try:
        proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except FileNotFoundError as exc:
        raise TacsError("OpenSSL executable was not found") from exc
    if proc.returncode == 0:
        return True
    # A bad signature is a normal negative result; operational failures are errors.
    diagnostic = (proc.stderr + "\n" + proc.stdout).lower()
    if "verification failure" in diagnostic:
        return False
    raise TacsError("OpenSSL verification could not run: " + diagnostic.strip())


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tacs", description="Read-only TACS tools (USB export is not implemented).")
    sub = parser.add_subparsers(dest="command", required=True)
    collect_parser = sub.add_parser("collect", help="read and print Git tag provenance")
    collect_parser.add_argument("--repo", default=".")
    serialize_parser = sub.add_parser("serialize", help="validate and canonically serialize language/cadence JSON")
    serialize_parser.add_argument("--input", required=True)
    verify_parser = sub.add_parser("verify", help="verify an Ed25519 detached signature")
    verify_parser.add_argument("--manifest", required=True)
    verify_parser.add_argument("--signature", required=True)
    verify_parser.add_argument("--public-key", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "collect":
            sys.stdout.buffer.write(canonical_json_bytes(collect_tags(args.repo)))
        elif args.command == "serialize":
            source = json.loads(Path(args.input).read_text(encoding="utf-8"))
            payload, digest = serialize_language_cadence(source)
            sys.stdout.buffer.write(payload)
            print("sha256=" + digest, file=sys.stderr)
        elif args.command == "verify":
            valid = verify_ed25519_signature(args.manifest, args.signature, args.public_key)
            print("VALID" if valid else "INVALID")
            return 0 if valid else 1
    except (TacsError, OSError, json.JSONDecodeError) as exc:
        print("tacs: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
