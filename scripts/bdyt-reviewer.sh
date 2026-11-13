#!/usr/bin/env bash
# bđyt ÆŤ8Ð — bounded, read-only background reviewer.
# Usage: bash scripts/bdyt-reviewer.sh SOURCE_FILE CANDIDATE_FILE
# This tool never edits, deletes, executes, or dispatches either input.

set -Eeuo pipefail
IFS=$'\n\t'

readonly MAX_BYTES=$((10 * 1024 * 1024))

fail() {
  printf 'BDYT_REVIEW=BLOCKED\nREASON=%s\n' "$1" >&2
  exit 2
}

[[ $# -eq 2 ]] || fail "usage: $0 SOURCE_FILE CANDIDATE_FILE"

source_arg=$1
candidate_arg=$2

[[ -f "$source_arg" && ! -L "$source_arg" ]] || fail "source must be an existing regular file, not a symlink"
[[ -f "$candidate_arg" && ! -L "$candidate_arg" ]] || fail "candidate must be an existing regular file, not a symlink"

source_file=$(cd -- "$(dirname -- "$source_arg")" && printf '%s/%s' "$PWD" "$(basename -- "$source_arg")")
candidate_file=$(cd -- "$(dirname -- "$candidate_arg")" && printf '%s/%s' "$PWD" "$(basename -- "$candidate_arg")")

[[ "$source_file" != "$candidate_file" ]] || fail "source and candidate must be distinct paths"

for tool in sha256sum wc cmp diff awk; do
  command -v "$tool" >/dev/null 2>&1 || fail "required utility missing: $tool"
done

source_bytes=$(wc -c < "$source_file")
candidate_bytes=$(wc -c < "$candidate_file")
source_bytes=$(printf '%s' "$source_bytes" | tr -d '[:space:]')
candidate_bytes=$(printf '%s' "$candidate_bytes" | tr -d '[:space:]')

[[ "$source_bytes" =~ ^[0-9]+$ && "$candidate_bytes" =~ ^[0-9]+$ ]] || fail "could not measure input bytes"
(( source_bytes <= MAX_BYTES && candidate_bytes <= MAX_BYTES )) || fail "input exceeds 10 MiB review limit"

source_digest=$(sha256sum -- "$source_file" | awk '{print $1}')
candidate_digest=$(sha256sum -- "$candidate_file" | awk '{print $1}')

printf 'BDYT_REVIEW=COMPLETE\n'
printf 'METHOD=ÆŤ8Ð\n'
printf 'SOURCE_BYTES=%s\n' "$source_bytes"
printf 'SOURCE_SHA256=%s\n' "$source_digest"
printf 'CANDIDATE_BYTES=%s\n' "$candidate_bytes"
printf 'CANDIDATE_SHA256=%s\n' "$candidate_digest"

if cmp -s -- "$source_file" "$candidate_file"; then
  printf 'DECISION=NO_OP\n'
  printf 'COST_OF_NOTHING=NO_WRITE_NO_DELETE_NO_DISPATCH\n'
  printf 'REASON=byte-identical; no adaptation is necessary\n'
  exit 0
fi

printf 'DECISION=DIFFERENT\n'
printf 'COST_OF_NOTHING=REVIEW_ONLY\n'
printf 'REVIEW=DIFF_AVAILABLE\n'
printf 'NOTICE=content differences are not proof of correctness or authorization\n'
printf '%s\n' '--- unified diff (source → candidate) ---'
set +e
diff -u --label source --label candidate -- "$source_file" "$candidate_file"
diff_status=$?
set -e
(( diff_status == 1 || diff_status == 0 )) || fail "diff utility failed"
printf '%s\n' '--- end diff ---'
printf 'ACTION=PROPOSE_ONLY\n'
printf 'MUTATION=NONE\n'
printf 'EXTERNAL_DISPATCH=FALSE\n'
exit 0
