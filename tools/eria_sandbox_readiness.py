#!/usr/bin/env python3
"""Read-only Linux sandbox capability probe; never launches candidate code."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return None


def probe(host_root: Path = Path("/"), *, platform: str | None = None,
          bwrap_path: str | None = None) -> dict[str, Any]:
    """Inspect host prerequisites without invoking subprocesses or mutating state."""
    actual_platform = sys.platform if platform is None else platform
    proc = host_root / "proc"
    sys_root = host_root / "sys"
    namespace_text = _read_text(proc / "sys/user/max_user_namespaces")
    try:
        namespace_count = int(namespace_text) if namespace_text is not None else 0
    except ValueError:
        namespace_count = 0

    controllers_text = _read_text(sys_root / "fs/cgroup/cgroup.controllers")
    controllers = sorted(set((controllers_text or "").split()))
    bwrap = bwrap_path if bwrap_path is not None else shutil.which("bwrap")
    checks = {
        "linux_host": actual_platform.startswith("linux"),
        "bubblewrap_present": bool(bwrap),
        "unprivileged_user_namespaces": namespace_count > 0,
        "cgroup_v2_present": (sys_root / "fs/cgroup/cgroup.controllers").is_file(),
        "cpu_controller": "cpu" in controllers,
        "memory_controller": "memory" in controllers,
        "pids_controller": "pids" in controllers,
    }
    ready = all(checks.values())
    return {
        "schema": "eria.sandbox.readiness/1.0",
        "status": "HOST_PREREQUISITES_PRESENT_REVIEW_REQUIRED" if ready else "HOST_NOT_READY",
        "checks": {key: "PASS" if value else "FAIL" for key, value in checks.items()},
        "observed": {
            "platform": actual_platform,
            "bubblewrap_path": bwrap or None,
            "user_namespace_limit": namespace_count,
            "cgroup_v2_controllers": controllers,
        },
        "execution_enabled": False,
        "candidate_code_executed": False,
        "source_write_enabled": False,
        "pons_decision": "HOLD",
        "limitations": [
            "Presence checks do not prove that namespace creation or isolation works.",
            "No bubblewrap command or candidate process was launched.",
            "No network-isolation, mount, seccomp, or resource-limit behavior was tested.",
            "A trusted, exact-digest PONS grant and a separately reviewed runner remain required.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host-root", type=Path, default=Path("/"),
                        help="Root used for read-only /proc and /sys inspection.")
    args = parser.parse_args()
    result = probe(args.host_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
