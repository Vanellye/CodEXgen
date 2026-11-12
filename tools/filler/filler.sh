#!/usr/bin/env bash
# ERIA FILLER — plan missing repository structures; create only mapped files.
# Default is read-only. Apply requires an explicit branch-bound approval token.
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

readonly MANIFEST="tools/filler/filler.manifest"
readonly LEDGER=".eria/filler/ledger.tsv"
readonly TARGET_BRANCH="feature/ashes-to-angels-pheonix"
readonly APPROVAL_TOKEN="ERIA-FILLER-APPROVED"

mode="plan"
approval=""
while (($#)); do
  case "$1" in
    --plan) mode="plan"; shift ;;
    --apply) mode="apply"; shift ;;
    --approve)
      (($# >= 2)) || { printf 'FILLER: --approve requires a branch name\n' >&2; exit 2; }
      approval="$2"; shift 2 ;;
    -h|--help)
      printf 'Usage: bash tools/filler/filler.sh [--plan | --apply --approve %s]\n' "$TARGET_BRANCH"
      exit 0 ;;
    *) printf 'FILLER: unknown argument: %s\n' "$1" >&2; exit 2 ;;
  esac
done

[[ -f "$MANIFEST" && ! -L "$MANIFEST" ]] || {
  printf 'FILLER: blocked: manifest missing or is a symlink\n' >&2; exit 2;
}

if [[ "$mode" == "apply" ]]; then
  [[ "$approval" == "$TARGET_BRANCH" ]] || {
    printf 'FILLER: blocked: explicit approval must name %s\n' "$TARGET_BRANCH" >&2; exit 3;
  }
  current_branch="$(git branch --show-current 2>/dev/null || true)"
  [[ "$current_branch" == "$TARGET_BRANCH" ]] || {
    printf 'FILLER: blocked: expected branch %s; found %s\n' "$TARGET_BRANCH" "${current_branch:-detached}" >&2
    exit 3
  }
fi

valid_repo_path() {
  local value="$1"
  [[ -n "$value" && "$value" != /* && "$value" != "." ]] || return 1
  case "/$value/" in
    *"/../"*|*"/./"*) return 1 ;;
  esac
  return 0
}

planned=0
created=0
skipped=0
blocked=0

printf 'FILLER: mode=%s branch=%s\n' "$mode" "$(git branch --show-current 2>/dev/null || printf 'unknown')"
printf 'FILLER: source files are immutable; no deletion, replacement, merge, push, or dispatch\n'

while IFS=$'\t' read -r target template || [[ -n "${target:-}" ]]; do
  [[ -z "${target:-}" || "$target" == #* ]] && continue
  if ! valid_repo_path "$target" || ! valid_repo_path "$template"; then
    printf 'FILLER: BLOCKED invalid path mapping: %s -> %s\n' "${target:-}" "${template:-}"
    ((blocked+=1)); continue
  fi
  if [[ ! -f "$template" || -L "$template" ]]; then
    printf 'FILLER: BLOCKED template missing or not a regular file: %s\n' "$template"
    ((blocked+=1)); continue
  fi
  if [[ -e "$target" || -L "$target" ]]; then
    printf 'FILLER: PRESERVED existing target: %s\n' "$target"
    ((skipped+=1)); continue
  fi

  source_hash="$(sha256sum "$template" | awk '{print $1}')"
  printf 'FILLER: MISSING %s <= %s sha256=%s\n' "$target" "$template" "$source_hash"
  ((planned+=1))

  if [[ "$mode" == "apply" ]]; then
    mkdir -p -- "$(dirname -- "$target")"
    # Re-check immediately before writing; never overwrite a racing/existing path.
    if [[ -e "$target" || -L "$target" ]]; then
      printf 'FILLER: PRESERVED target appeared during apply: %s\n' "$target"
      ((skipped+=1)); continue
    fi
    install -m 0644 -- "$template" "$target"
    mkdir -p -- "$(dirname -- "$LEDGER")"
    printf '%s\t%s\t%s\t%s\n' "$target" "$template" "$source_hash" "$TARGET_BRANCH" >> "$LEDGER"
    printf 'FILLER: CREATED %s\n' "$target"
    ((created+=1))
  fi
done < "$MANIFEST"

printf 'FILLER: planned=%d created=%d preserved=%d blocked=%d\n' "$planned" "$created" "$skipped" "$blocked"
if ((blocked > 0)); then exit 4; fi
