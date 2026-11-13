#!/data/data/com.termux/files/usr/bin/bash
# Optional local checkout helper. Does not force-push or merge.
set -euo pipefail
REPO="${1:-$HOME/CodEXgen}"
BRANCH="${ERIA_BRANCH:-feature/eria-resonant-painting-v2}"
REMOTE="${ERIA_REMOTE:-origin}"
cd "$REPO"
git rev-parse --is-inside-work-tree >/dev/null
current="$(git branch --show-current)"
if [[ "$current" == "main" || "$current" == "master" || "$current" == "core" ]]; then
  echo "Refusing to commit from protected branch: $current" >&2; exit 2
fi
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Working tree is not clean; commit or stash unrelated changes first." >&2; exit 3
fi
git add ERIA/ResonantPatternPainting
if ! git diff --cached --quiet; then
  git commit -m "Add ERIA resonant pattern painting v2"
fi
git push -u "$REMOTE" "$BRANCH"
