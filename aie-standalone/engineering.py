"""Approval-gated repository engineering primitives for Æị.

No model/provider is called here. AI-generated content must arrive as a proposal
from a separately configured provider and pass through this approval boundary.
"""
from __future__ import annotations
import hashlib, json, os, secrets, subprocess, tempfile
from pathlib import Path, PurePosixPath

TEXT_SUFFIXES = {".py", ".c", ".h", ".cpp", ".hpp", ".kt", ".java", ".js", ".ts",
 ".html", ".css", ".json", ".yaml", ".yml", ".toml", ".md", ".sh", ".gradle", ".xml", ".txt"}
PROTECTED_PARTS = {".git", ".eria", ".aie", "node_modules", "build", ".gradle"}
MAX_FILE_BYTES = 1_000_000

class PolicyError(Exception):
    pass

def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True,
        capture_output=True, text=True).stdout.strip()

class EngineeringWorkspace:
    def __init__(self, repository: str, state_dir: str | None = None):
        self.root = Path(repository).resolve(strict=True)
        if not (self.root / ".git").exists():
            raise PolicyError("Repository root is not a Git worktree")
        self.state = Path(state_dir or Path.home() / ".eria" / "aie-approvals")
        self.state.mkdir(parents=True, exist_ok=True, mode=0o700)
        try: self.state.chmod(0o700)
        except OSError: pass

    def branch(self) -> str:
        return _git(self.root, "branch", "--show-current")

    def _path(self, relative: str) -> Path:
        posix = PurePosixPath(relative)
        if posix.is_absolute() or not relative or any(p in ("", ".", "..") for p in posix.parts):
            raise PolicyError("Path must be normalized and repository-relative")
        if any(p in PROTECTED_PARTS for p in posix.parts):
            raise PolicyError("Protected path")
        if posix.suffix.lower() not in TEXT_SUFFIXES:
            raise PolicyError("Only approved text-source files are accessible")
        target = self.root.joinpath(*posix.parts)
        parent = target.parent.resolve()
        if parent != self.root and self.root not in parent.parents:
            raise PolicyError("Path escapes repository")
        if target.is_symlink(): raise PolicyError("Symbolic links are denied")
        return target

    def list_tracked(self, prefix: str = "") -> list[str]:
        files = _git(self.root, "ls-files", "-z").split("\0")
        return [f for f in files if f and (not prefix or f.startswith(prefix))
          and PurePosixPath(f).suffix.lower() in TEXT_SUFFIXES
          and not any(p in PROTECTED_PARTS for p in PurePosixPath(f).parts)]

    def read(self, relative: str) -> dict:
        target = self._path(relative)
        if relative not in set(self.list_tracked()):
            raise PolicyError("Read is limited to tracked files")
        data = target.read_bytes()
        if len(data) > MAX_FILE_BYTES: raise PolicyError("File exceeds 1 MB limit")
        try: value = data.decode("utf-8")
        except UnicodeDecodeError as exc: raise PolicyError("File is not UTF-8") from exc
        return {"path": relative, "content": value,
                "sha256": hashlib.sha256(data).hexdigest(), "branch": self.branch()}

    def propose(self, relative: str, content: str, rationale: str) -> dict:
        if self.branch() in ("", "main", "master"):
            raise PolicyError("Writes require a non-main feature branch")
        target = self._path(relative)
        if relative not in set(self.list_tracked()):
            raise PolicyError("Only existing tracked files can be replaced")
        if not isinstance(content, str) or len(content.encode("utf-8")) > MAX_FILE_BYTES:
            raise PolicyError("Proposal must be UTF-8 text no larger than 1 MB")
        if not rationale.strip(): raise PolicyError("A rationale is required")
        proposal_id = secrets.token_urlsafe(18)
        record = {"id": proposal_id, "path": relative, "content": content,
          "rationale": rationale, "expected_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
          "branch": self.branch(), "status": "pending"}
        path = self.state / (proposal_id + ".json")
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream: json.dump(record, stream)
        return {k:v for k,v in record.items() if k != "content"}

    def approve(self, proposal_id: str, explicit_human_approval: bool) -> dict:
        if explicit_human_approval is not True:
            raise PolicyError("Explicit human approval is required")
        if not proposal_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in proposal_id):
            raise PolicyError("Invalid proposal ID")
        path = self.state / (proposal_id + ".json")
        if not path.is_file(): raise PolicyError("Unknown proposal")
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("status") != "pending": raise PolicyError("Proposal is not pending")
        if self.branch() in ("", "main", "master") or self.branch() != record["branch"]:
            raise PolicyError("Branch changed or protected branch selected")
        target = self._path(record["path"])
        if record["path"] not in set(self.list_tracked()): raise PolicyError("Target is no longer tracked")
        current = target.read_bytes()
        if hashlib.sha256(current).hexdigest() != record["expected_sha256"]:
            raise PolicyError("Target changed; create a fresh proposal")
        mode = target.stat().st_mode & 0o777
        fd, tmp = tempfile.mkstemp(prefix=".aie-", dir=str(target.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
                stream.write(record["content"]); stream.flush(); os.fsync(stream.fileno())
            os.chmod(tmp, mode); os.replace(tmp, target)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
        record["status"] = "applied"
        record["applied_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        path.write_text(json.dumps(record), encoding="utf-8"); os.chmod(path, 0o600)
        return {"id": proposal_id, "path": record["path"], "status": "applied",
          "branch": record["branch"], "sha256": record["applied_sha256"],
          "note": "No Git commit or push was made; review and commit separately."}
