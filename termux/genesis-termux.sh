#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
ROOT="${ERIA_REPO:-$HOME/CodEXgen}"
cd "$ROOT"
exec python tools/genesis_constant_runner.py --interval "${GENESIS_INTERVAL:-900}"
