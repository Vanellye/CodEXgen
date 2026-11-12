#!/usr/bin/env bash
# ÆĀÄÂ advisory source scanner. Read-only; never executes or repairs scanned files.
set -euo pipefail

ROOT="${1:-.}"
if [[ ! -d "$ROOT" ]]; then
  echo "ERROR: scan root is not a directory: $ROOT" >&2
  exit 2
fi

printf 'AEAA_SCAN\tmode=read-only\troot=%s\n' "$ROOT"
printf 'CLASS\tPATH\tLINE\tRULE\tEVIDENCE\n'

# Review prompts only; avoid generated/build/vendor directories.
while IFS= read -r -d '' file; do
  case "$file" in
    */.git/*|*/build/*|*/.gradle/*|*/.venv/*|*/node_modules/*|*/vendor/*) continue ;;
  esac
  case "$file" in
    *.sh|*.bash|*.yml|*.yaml|*.py|*.kt|*.kts|*.java|*.c|*.h|*.cpp|*.hpp|Dockerfile|*.toml) ;;
    *) continue ;;
  esac
  awk '
    /curl[[:space:]].*\\|[[:space:]]*(sh|bash)([[:space:]]|$)/ { printf "HEURISTIC\\t%s\\t%d\\tREMOTE-PIPE-TO-SHELL\\t%s\\n", FILENAME, FNR, $0 }
    /(^|[;[:space:]])eval[[:space:]]/ { printf "HEURISTIC\\t%s\\t%d\\tDYNAMIC-EVAL\\t%s\\n", FILENAME, FNR, $0 }
    /rm[[:space:]]+-rf[[:space:]]+\\/([[:space:]]|$)/ { printf "HEURISTIC\\t%s\\t%d\\tROOT-RECURSIVE-DELETE\\t%s\\n", FILENAME, FNR, $0 }
    /chmod[[:space:]]+(-R[[:space:]]+)?777([[:space:]]|$)/ { printf "HEURISTIC\\t%s\\t%d\\tWORLD-WRITABLE-PERMISSIONS\\t%s\\n", FILENAME, FNR, $0 }
  ' "$file"
done < <(find "$ROOT" -type f -print0)

printf 'AEAA_SCAN_COMPLETE\\tadvisory_only=true\\tautomatic_changes=none\\n'
