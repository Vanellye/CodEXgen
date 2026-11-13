#!/usr/bin/env bash
# bđyt v0.1 — bounded text-language interpreter. No eval, shell expansion, or dispatch.
set -Eeuo pipefail
IFS=$'\n\t'

fail() { printf 'BDYT_ERROR line=%s reason=%s\n' "${line_no:-0}" "$1" >&2; exit 2; }
[[ $# -eq 1 && -f "$1" && ! -L "$1" ]] || { echo 'usage: bash scripts/bdyt.sh PROGRAM.bdyt' >&2; exit 2; }
program=$1
[[ -r "$program" ]] || fail 'program is not readable'

declare -A values=() origins=() digests=()
active=''
line_no=0
ended=0

while IFS= read -r line || [[ -n "$line" ]]; do
  ((line_no+=1))
  line=${line%$'\r'}
  [[ -z "${line//[[:space:]]/}" || "$line" =~ ^[[:space:]]*# ]] && continue
  [[ $ended -eq 0 ]] || fail 'content after ---- boundary'

  if [[ "$line" =~ ^[[:space:]]*ºŌº[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]+\"([^\"]+)\"[[:space:]]*$ ]]; then
    id=${BASH_REMATCH[1]}; path=${BASH_REMATCH[2]}
    [[ ! ${values[$id]+yes} ]] || fail "origin id '$id' already exists"
    [[ -f "$path" && ! -L "$path" && -r "$path" ]] || fail "origin '$path' must be a readable regular non-symlink file"
    size=$(wc -c < "$path"); size=${size//[[:space:]]/}
    (( size <= 1048576 )) || fail 'origin exceeds 1 MiB text input limit'
    text_size=$(LC_ALL=C tr -d '\\000' < "$path" | wc -c); text_size=${text_size//[[:space:]]/}
    [[ "$text_size" == "$size" ]] || fail 'NUL/binary input is not supported'
    values[$id]=$(cat -- "$path")
    origins[$id]=$path
    digests[$id]=$(sha256sum -- "$path" | awk '{print $1}')
    printf 'ORIGIN id=%s bytes=%s sha256=%s\n' "$id" "$size" "${digests[$id]}"
  elif [[ "$line" =~ ^[[:space:]]*\*[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*$ ]]; then
    id=${BASH_REMATCH[1]}; [[ ${values[$id]+yes} ]] || fail "unknown value '$id'"
    active=$id; printf 'ADOPT active=%s\n' "$active"
  elif [[ "$line" =~ ^[[:space:]]*\+[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]+\"([^\"]*)\"[[:space:]]*$ ]]; then
    out=${BASH_REMATCH[1]}; src=${BASH_REMATCH[2]}; suffix=${BASH_REMATCH[3]}
    [[ ! ${values[$out]+yes} ]] || fail "destination '$out' already exists; adaptation is append-only"
    [[ ${values[$src]+yes} ]] || fail "unknown source '$src'"
    [[ "$active" == "$src" ]] || fail "source '$src' must be adopted with * before adaptation"
    values[$out]="${values[$src]}$suffix"; printf 'ADAPT result=%s from=%s\n' "$out" "$src"
  elif [[ "$line" =~ ^[[:space:]]*×[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*$ ]]; then
    out=${BASH_REMATCH[1]}; left=${BASH_REMATCH[2]}; right=${BASH_REMATCH[3]}
    [[ ! ${values[$out]+yes} ]] || fail "destination '$out' already exists"
    [[ ${values[$left]+yes} && ${values[$right]+yes} ]] || fail 'compose operands must exist'
    values[$out]="${values[$left]}${values[$right]}"; printf 'COMPOSE result=%s left=%s right=%s\n' "$out" "$left" "$right"
  elif [[ "$line" =~ ^[[:space:]]*÷[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]+\"([^\"]+)\"[[:space:]]*$ ]]; then
    left=${BASH_REMATCH[1]}; right=${BASH_REMATCH[2]}; src=${BASH_REMATCH[3]}; sep=${BASH_REMATCH[4]}
    [[ ! ${values[$left]+yes} && ! ${values[$right]+yes} ]] || fail 'partition destinations must be new'
    [[ ${values[$src]+yes} ]] || fail "unknown partition source '$src'"
    content=${values[$src]}; [[ "$content" == *"$sep"* ]] || fail 'partition delimiter not found'
    values[$left]=${content%%"$sep"*}; values[$right]=${content#*"$sep"}; printf 'PARTITION left=%s right=%s source=%s\n' "$left" "$right" "$src"
  elif [[ "$line" =~ ^[[:space:]]*=[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*$ ]]; then
    left=${BASH_REMATCH[1]}; right=${BASH_REMATCH[2]}
    [[ ${values[$left]+yes} && ${values[$right]+yes} ]] || fail 'equality operands must exist'
    if [[ "${values[$left]}" == "${values[$right]}" ]]; then printf 'VERIFY=TRUE left=%s right=%s\n' "$left" "$right"; else printf 'VERIFY=FALSE left=%s right=%s\n' "$left" "$right"; fi
  elif [[ "$line" =~ ^[[:space:]]*\<\>[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*$ ]]; then
    left=${BASH_REMATCH[1]}; right=${BASH_REMATCH[2]}
    [[ ${values[$left]+yes} && ${values[$right]+yes} ]] || fail 'review operands must exist'
    if [[ "${values[$left]}" == "${values[$right]}" ]]; then printf 'REVIEW=IDENTICAL left=%s right=%s\n' "$left" "$right"; else printf 'REVIEW=DIFFERENT left=%s right=%s\n' "$left" "$right"; fi
  elif [[ "$line" =~ ^[[:space:]]*/[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*$ ]]; then
    id=${BASH_REMATCH[1]}; [[ ${values[$id]+yes} ]] || fail "unknown route value '$id'"
    printf 'ROUTE=LOCAL_REPORT name=%s\n' "$id"
    printf '%s\n' "${values[$id]}"
  elif [[ "$line" =~ ^[[:space:]]*----[[:space:]]*$ ]]; then
    ended=1; printf 'RECEIPT=COMPLETE mutation=NONE external_dispatch=FALSE\n'
  else
    fail 'invalid syntax or unsupported operator form'
  fi
done < "$program"
(( ended == 1 )) || fail 'missing ---- execution boundary'
