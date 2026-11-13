#!/data/data/com.termux/files/usr/bin/bash
# ERIA Root Inventory — read-only path inventory for an already-rooted device.
# Usage: eria-root-inventory [output-file]
# Root is requested only through the installed su manager; no exploit or rooting.
set -u
umask 077

OUT="${1:-$HOME/eria-root-inventory.txt}"
AUDIT="${ERIA_ROOT_AUDIT:-$HOME/.eria/root-inventory.tsv}"
TMP="${TMPDIR:-$HOME}/eria-root-inventory.tmp.$$"
ERR="${TMPDIR:-$HOME}/eria-root-inventory.err.$$"

cleanup() { rm -f -- "$TMP" "$ERR"; }
trap cleanup EXIT HUP INT TERM

if ! command -v find >/dev/null 2>&1; then
  printf 'ERROR: find unavailable. Run: pkg install findutils\n' >&2
  exit 127
fi
if ! command -v sha256sum >/dev/null 2>&1; then
  printf 'ERROR: sha256sum unavailable. Run: pkg install coreutils\n' >&2
  exit 127
fi

OUT_DIR="$(dirname -- "$OUT")"
mkdir -p -- "$OUT_DIR" "$(dirname -- "$AUDIT")" || exit 5
: > "$TMP" || exit 5
: > "$ERR" || exit 5

UID_NOW="$(id -u)"
ROOT_MODE="user"
if [ "$UID_NOW" = "0" ]; then
  ROOT_MODE="root-shell"
elif command -v su >/dev/null 2>&1 && su -c 'test "$(id -u)" = 0' >/dev/null 2>&1; then
  ROOT_MODE="su-approved"
else
  printf 'ROOT NOT AVAILABLE: inventory will not run. Install/configure a legitimate root manager if your bootloader/device supports rooting.\n' >&2
  printf 'No exploit, privilege bypass, or fallback scan was attempted.\n' >&2
  exit 10
fi

# Skip volatile kernel interfaces and pseudo-filesystems. Other mounted
# filesystems are traversed. find lists names/paths only; it does not read
# file contents and does not follow symbolic links.
if [ "$ROOT_MODE" = "root-shell" ]; then
  find / \( -path /proc -o -path /sys -o -path /dev -o -path /run \) -prune -o -print >"$TMP" 2>"$ERR"
  FIND_STATUS=$?
else
  su -c 'find / \( -path /proc -o -path /sys -o -path /dev -o -path /run \) -prune -o -print' >"$TMP" 2>"$ERR"
  FIND_STATUS=$?
fi

# Remove the temporary inventory and final output if encountered during scan.
grep -Fvx -e "$TMP" -e "$ERR" -e "$OUT" "$TMP" > "${TMP}.filtered" 2>/dev/null || true
mv -- "${TMP}.filtered" "$TMP" || exit 5
mv -- "$TMP" "$OUT" || {
  printf 'ERROR: cannot write inventory: %s\n' "$OUT" >&2
  exit 5
}

STAMP="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
DEVICE="$(getprop ro.product.model 2>/dev/null || printf unknown)"
SCRIPT_HASH="$(sha256sum "$0" | awk '{print $1}')"
INVENTORY_HASH="$(sha256sum "$OUT" | awk '{print $1}')"
COUNT="$(wc -l < "$OUT" | tr -d ' ')"
ERROR_COUNT="$(wc -l < "$ERR" | tr -d ' ')"

printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  "$STAMP" "$DEVICE" "$ROOT_MODE" "$FIND_STATUS" "$COUNT" \
  "$ERROR_COUNT" "$SCRIPT_HASH" "$INVENTORY_HASH" >> "$AUDIT"

printf 'Mode: %s\nInventory: %s\nEntries: %s\n' "$ROOT_MODE" "$OUT" "$COUNT"
printf 'Permission/scan errors: %s\nAudit: %s\n' "$ERROR_COUNT" "$AUDIT"
if [ -s "$ERR" ]; then
  printf '\nSome paths were not readable:\n' >&2
  cat "$ERR" >&2
fi
exit "$FIND_STATUS"
