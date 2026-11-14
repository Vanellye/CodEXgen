#!/usr/bin/env python3
"""Progress a proposed patch in a disposable snapshot and isolated test sandbox."""
from __future__ import annotations
import argparse, io, os, subprocess, sys, tarfile, tempfile
from pathlib import Path
from eria_os_sandbox import SandboxError, run as sandbox_run

class EvolutionHold(RuntimeError): pass

def git(root: Path, *args: str, check=True, text=True):
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                       text=text, stdin=subprocess.DEVNULL)
    if check and p.returncode:
        detail = (p.stderr or p.stdout)
        if isinstance(detail, bytes):
            detail = detail.decode("utf-8", "replace")
        raise EvolutionHold(str(detail).strip())
    return p

def snapshot(repo: Path, dest: Path):
    archive = git(repo, "archive", "--format=tar", "HEAD", text=False).stdout
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
        for m in tar.getmembers():
            name = Path(m.name)
            if name.is_absolute() or ".." in name.parts or not (m.isfile() or m.isdir()):
                raise EvolutionHold("Unsafe Git archive entry: " + m.name)
        tar.extractall(dest, filter="data")

def apply_patch(dest: Path, patch_file: Path):
    raw = patch_file.read_bytes()
    if len(raw) > 2*1024*1024: raise EvolutionHold("Patch exceeds 2 MiB.")
    for args in (["apply", "--check", "--whitespace=error"],
                 ["apply", "--whitespace=error"]):
        p = subprocess.run(["git", "-C", str(dest), *args], input=raw, capture_output=True)
        if p.returncode: raise EvolutionHold((p.stderr or p.stdout).decode("utf-8", "replace"))

def export_patch(candidate: Path, output: Path):
    p = git(candidate, "diff", "--binary", "HEAD", check=False, text=False)
    if p.returncode not in (0, 1):
        raise EvolutionHold(p.stderr.decode("utf-8", "replace"))
    if not p.stdout: raise EvolutionHold("No code progression was produced.")
    output.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(output, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f: f.write(p.stdout)

def progress(repo: Path, patch: Path, output: Path, timeout: int):
    repo, patch, output = repo.resolve(), patch.resolve(), output.resolve()
    if not (repo/".git").exists(): raise EvolutionHold("Repository must be a Git worktree.")
    if not patch.is_file(): raise EvolutionHold("Proposed patch not found.")
    if output.exists(): raise EvolutionHold("Candidate output exists; refusing overwrite.")
    if git(repo, "status", "--porcelain").stdout.strip():
        raise EvolutionHold("Source worktree must be clean.")
    with tempfile.TemporaryDirectory(prefix="eria-evolution-") as td:
        work = Path(td)/"workspace"; work.mkdir()
        snapshot(repo, work)
        git(work, "init", "-q")
        git(work, "add", "-A")
        git(work, "-c", "user.name=ERIA Sandbox", "-c",
            "user.email=eria-sandbox@localhost", "commit", "-q", "-m", "sandbox baseline")
        apply_patch(work, patch)
        code = sandbox_run(work, [sys.executable, "-m", "unittest",
                                  "discover", "-s", "tests", "-v"], timeout)
        if code: raise EvolutionHold(f"Sandbox tests failed: exit {code}")
        export_patch(work, output)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", type=Path, default=Path("."))
    p.add_argument("--patch", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--timeout", type=int, default=300)
    a = p.parse_args()
    try: progress(a.repo, a.patch, a.output, a.timeout)
    except (EvolutionHold, SandboxError, OSError, subprocess.SubprocessError) as e:
        print("ERIA EVOLUTION HOLD:", e, file=sys.stderr); return 2
    print("CANDIDATE_PATCH="+str(a.output.resolve()))
    print("SANDBOX_TESTS=PASSED")
    print("SOURCE_REPOSITORY_MODIFIED=false")
    print("LOCAL_COMMIT_CREATED=false")
    print("REMOTE_PUSHED=false")
    return 0

if __name__ == "__main__": raise SystemExit(main())
