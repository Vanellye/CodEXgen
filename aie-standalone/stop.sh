#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
PORT="${AIE_PORT:-8780}"
PIDS="$(pgrep -f 'aie-standalone/server.py' || true)"
if [ -z "$PIDS" ]; then echo "No Æị standalone process found."; exit 0; fi
for PID in $PIDS; do
  [ "$PID" = "$$" ] || kill "$PID" 2>/dev/null || true
done
echo "Stop signal sent to Æị standalone process(es) on port $PORT."
