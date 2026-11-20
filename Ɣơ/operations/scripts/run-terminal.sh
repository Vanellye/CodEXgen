#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
export PYTHONPATH="$ROOT/Ɣơ/operations/src${PYTHONPATH:+:$PYTHONPATH}"
exec python -m gamma_ops.cli "$@"
