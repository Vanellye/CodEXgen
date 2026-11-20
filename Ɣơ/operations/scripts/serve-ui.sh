#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UI_DIR="$(cd "$SCRIPT_DIR/../ui" && pwd)"
PORT="${PORT:-8765}"
cd "$UI_DIR"
echo "ERIA Repository Eyes: http://127.0.0.1:$PORT/"
echo "Stop the local viewer with Ctrl+C. No external host is contacted."
exec python3 -m http.server "$PORT" --bind 127.0.0.1
