#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
command -v python >/dev/null || { echo "Install Python first: pkg install python"; exit 1; }
export AIE_HOST="${AIE_HOST:-127.0.0.1}"
export AIE_PORT="${AIE_PORT:-8780}"
export ERIA_API_ORIGIN="${ERIA_API_ORIGIN:-http://127.0.0.1:8778}"
echo "Starting Æị standalone. Open http://127.0.0.1:${AIE_PORT}/ on this phone."
echo "The existing ERIA API must already be running at ${ERIA_API_ORIGIN}."
exec python "$HERE/server.py"
