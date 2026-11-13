#!/usr/bin/env bash
set -Eeuo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
spec="$root/docs/PERMINT-LANGUAGE-EXTENSION.md"
[[ -f "$spec" && ! -L "$spec" ]]
for token in '***' '#' '&^&^&' '×' '^&&&^' '÷' '()'; do
  grep -Fq -- "$token" "$spec" || { printf 'MISSING_OPERATOR=%s\n' "$token" >&2; exit 1; }
done
for term in 'Proposed-@L·L Language' 'AðÐ' 'Bridge integrity' 'BREAK' '("a" a "m")' 'ion rinse' 'x ride z roll 2 þæč̣' '"T"' '"O"' '§ŢĀN̈ĎÏÑƔ' '"STride" Code' 'Forward Faculty' 'A.M.A.' 'Auto Matic Ally Addinɣ' 'Code Genesis Extract' 'ALL·L·^' '*^\\_/^*' 'INCOMPLETE' 'NO_CONSENT'; do
  grep -Fq -- "$term" "$spec" || { printf 'MISSING_REQUIREMENT=%s\n' "$term" >&2; exit 1; }
done
grep -Fq 'not implemented by' "$spec"
grep -Fq 'No source file is modified' "$spec"
grep -Fq 'no retry or dispatch occurs' "$spec"
printf 'PERMINT_SPEC_TESTS=PASS\n'
