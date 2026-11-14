#!/usr/bin/env python3
"""ERIA Repository Conversation Engine: read-only Git and text inspector."""
import argparse, json, re, subprocess, sys
from pathlib import Path

from eria_oprozal import OprozalAdvisor

VERSION = "1.2"
MAX_BYTES = 1_000_000
MAX_HITS = 30
SKIP_DIRS = {".git", ".gradle", ".idea", "node_modules", "__pycache__", ".venv", "venv", "build", "dist"}
SECRET_NAME = re.compile(r"(secret|credential|token|password|private[_-]?key|\.env)", re.I)
SECRET_VALUE = re.compile(r"(?i)(api[_-]?key|access[_-]?token|password|client_secret)\s*[:=]\s*['\"]?([A-Za-z0-9_\-./+=]{8,})")


class RepoError(Exception):
    pass


def redact(text):
    return SECRET_VALUE.sub(lambda m: m.group(1) + "=[REDACTED]", text)


class Repository:
    def __init__(self, root):
        self.root = Path(root).resolve()
        p = subprocess.run(
            ["git", "-C", str(self.root), "rev-parse", "--show-toplevel"],
            text=True, capture_output=True
        )
        if p.returncode:
            raise RepoError("Selected directory is not inside a Git working tree.")
        self.root = Path(p.stdout.strip()).resolve()

    def git(self, *args):
        allowed = {"status", "branch", "log", "ls-files", "remote", "tag", "rev-parse"}
        if not args or args[0] not in allowed:
            raise RepoError("Git operation is not on the read-only allowlist.")
        p = subprocess.run(
            ["git", "-C", str(self.root), *args], text=True, capture_output=True
        )
        if p.returncode and p.stderr:
            raise RepoError(p.stderr.strip())
        return p.stdout

    def files(self):
        raw = self.git("ls-files", "--cached", "--others", "--exclude-standard", "-z")
        return sorted(x for x in raw.split("\0") if x)

    def show(self, rel):
        p = (self.root / rel).resolve()
        if self.root not in p.parents:
            raise RepoError("Requested path escapes repository root.")
        if not p.is_file():
            raise RepoError("Not a regular file.")
        if p.stat().st_size > MAX_BYTES:
            raise RepoError("File exceeds 1 MB inspection limit.")
        data = p.read_bytes()
        if b"\0" in data[:8192]:
            raise RepoError("Binary file: text inspection skipped.")
        return redact(data.decode("utf-8", errors="replace"))

    def search(self, query):
        terms = [x.lower() for x in re.findall(r"[A-Za-z0-9_.-]+", query) if len(x) > 1]
        hits = []
        for rel in self.files():
            p = self.root / rel
            if any(part in SKIP_DIRS for part in p.parts) or SECRET_NAME.search(p.name):
                continue
            try:
                if not p.is_file() or p.stat().st_size > MAX_BYTES:
                    continue
                data = p.read_bytes()
                if b"\0" in data[:8192]:
                    continue
                for n, line in enumerate(data.decode("utf-8", errors="replace").splitlines(), 1):
                    safe = redact(line).strip()
                    if safe and any(t in safe.lower() for t in terms):
                        hits.append((rel, n, safe[:240]))
                        if len(hits) >= MAX_HITS:
                            return hits
            except OSError:
                continue
        return hits


def fmt(path):
    return {
        ".py": "Python", ".sh": "Bash", ".kt": "Kotlin", ".java": "Java",
        ".c": "C", ".h": "C/C++ header", ".cpp": "C++", ".ptn": "Pantheon draft/spec",
        ".json": "JSON", ".yaml": "YAML", ".yml": "YAML", ".toml": "TOML",
        ".xml": "XML", ".gradle": "Gradle", ".kts": "Kotlin DSL", ".md": "Markdown",
        ".html": "HTML", ".js": "JavaScript", ".ts": "TypeScript", ".wav": "WAV audio",
        ".mp3": "MP3 audio", ".fa": "FASTA", ".fasta": "FASTA", ".csv": "CSV",
    }.get(Path(path).suffix.lower(), "Other")


