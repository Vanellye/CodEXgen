#!/usr/bin/env bash
set -euo pipefail
echo "Ɣơ ARM build preflight"
NDK="${ANDROID_NDK_HOME:-${ANDROID_NDK_ROOT:-}}"
if [[ -z "$NDK" || ! -d "$NDK" ]]; then
  echo "HOLD: Android NDK unavailable; no ARM binary built."
  exit 2
fi
if ! find "$NDK/toolchains/llvm/prebuilt" -name 'aarch64-linux-android*-clang' -type f -print -quit 2>/dev/null | grep -q .; then
  echo "HOLD: Android ARM64 clang toolchain not found."
  exit 2
fi
echo "READY: ARM64 toolchain detected; no native target is defined in this Python-only milestone."
echo "A native binary requires a separately reviewed source target and reproducible build recipe."
