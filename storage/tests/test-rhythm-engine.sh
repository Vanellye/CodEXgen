#!/usr/bin/env bash
set -Eeuo pipefail
ENGINE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/rhythm-engine.sh"
TMP_ROOT=$(mktemp -d)
trap 'rm -rf -- "$TMP_ROOT"' EXIT
export ERIA_STORAGE_ROOT="$TMP_ROOT/state"
pass=0
fail=0

ok() {
    local name=$1
    shift
    if "$@"; then
        printf 'ok - %s\n' "$name"
        pass=$((pass + 1))
    else
        printf 'not ok - %s\n' "$name" >&2
        fail=$((fail + 1))
    fi
}
expect_fail() {
    local name=$1
    shift
    if "$@" >/dev/null 2>&1; then
        printf 'not ok - %s (unexpected success)\n' "$name" >&2
        fail=$((fail + 1))
    else
        printf 'ok - %s\n' "$name"
        pass=$((pass + 1))
    fi
}

mkdir -p "$TMP_ROOT/data"
printf 'ERIA rhythm payload\n' > "$TMP_ROOT/data/source.txt"
printf 'old payload\n' > "$TMP_ROOT/data/existing.txt"

ok "read emits SHA-256" bash -c '"$1" read "$2" | grep -Eq "^[0-9a-f]{64}  "' _ "$ENGINE" "$TMP_ROOT/data/source.txt"
ok "write creates destination" "$ENGINE" write "$TMP_ROOT/data/source.txt" "$TMP_ROOT/data/new.txt"
ok "verify accepts identical content" "$ENGINE" verify "$TMP_ROOT/data/source.txt" "$TMP_ROOT/data/new.txt"
expect_fail "write refuses overwrite by default" "$ENGINE" write "$TMP_ROOT/data/source.txt" "$TMP_ROOT/data/existing.txt"
ok "refused overwrite preserves existing bytes" grep -qx 'old payload' "$TMP_ROOT/data/existing.txt"
ok "explicit overwrite replaces destination" "$ENGINE" write --overwrite "$TMP_ROOT/data/source.txt" "$TMP_ROOT/data/existing.txt"
ok "overwritten destination verifies" "$ENGINE" verify "$TMP_ROOT/data/source.txt" "$TMP_ROOT/data/existing.txt"
expect_fail "read rejects missing file" "$ENGINE" read "$TMP_ROOT/data/missing.txt"
expect_fail "verify rejects missing destination" "$ENGINE" verify "$TMP_ROOT/data/source.txt" "$TMP_ROOT/data/missing.txt"
expect_fail "write rejects missing source" "$ENGINE" write "$TMP_ROOT/data/missing.txt" "$TMP_ROOT/data/nope.txt"
expect_fail "write rejects source equal to destination" "$ENGINE" write "$TMP_ROOT/data/source.txt" "$TMP_ROOT/data/source.txt"
expect_fail "invalid argument count is rejected" "$ENGINE" write
expect_fail "checkpoint rejects unsafe label" "$ENGINE" checkpoint "$TMP_ROOT/data/source.txt" '../escape'
ok "checkpoint writes checksum manifest" bash -c '
    "$1" checkpoint "$2" unit-test >/dev/null &&
    grep -Eq "^sha256=[0-9a-f]{64}$" "$ERIA_STORAGE_ROOT"/checkpoints/*.checkpoint
' _ "$ENGINE" "$TMP_ROOT/data/source.txt"
ok "sync copies and verifies" "$ENGINE" sync "$TMP_ROOT/data/source.txt" "$TMP_ROOT/data/synced.txt"

printf '\nBash M*ASH tests: %d passed, %d failed\n' "$pass" "$fail"
(( fail == 0 ))
