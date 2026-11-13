#!/usr/bin/env bash
set -Eeuo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
spec="$root/docs/PERMINT-LANGUAGE-EXTENSION.md"
[[ -f "$spec" && ! -L "$spec" ]]
for token in '***' '#' '&^&^&' '×' '^&&&^' '÷' '()'; do
  grep -Fq -- "$token" "$spec" || { printf 'MISSING_OPERATOR=%s\n' "$token" >&2; exit 1; }
done
for term in 'Intent' 'Consent' 'Evidence' 'Forward' 'Reverse' 'Review' 'Forward Faculty' 'Permint' '§ŢĀN̈ĎÏÑƔ' '"STride" Code'; do
  grep -Fq -- "$term" "$spec" || { printf 'MISSING_REQUIREMENT=%s\n' "$term" >&2; exit 1; }
done
grep -Fq 'not accepted by the current v0.1 interpreter' "$spec"
grep -Fq 'No source file is modified' "$spec"
grep -Fq 'cannot approve or execute its own proposal' "$spec"
printf 'PERMINT_SPEC_TESTS=PASS\n'
