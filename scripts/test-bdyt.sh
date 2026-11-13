#!/usr/bin/env bash
set -Eeuo pipefail
root=$(mktemp -d)
trap 'rm -rf "$root"' EXIT
printf 'alpha:beta' > "$root/source.txt"
cat > "$root/program.bdyt" <<PROGRAM
ºŌº origin "$root/source.txt"
* origin
+ adapted origin "!"
× combined origin adapted
÷ first second combined ":"
= origin origin
<> origin adapted
/ adapted
----
PROGRAM
before=$(sha256sum "$root/source.txt" | awk '{print $1}')
out=$(bash "$(dirname "$0")/bdyt.sh" "$root/program.bdyt")
after=$(sha256sum "$root/source.txt" | awk '{print $1}')
[[ "$before" == "$after" ]]
grep -q 'ADOPT active=origin' <<<"$out"
grep -q 'ADAPT result=adapted' <<<"$out"
grep -q 'COMPOSE result=combined' <<<"$out"
grep -q 'PARTITION left=first right=second' <<<"$out"
grep -q 'VERIFY=TRUE left=origin right=origin' <<<"$out"
grep -q 'REVIEW=DIFFERENT left=origin right=adapted' <<<"$out"
grep -q 'ROUTE=LOCAL_REPORT name=adapted' <<<"$out"
grep -q 'RECEIPT=COMPLETE mutation=NONE external_dispatch=FALSE' <<<"$out"
cat > "$root/bad.bdyt" <<PROGRAM
* missing
----
PROGRAM
if bash "$(dirname "$0")/bdyt.sh" "$root/bad.bdyt" >/dev/null 2>&1; then
  echo 'expected unknown identifier to fail' >&2; exit 1
fi
printf 'BDYT_TESTS=PASS\n'
