#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${ERIA_REPO:-$HOME/CodEXgen}"
cd "$ROOT"

# User-configurable ERIA worker controls. These change ERIA's own runner
# configuration only; Android/Termux OS and permission boundaries remain in force.
GENESIS_INTERVAL="${GENESIS_INTERVAL:-900}"
GENESIS_OUT="${GENESIS_OUT:-$ROOT/generated_modules}"
GENESIS_AUDIT="${GENESIS_AUDIT:-$ROOT/.eria/genesis-runs.jsonl}"
GENESIS_LOCK="${GENESIS_LOCK:-$ROOT/.eria/genesis.lock}"

case "$GENESIS_INTERVAL" in
  ''|*[!0-9]*)
    echo "GENESIS_INTERVAL must be an integer number of seconds." >&2
    exit 2
    ;;
esac

if (( GENESIS_INTERVAL < 60 )); then
  echo "GENESIS_INTERVAL must be at least 60 seconds to protect device resources." >&2
  exit 2
fi

mkdir -p "$(dirname "$GENESIS_AUDIT")" "$(dirname "$GENESIS_LOCK")" "$GENESIS_OUT"

exec python tools/genesis_constant_runner.py \
  --interval "$GENESIS_INTERVAL" \
  --out "$GENESIS_OUT" \
  --audit "$GENESIS_AUDIT" \
  --lock "$GENESIS_LOCK"
