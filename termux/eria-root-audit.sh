#!/data/data/com.termux/files/usr/bin/bash
# ERIA Root-Aware Filesystem Audit
# Read-only. Never invokes su, changes permissions, or reads file contents.
set -u
umask 077

OUT="${ERIA_FILE_LIST:-$HOME/eria-filesystem-inventory.txt}"
AUDIT="${ERIA_AUDIT:-$HOME/.eria/filesystem-audit.jsonl}"
ERRORS="${ERIA_ERRORS:-$HOME/eria-filesystem-errors.txt}"
MODE="USER"
UID_NOW="$(id -u 2>/dev/null || printf 'unknown')"

if [ "$UID_NOW" = "0" ]; then
  MODE="ROOT"
fi

for tool in find date sha256sum wc; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    printf 'ERROR: missing command: %s\n' "$tool" >&2
    printf 'Install Termux packages if needed: pkg install findutils coreutils\n' >&2
    exit 127
  fi
done

mkdir -p "$(dirname "$OUT")" "$(dirname "$AUDIT")" "$(dirname "$ERRORS")" || exit 5
TMP="${OUT}.tmp.$$"
ERRTMP="${ERRORS}.tmp.$$"
trap 'rm -f -- "$TMP" "$ERRTMP"' EXIT HUP INT TERM
: > "$TMP"
: > "$ERRTMP"

# User mode scans Termux home and shared storage. Root mode additionally
# attempts common Android filesystem roots; find reports denied paths.
if [ "$MODE" = "ROOT" ]; then
  ROOTS=(/)
else
  ROOTS=("$HOME" "$HOME/storage/shared" /storage/emulated/0 /sdcard)
fi

declare -A SEEN=()
for scan in "${ROOTS[@]}"; do
  [ -d "$scan" ] || continue
  real="$(cd -- "$scan" 2>/dev/null && pwd -P)" || {
    printf 'CANNOT_ENTER\t%s\n' "$scan" >> "$ERRTMP"
    continue
  }
  [ -n "${SEEN[$real]+x}" ] && continue
  SEEN["$real"]=1
  printf '\n===== ROOT %s =====\n' "$real" >> "$TMP"

  if [ "$MODE" = "ROOT" ] && [ "$real" = "/" ]; then
    find -P "$real" \
      \( -path /proc -o -path /sys -o -path /dev -o -path /acct -o -path /config \
         -o -path "$OUT" -o -path "$TMP" -o -path "$ERRTMP" \
         -o -path "$ERRORS" -o -path "$AUDIT" \) -prune \
      -o -print >> "$TMP" 2>> "$ERRTMP" || true
  else
    find -P "$real" \
      \( -path "$OUT" -o -path "$TMP" -o -path "$ERRTMP" \
         -o -path "$ERRORS" -o -path "$AUDIT" \) -prune \
      -o -print >> "$TMP" 2>> "$ERRTMP" || true
  fi
done

if ! mv -- "$TMP" "$OUT"; then
  printf 'ERROR: cannot write inventory: %s\n' "$OUT" >&2
  exit 6
fi
mv -- "$ERRTMP" "$ERRORS" || exit 7

STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
COUNT="$(wc -l < "$OUT" | tr -d ' ')"
DENIED="$(wc -l < "$ERRORS" | tr -d ' ')"
HASH="$(sha256sum "$OUT" | awk '{print $1}')"
mkdir -p "$(dirname "$AUDIT")"
printf '{"timestamp":"%s","uid":"%s","mode":"%s","inventory":"%s","entries":%s,"error_lines":%s,"sha256":"%s","read_only":true,"su_invoked":false}\n' \
  "$STAMP" "$UID_NOW" "$MODE" "$OUT" "$COUNT" "$DENIED" "$HASH" >> "$AUDIT"

printf 'ERIA filesystem audit complete\n'
printf 'Mode: %s (uid=%s)\n' "$MODE" "$UID_NOW"
printf 'Inventory: %s (%s lines)\n' "$OUT" "$COUNT"
printf 'Errors: %s (%s lines)\n' "$ERRORS" "$DENIED"
printf 'Audit ledger: %s\n' "$AUDIT"
printf 'Inventory SHA-256: %s\n' "$HASH"
printf 'No privilege escalation or file-content reads were attempted.\n'
