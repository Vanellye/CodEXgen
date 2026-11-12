#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ACTUATOR="$HERE/../runtime/thanks-actuator.sh"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

base=(--simulate --trigger detected --approval-id approval-test-001 --actor test-reviewer
  --scope THANKs:simulated-motion:execute --evidence-status SUPPORTED
  --evidence-id evidence-test-001 --independent yes --reproducible yes
  --requested-speed 1.5 --max-speed 2.0)

expect_blocked() {
  local name="$1"; shift
  if bash "$ACTUATOR" "${base[@]}" "$@" >"$tmp/out" 2>&1; then
    echo "FAIL: $name unexpectedly passed"; exit 1
  fi
  grep -q 'DECISION=BLOCKED' "$tmp/out" || { echo "FAIL: $name had no blocked decision"; cat "$tmp/out"; exit 1; }
  echo "PASS: $name"
}

bash "$ACTUATOR" "${base[@]}" >"$tmp/out"
grep -q 'DECISION=SIMULATED_ACTUATION' "$tmp/out"
grep -q 'PHYSICAL_ACTUATION=none' "$tmp/out"
echo "PASS: both independent gates permit simulation only"

expect_blocked "authorization missing" --approval-id ""
expect_blocked "authorization scope mismatch" --scope THANKs:physical:execute
expect_blocked "evidence not supported" --evidence-status PARTIAL
expect_blocked "evidence not independent" --independent no
expect_blocked "evidence not reproducible" --reproducible no
expect_blocked "trigger without recognized detection" --trigger ""
expect_blocked "speed above ceiling" --requested-speed 2.1
expect_blocked "emergency stop" --emergency-stop yes

echo "ALL_TESTS_PASSED"
