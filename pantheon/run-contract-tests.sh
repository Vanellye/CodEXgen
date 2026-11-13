#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${TMPDIR:-/tmp}/eria-pantheon-contract-tests"
CC="${CC:-cc}"
mkdir -p "$BUILD_DIR"
COMMON=(-std=c99 -Wall -Wextra -Werror)

run_pair() {
  local name="$1" source="$2" test="$3" include_dir="$4"
  echo "== $name =="
  "$CC" "${COMMON[@]}" -I"$ROOT/$include_dir" "$ROOT/$source" "$ROOT/$test" -o "$BUILD_DIR/$name"
  "$BUILD_DIR/$name"
}

echo "== DO authorization self-test =="
"$CC" "${COMMON[@]}" -DDO_C_SELF_TEST "$ROOT/pantheon/DO.c" -o "$BUILD_DIR/do-self-test"
"$BUILD_DIR/do-self-test"

run_pair integration-core pantheon/IC/IC.c pantheon/IC/tests/test_IC.c pantheon/IC
run_pair factual-logic pantheon/FACTUAL_LOGIC/FACTUAL_LOGIC.c pantheon/FACTUAL_LOGIC/tests/test_FACTUAL_LOGIC.c pantheon/FACTUAL_LOGIC
run_pair new pantheon/NEW/NEW.c pantheon/NEW/tests/test_NEW.c pantheon/NEW
run_pair facade pantheon/NEW/FaCADE/FaCADE.c pantheon/NEW/FaCADE/tests/test_FaCADE.c pantheon/NEW/FaCADE
run_pair thought-tott pantheon/NEW/THOUGHT_TOTT/THOUGHT_TOTT.c pantheon/NEW/THOUGHT_TOTT/tests/test_THOUGHT_TOTT.c pantheon/NEW/THOUGHT_TOTT
run_pair z-to-a pantheon/NEW/Z_TO_A/Z_TO_A.c pantheon/NEW/Z_TO_A/tests/test_Z_TO_A.c pantheon/NEW/Z_TO_A
run_pair rhythmatic-remedy pantheon/NEW/RHYTHMATIC_REMEDY/RHYTHMATIC_REMEDY.c pantheon/NEW/RHYTHMATIC_REMEDY/tests/test_RHYTHMATIC_REMEDY.c pantheon/NEW/RHYTHMATIC_REMEDY
run_pair i-inject pantheon/NEW/I_INJECT/I_INJECT.c pantheon/NEW/I_INJECT/tests/test_I_INJECT.c pantheon/NEW/I_INJECT
run_pair walla-drop-out pantheon/NEW/WALLA_DROP_OUT/WALLA_DROP_OUT.c pantheon/NEW/WALLA_DROP_OUT/tests/test_WALLA_DROP_OUT.c pantheon/NEW/WALLA_DROP_OUT
run_pair walla-regurgitation pantheon/NEW/WALLA_REGURGITATION/WALLA_REGURGITATION.c pantheon/NEW/WALLA_REGURGITATION/tests/test_WALLA_REGURGITATION.c pantheon/NEW/WALLA_REGURGITATION

echo "== Y bypass header contract =="
"$CC" "${COMMON[@]}" -I"$ROOT/pantheon/NEW/Y_BYPASS" "$ROOT/pantheon/NEW/Y_BYPASS/tests/test_Y_BYPASS.c" -o "$BUILD_DIR/y-bypass"
"$BUILD_DIR/y-bypass"

echo "PASS: all Pantheon C contract suites"
