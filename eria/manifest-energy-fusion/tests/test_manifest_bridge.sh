#!/usr/bin/env bash
set -euo pipefail

here=$(cd -- "$(dirname -- "$0")" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf -- "$tmp"' EXIT

bash "$here/verify_manifest.sh" "$here/manifest.json" "$here/integrity.sha256" >/dev/null
cp -- "$here/manifest.json" "$tmp/manifest.json"
cp -- "$here/integrity.sha256" "$tmp/integrity.sha256"
python3 - "$tmp/manifest.json" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
p.write_text(p.read_text().replace("proposed-reviewable-artifact", "tampered-artifact"))
PY
if bash "$here/verify_manifest.sh" "$tmp/manifest.json" "$tmp/integrity.sha256" >/dev/null 2>&1; then
  echo "FAIL: tampered manifest was accepted" >&2
  exit 1
fi
if bash "$here/verify_manifest.sh" "$here/manifest.json" "$tmp/missing.sha256" >/dev/null 2>&1; then
  echo "FAIL: missing checksum was accepted" >&2
  exit 1
fi
echo "ERIA Bash bridge tests: PASS (valid, tampered, missing-checksum)"
