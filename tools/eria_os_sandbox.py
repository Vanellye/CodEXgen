#!/usr/bin/env python3
"""Fail-closed bubblewrap runner for isolated ERIA validation jobs."""
from __future__ import annotations
import argparse, os, platform, shutil, subprocess, sys
from pathlib import Path

class SandboxError(RuntimeError): pass

def build_command(workspace: Path, command: list[str]) -> list[str]:
    if platform.system() != "Linux":
        raise SandboxError("OS sandbox requires Linux.")
    bwrap = shutil.which("bwrap")
    if not bwrap:
        raise SandboxError("bubblewrap (bwrap) missing; refusing unsandboxed execution.")
    workspace = workspace.resolve()
    if not workspace.is_dir():
        raise SandboxError("Workspace directory does not exist.")
    args = [bwrap, "--die-with-parent", "--new-session", "--unshare-all",
            "--unshare-net", "--cap-drop", "ALL", "--ro-bind", "/", "/",
            "--dev", "/dev", "--proc", "/proc", "--tmpfs", "/tmp"]
    for path in (Path.home(), Path("/root"), Path("/storage"), Path("/sdcard"),
                 Path("/mnt"), Path("/media"), Path("/run"), Path("/var/tmp")):
        if path.exists() and str(path) not in ("/", "/tmp"):
            args.extend(["--tmpfs", str(path)])
    args.extend(["--bind", str(workspace), "/workspace", "--chdir", "/workspace",
                 "--setenv", "HOME", "/tmp/eria-home",
                 "--setenv", "PATH", os.environ.get("PATH", "/usr/bin:/bin"),
                 "--setenv", "PYTHONDONTWRITEBYTECODE", "1", "--", *command])
    return args

def run(workspace: Path, command: list[str], timeout: int = 300) -> int:
    if not command: raise SandboxError("No command supplied.")
    try:
        result = subprocess.run(build_command(workspace, command), capture_output=True,
                                text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired as exc:
        raise SandboxError(f"Sandbox timed out after {timeout} seconds.") from exc
    except OSError as exc:
        raise SandboxError(f"bubblewrap could not start: {exc}") from exc
    if result.stdout: print(result.stdout, end="")
    if result.stderr: print(result.stderr, end="", file=sys.stderr)
    return result.returncode

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("command", nargs=argparse.REMAINDER)
    a = p.parse_args()
    cmd = a.command[1:] if a.command[:1] == ["--"] else a.command
    try: return run(a.workspace, cmd, a.timeout)
    except SandboxError as exc:
        print("ERIA SANDBOX HOLD:", exc, file=sys.stderr); return 125

if __name__ == "__main__": raise SystemExit(main())
