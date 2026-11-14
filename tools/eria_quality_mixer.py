#!/usr/bin/env python3
"""ERIA repository-wide quality assessor and safe synthesis planner.

This tool inventories source files, scores static evidence, records provenance,
and proposes (never silently applies) code combinations. It also mixes PCM WAV
tracks with explicit output paths. It does not execute fetched source code.
"""
from __future__ import annotations

import argparse
import array
import hashlib
import json
import math
import re
import struct
import subprocess
import wave
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SKIP = {".git", ".gradle", ".idea", ".venv", "venv", "__pycache__", "node_modules",
        "build", "dist", ".cache", ".pytest_cache", ".eria"}
TEXT = {".kt", ".kts", ".java", ".cpp", ".cc", ".c", ".h", ".hpp", ".py", ".sh",
        ".bash", ".html", ".htm", ".css", ".js", ".mjs", ".ts", ".tsx", ".jsx",
        ".json", ".yaml", ".yml", ".toml", ".ini", ".properties", ".md", ".txt",
        ".xml", ".gradle", ".sql", ".cmake", ".mk"}
AUDIO = {".wav"}
MAX_BYTES = 2 * 1024 * 1024
SECRET_NAME = re.compile(r"(^\.env($|\.)|secret|credential|token|password|private[_-]?key|\.pem$|\.p12$|\.jks$|id_rsa)", re.I)
SECRET_VALUE = re.compile(r"(?i)(api[_-]?key|access[_-]?token|password|client_secret)\s*[:=]\s*['\"]?[^\s'\"]{8,}")
RULES = [
    ("ERIA001", "high", re.compile(r"\b(?:eval|exec)\s*\("), "Dynamic code execution needs explicit review."),
    ("ERIA002", "high", re.compile(r"\bshell\s*=\s*True"), "Shell invocation can create command-injection risk."),
    ("ERIA003", "high", SECRET_VALUE, "Possible embedded credential; inspect securely and rotate if real."),
    ("ERIA004", "medium", re.compile(r"\bexcept\s*:\s*(?:pass)?"), "Bare exception handling can hide failures."),
    ("ERIA005", "low", re.compile(r"\b(?:TODO|FIXME|XXX)\b", re.I), "Unresolved engineering marker."),
    ("ERIA006", "medium", re.compile(r"\b(?:pickle\.loads|yaml\.load)\s*\("), "Deserialization of untrusted input needs review."),
]
DECL = re.compile(r"^\s*(?:async\s+)?(?:def|class|fun|interface|object|struct|enum|function)\s+([A-Za-z_][A-Za-z0-9_]*)", re.M)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(root: Path, *args: str) -> str:
    try:
        p = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                           text=True, timeout=8, check=True)
        return p.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def scan(root: Path) -> dict:
    root = root.resolve()
    head = git(root, "rev-parse", "HEAD")
    branch = git(root, "branch", "--show-current") or "detached/unknown"
    files, findings, hashes, symbols = [], [], defaultdict(list), defaultdict(list)
    skipped = 0
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if any(part in SKIP for part in p.relative_to(root).parts) or p.is_symlink():
            continue
        if SECRET_NAME.search(p.name) or p.suffix.lower() not in TEXT:
            skipped += 1
            continue
        try:
            if p.stat().st_size > MAX_BYTES:
                skipped += 1
                continue
            raw = p.read_bytes()
            if b"\0" in raw:
                skipped += 1
                continue
            source = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError):
            skipped += 1
            continue
        digest = sha256(raw)
        hashes[digest].append(rel)
        names = sorted(set(DECL.findall(source)))
        for name in names:
            symbols[name].append(rel)
        file_findings = []
        for rule_id, severity, pattern, message in RULES:
            for match in pattern.finditer(source):
                line = source.count("\n", 0, match.start()) + 1
                item = {"rule": rule_id, "severity": severity, "path": rel,
                        "line": line, "message": message}
                findings.append(item)
                file_findings.append(item)
        high = sum(x["severity"] == "high" for x in file_findings)
        medium = sum(x["severity"] == "medium" for x in file_findings)
        low = sum(x["severity"] == "low" for x in file_findings)
        score = max(0, 100 - high * 25 - medium * 10 - low * 2)
        files.append({"path": rel, "bytes": len(raw), "sha256": digest,
                      "language": p.suffix.lower(), "declared_symbols": names,
                      "finding_count": len(file_findings), "static_score": score})
    duplicates = [{"sha256": h, "paths": paths} for h, paths in hashes.items() if len(paths) > 1]
    mix = []
    for name, paths in sorted(symbols.items()):
        unique = sorted(set(paths))
        if len(unique) > 1:
            mix.append({"symbol": name, "candidate_paths": unique,
                        "action": "compare interfaces and tests; synthesize only after approval"})
    counts = {s: sum(x["severity"] == s for x in findings) for s in ("high", "medium", "low")}
    return {"schema": "eria-quality-report/v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "provenance": {"repository": str(root), "branch": branch, "head_commit": head,
                           "working_tree_status": git(root, "status", "--short")},
            "policy": {"mode": "read-only assessment; no source writes; no fetched code execution",
                       "score_note": "Heuristic static triage score, not a proof of correctness or security."},
            "summary": {"files_assessed": len(files), "skipped": skipped,
                        "findings": counts, "exact_duplicate_groups": len(duplicates),
                        "mix_candidates": len(mix)},
            "files": files, "findings": findings,
            "duplicates": duplicates, "mix_candidates": mix}


