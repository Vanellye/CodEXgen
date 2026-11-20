#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NDK="${ANDROID_NDK_HOME:-${ANDROID_NDK_ROOT:-}}"
if [[ -z "$NDK" || ! -d "$NDK" ]]; then echo "HOLD: Android NDK unavailable; ARM64 binary not built."; exit 2; fi
HOST_TAG="$(uname -s | tr '[:upper:]' '[:lower:]')-$(uname -m)"
TOOLCHAIN="$NDK/toolchains/llvm/prebuilt/$HOST_TAG/bin"
if [[ ! -x "$TOOLCHAIN/aarch64-linux-android24-clang++" ]]; then echo "HOLD: ARM64 compiler missing for $HOST_TAG."; exit 2; fi
OUT="${1:-$ROOT/build/arm64-v8a}"; mkdir -p "$OUT"
"$TOOLCHAIN/aarch64-linux-android24-clang++" -std=c++17 -O2 -Wall -Wextra -Werror \
  "$ROOT/native/arm64/codec_probe.cpp" -o "$OUT/gamma-codec-probe"
file "$OUT/gamma-codec-probe"
echo "BUILT: ARM64 codec smoke binary (not a finance executor)."
