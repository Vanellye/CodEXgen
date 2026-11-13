#!/usr/bin/env bash
# Read-only adapter: parses and validates a supplied record; never executes its action.
set -euo pipefail
if [[ $# -lt 1 || $# -gt 2 ]]; then
  printf 'usage: %s RECORD.json [EXPECTED_COMMIT_SHA]\n' "$0" >&2
  exit 64
fi
SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
if [[ $# -eq 2 ]]; then
  exec python3 "$SCRIPT_DIR/verify_evidence.py" "$1" --expected-sha "$2"
fi
exec python3 "$SCRIPT_DIR/verify_evidence.py" "$1"