def mix_wav(inputs: list[Path], output: Path) -> dict:
    if len(inputs) < 2:
        raise ValueError("Audio mix requires at least two WAV input tracks.")
    tracks = []
    spec = None
    for path in inputs:
        with wave.open(str(path), "rb") as w:
            current = (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getcomptype())
            if current[1] != 2 or current[3] != "NONE":
                raise ValueError("Only uncompressed 16-bit PCM WAV files are supported.")
            if spec is None:
                spec = current
            elif current != spec:
                raise ValueError("All tracks must have matching channels, sample rate and PCM format.")
            frames = w.readframes(w.getnframes())
            values = array.array("h")
            values.frombytes(frames)
            if struct.pack("=H", 1) != struct.pack("<H", 1):
                values.byteswap()
            tracks.append(values)
    length = max(map(len, tracks))
    mixed = [0.0] * length
    gain = 1.0 / len(tracks)
    for track in tracks:
        for i, value in enumerate(track):
            mixed[i] += value * gain
    peak = max((abs(x) for x in mixed), default=0.0)
    scale = min(1.0, 32767.0 / peak) if peak else 1.0
    result = array.array("h", (max(-32768, min(32767, int(round(x * scale)))) for x in mixed))
    if struct.pack("=H", 1) != struct.pack("<H", 1):
        result.byteswap()
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as w:
        w.setnchannels(spec[0]); w.setsampwidth(2); w.setframerate(spec[2])
        w.writeframes(result.tobytes())
    return {"output": str(output.resolve()), "tracks": [str(x) for x in inputs],
            "sample_rate": spec[2], "channels": spec[0], "frames": len(result) // spec[0],
            "normalization": "peak-safe"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    a = sub.add_parser("assess", help="Assess the complete repository without executing source.")
    a.add_argument("root", nargs="?", default=".")
    a.add_argument("--output", default=".eria/quality/latest.json")
    m = sub.add_parser("mix-audio", help="Mix two or more matching 16-bit PCM WAV tracks.")
    m.add_argument("--output", required=True)
    m.add_argument("inputs", nargs="+")
    args = ap.parse_args()
    if args.command == "assess":
        report = scan(Path(args.root))
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"report": str(target), **report["summary"]}, indent=2))
    else:
        print(json.dumps(mix_wav([Path(x) for x in args.inputs], Path(args.output)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
