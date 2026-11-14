"""ERIA Resonance and acquisition primitives.

Safe local-only primitives. Playback and inbox watching are not started at
import time. Callers must explicitly start playback from a user gesture and
must provide a verified approval grant before enabling automatic acquisition.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import struct
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MAX_PLAYBACK_VOLUME = 0.50
SUPPORTED_SUFFIXES = {".csv", ".json", ".txt"}


class ResonanceHold(PermissionError):
    """An operation is not approved or its input is not eligible."""


def load_config(repository: str | Path) -> dict[str, Any]:
    path = Path(repository).resolve(strict=True) / "storage" / "settings.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "eria.resonance-console/1.0":
        raise ResonanceHold("Unsupported resonance configuration schema.")
    if data.get("maximum_playback_volume_percent", 0) > 50:
        raise ResonanceHold("Playback ceiling exceeds the safe 50% limit.")
    return data


def synthesize_tone(frequency_hz: float, duration_seconds: float = 1.0,
                    volume_percent: float = 25.0, sample_rate: int = 44100) -> bytes:
    """Create a bounded mono PCM WAV for browser playback after user gesture."""
    if not math.isfinite(frequency_hz) or not 20 <= frequency_hz <= 20000:
        raise ValueError("Audible frequency must be between 20 and 20000 Hz.")
    if not math.isfinite(duration_seconds) or not 0.05 <= duration_seconds <= 10:
        raise ValueError("Duration must be between 0.05 and 10 seconds.")
    if not math.isfinite(volume_percent) or not 0 <= volume_percent <= 50:
        raise ValueError("Playback volume must be between 0 and 50 percent.")
    if sample_rate not in (22050, 44100, 48000):
        raise ValueError("Unsupported sample rate.")
    count = int(sample_rate * duration_seconds)
    peak = min(volume_percent / 100.0, MAX_PLAYBACK_VOLUME)
    frames = bytearray()
    for i in range(count):
        # 10 ms fade-in/out avoids clicks; output is peak-limited.
        fade = min(1.0, i / max(1, int(sample_rate * .01)),
                   (count - i - 1) / max(1, int(sample_rate * .01)))
        sample = int(32767 * peak * max(0.0, fade) *
                     math.sin(2 * math.pi * frequency_hz * i / sample_rate))
        frames.extend(struct.pack("<h", sample))
    from io import BytesIO
    output = BytesIO()
    with wave.open(output, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(bytes(frames))
    return output.getvalue()


def acquire_inbox(repository: str | Path, *, approval_grant: dict[str, Any] | None = None
                  ) -> dict[str, Any]:
    """Acquire eligible inbox files only when exact-scope approval is present.

    This is a single scan, not a background watcher. Repeated scans are
    idempotent by source SHA-256. Source files are never moved or modified.
    """
    root = Path(repository).resolve(strict=True)
    config = load_config(root)
    policy = config["automatic_capture"]
    expected = "storage/inbox/"
    if not policy.get("approval_required") or not policy.get("enabled"):
        raise ResonanceHold("Automatic acquisition is requested but disabled pending approval.")
    if not isinstance(approval_grant, dict) or not (
        approval_grant.get("capability") == "eria.acquire"
        and approval_grant.get("scope") == expected
        and approval_grant.get("approved") is True
        and isinstance(approval_grant.get("approval_reference"), str)
        and approval_grant["approval_reference"].strip()
    ):
        raise ResonanceHold("A verified, exact-scope acquisition approval is required.")

    inbox = root / "storage" / "inbox"
    records = root / "storage" / "acquisitions"
    for folder in (inbox, records):
        if folder.is_symlink():
            raise ResonanceHold("Inbox and acquisition directories cannot be symlinks.")
        folder.mkdir(parents=True, exist_ok=True)
        if root not in folder.resolve(strict=True).parents:
            raise ResonanceHold("Acquisition path escapes repository.")
    index_path = records / "index.jsonl"
    known: set[str] = set()
    if index_path.exists():
        for line in index_path.read_text(encoding="utf-8").splitlines():
            try:
                known.add(json.loads(line)["source_sha256"])
            except (ValueError, KeyError, TypeError):
                continue

    acquired, held, duplicates = [], [], []
    for path in sorted(inbox.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            held.append({"path": rel, "status": "HOLD", "reason": "unsupported format"})
            continue
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest in known:
            duplicates.append({"path": rel, "sha256": digest})
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            held.append({"path": rel, "status": "HOLD", "reason": "not valid UTF-8"})
            continue
        record = {
            "schema": "eria.acquisition/1.0",
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "source_path": rel,
            "source_sha256": digest,
            "source_size_bytes": len(raw),
            "content_utf8": text,
            "approval_reference": approval_grant["approval_reference"],
            "transformations": ["read-only inbox acquisition", "UTF-8 validation"],
            "authority": "NON_AUTHORITATIVE"
        }
        line = json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
        fd = os.open(index_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND |
                     getattr(os, "O_NOFOLLOW", 0), 0o600)
        with os.fdopen(fd, "a", encoding="utf-8") as stream:
            stream.write(line)
            stream.flush()
            os.fsync(stream.fileno())
        known.add(digest)
        acquired.append({"path": rel, "sha256": digest, "status": "acquired"})
    return {"status": "complete", "acquired": acquired, "duplicates": duplicates,
            "held": held, "source_files_modified": False,
            "authority": "NON_AUTHORITATIVE"}
