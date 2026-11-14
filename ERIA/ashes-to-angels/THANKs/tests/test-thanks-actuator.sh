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
echo "PASS: detected trigger plus both independent gates permits simulation only"

manual=(--trigger manual --manual-trigger-approval-id manual-approval-001
  --manual-trigger-reason "automatic detector unavailable")
bash "$ACTUATOR" "${base[@]}" "${manual[@]}" >"$tmp/out"
grep -q 'TRIGGER_OVERRIDE=ON' "$tmp/out"
grep -q 'TRIGGER_PATH=MANUAL_OVERRIDE' "$tmp/out"
grep -q 'DECISION=SIMULATED_ACTUATION' "$tmp/out"
echo "PASS: manual override requires its own authorization and both gates"

expect_blocked "manual override missing authorization ID" --trigger manual --manual-trigger-reason "detector unavailable"
expect_blocked "manual override missing reason" --trigger manual --manual-trigger-approval-id manual-approval-001
expect_blocked "Pheônix authorization missing" --approval-id ""
expect_blocked "Pheônix authorization scope mismatch" --scope THANKs:physical:execute
expect_blocked "Sure-rarity evidence not supported" --evidence-status PARTIAL
expect_blocked "Sure-rarity evidence not independent" --independent no
expect_blocked "Sure-rarity evidence not reproducible" --reproducible no
expect_blocked "missing trigger path" --trigger ""
expect_blocked "speed above ceiling" --requested-speed 2.1
expect_blocked "emergency stop" --emergency-stop yes

# The override is a fixed-on policy constant; an environment value cannot disable it.
TRIGGER_OVERRIDE=OFF bash "$ACTUATOR" "${base[@]}" "${manual[@]}" >"$tmp/out"
grep -q 'TRIGGER_OVERRIDE=ON' "$tmp/out"
echo "PASS: environment cannot restore an OFF switch"

echo "ALL_TESTS_PASSED"
