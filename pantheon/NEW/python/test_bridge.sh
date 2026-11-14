#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
NEW_DIR="$(cd "$HERE/.." && pwd)"
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT

CC="${CC:-clang}"
command -v "$CC" >/dev/null 2>&1 || {
  echo "Missing C compiler. Install it with: pkg install clang"
  exit 2
}

"$CC" -std=c11 -Wall -Wextra -Werror -fPIC -shared \
  -I"$NEW_DIR" \
  "$NEW_DIR/NEW.c" \
  "$NEW_DIR/FaCADE/FaCADE.c" \
  -o "$BUILD_DIR/liberia_pantheon.so"

export ERIA_PANTHEON_LIBRARY="$BUILD_DIR/liberia_pantheon.so"
export PYTHONPATH="$HERE${PYTHONPATH:+:$PYTHONPATH}"

python -m unittest discover -s "$HERE/tests" -v
