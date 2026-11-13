#!/data/data/com.termux/files/usr/bin/bash
# ERIA Show Files — read-only inventory, including dotfiles.
# Usage: eria-show-files [directory]
set -u

ROOT="${1:-$HOME}"
OUT="${ERIA_FILE_LIST:-$HOME/eria-file-inventory.txt}"

if ! command -v find >/dev/null 2>&1; then
  printf 'ERROR: find is unavailable. Install it with: pkg install findutils\n' >&2
  exit 127
fi

if [ ! -d "$ROOT" ]; then
  printf 'ERROR: not a directory: %s\n' "$ROOT" >&2
  exit 2
fi

ROOT="$(cd -- "$ROOT" 2>/dev/null && pwd -P)" || {
  printf 'ERROR: cannot enter directory: %s\n' "$ROOT" >&2
  exit 3
}

TMP="${OUT}.tmp.$$"
ERR="${OUT}.errors.$$"
trap 'rm -f -- "$TMP" "$ERR"' EXIT HUP INT TERM

# find includes hidden entries automatically; -P behavior is the default,
# so symbolic links are listed but not traversed.
if ! find "$ROOT" -path "$OUT" -prune -o -path "$TMP" -prune -o -path "$ERR" -prune -o -print >"$TMP" 2>"$ERR"; then
  FIND_STATUS=1
else
  FIND_STATUS=0
fi

if ! mv -- "$TMP" "$OUT"; then
  printf 'ERROR: cannot write inventory to %s\n' "$OUT" >&2
  exit 5
fi

printf 'Inventory: %s\n' "$OUT"
printf 'Entries: '
wc -l <"$OUT"
if [ -s "$ERR" ]; then
  printf '\nSome paths could not be inspected (no permission bypass attempted):\n' >&2
  cat "$ERR" >&2
fi
rm -f -- "$ERR"
trap - EXIT HUP INT TERM
exit "$FIND_STATUS"