class Conversation:
    def __init__(self, repo):
        self.r = repo
        self.oprozal = OprozalAdvisor()
        self.last_oprozal_advice = None
        # Optional adapter keeps older checkouts usable if integration files are absent.
        try:
            from eria_pantheon.interface import ERIAPantheonInterface
            self.integration = ERIAPantheonInterface(repo)
        except ImportError:
            self.integration = None

    def ask(self, q):
        """Answer through the existing router, then attach a deficiency reaction when warranted."""
        self.last_oprozal_advice = None
        answer = self._ask_without_oprozal(q)
        try:
            revision = self.r.git("rev-parse", "HEAD").strip() or "unknown"
        except (RepoError, OSError):
            revision = "unknown"
        advice = self.oprozal.assess(q, source_revision=revision)
        if advice is not None:
            self.last_oprozal_advice = advice
            answer += self.oprozal.render(advice)
        return answer

    def _ask_without_oprozal(self, q):
        low = q.lower().strip()
        out = [f"ERIA Repository Conversation Engine {VERSION}", f"Repository: {self.r.root}"]
        try:
            if low.startswith(("integration.", "bridge.", "pons.", "code.bypass ", "repository.ask ")):
                if self.integration is None:
                    out.append("Integration unavailable: eria_pantheon package is missing.")
                else:
                    return self.integration.handle(q)
            elif "status" in low or "working tree" in low:
                out += ["Git status:", self.r.git("status", "--short", "--branch")]
            elif "branch" in low:
                out += ["Branches:", self.r.git("branch", "-a", "--no-color")]
            elif any(x in low for x in ("commit", "history", "log")):
                out += ["Commit history:", self.r.git(
                    "log", "--all", "-30", "--date=iso-strict",
                    "--pretty=format:%h%x09%ad%x09%an%x09%s"
                )]
            elif "remote" in low:
                out += [
                    "Remote names (URLs hidden to avoid credential disclosure):",
                    self.r.git("remote") or "(none)"
                ]
            elif "tag" in low:
                out += ["Tags:", self.r.git("tag", "--list", "--sort=-creatordate") or "(none)"]
            elif any(x in low for x in ("all files", "file list", "inventory", "formats", "file types")):
                files = self.r.files()
                counts = {}
                for f in files:
                    counts[fmt(f)] = counts.get(fmt(f), 0) + 1
                out += [
                    f"Files: {len(files)}",
                    json.dumps(counts, sort_keys=True),
                    "Paths:\n" + "\n".join(files[:250])
                ]
                if len(files) > 250:
                    out.append(f"{len(files) - 250} more paths omitted.")
            elif low.startswith("show "):
                out += ["File: " + q[5:].strip(), self.r.show(q[5:].strip())]
            else:
                hits = self.r.search(q)
                if hits:
                    out += ["Evidence matches:"] + [f"{p}:{n}: {s}" for p, n, s in hits]
                else:
                    out += [
                        "No text matches found. Ask about status, branches, commits, remotes, "
                        "tags, all files, show path/to/file, integration.status, or code.bypass."
                    ]
        except (RepoError, OSError) as e:
            out.append("Inspection note: " + str(e))
        return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Read-only ERIA repository conversation engine")
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("-q", "--question")
    a = ap.parse_args()
    try:
        chat = Conversation(Repository(a.repo))
    except RepoError as e:
        print("ERIA:", e, file=sys.stderr)
        return 2
    if a.question:
        print(chat.ask(a.question))
        return 0
    print(
        f"ERIA Repository Conversation Engine {VERSION}\n"
        f"Repository: {chat.r.root}\nRead-only. Type quit to exit."
    )
    while True:
        try:
            q = input("ERIA> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q.lower() in {"quit", "exit"}:
            break
        if q:
            print(chat.ask(q))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
