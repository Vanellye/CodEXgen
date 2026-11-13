#!/usr/bin/env bash
# Read-only verifier: checks a detached SHA-256 and parses JSON; never sources or executes manifest data.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  printf 'usage: %s <manifest.json> <manifest.sha256>\n' "$0" >&2
  exit 2
fi

manifest=$1
checksum_file=$2

[[ -f "$manifest" && -r "$manifest" ]] || { echo "manifest is not a readable regular file" >&2; exit 2; }
[[ -f "$checksum_file" && -r "$checksum_file" ]] || { echo "checksum file is not a readable regular file" >&2; exit 2; }
command -v sha256sum >/dev/null 2>&1 || { echo "sha256sum is required" >&2; exit 2; }
command -v python3 >/dev/null 2>&1 || { echo "python3 is required for JSON syntax validation" >&2; exit 2; }

expected=$(awk 'NR == 1 { print $1 }' "$checksum_file")
[[ "$expected" =~ ^[[:xdigit:]]{64}$ ]] || { echo "invalid SHA-256 checksum format" >&2; exit 1; }
actual=$(sha256sum -- "$manifest")
actual=${actual%% *}
[[ "$actual" == "$expected" ]] || { echo "manifest SHA-256 mismatch" >&2; exit 1; }
python3 -m json.tool "$manifest" >/dev/null
printf 'ERIA manifest integrity: OK (%s)\n' "$actual"
