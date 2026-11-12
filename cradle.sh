#!/usr/bin/env bash
# ERIA Cradle: guarded, provider-neutral entry point for the Gradle wrapper.
# Invoke with: bash ./cradle.sh <test|assemble|verify|tasks>
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

readonly GRADLE_WRAPPER="./gradlew"

fail() {
  printf 'CRADLE: BLOCKED: %s\n' "$*" >&2
  exit 2
}

[[ -f "$GRADLE_WRAPPER" ]] || fail "Gradle wrapper not found at $GRADLE_WRAPPER"
[[ -f "gradle/wrapper/gradle-wrapper.properties" ]] || fail "Gradle wrapper properties are missing"
command -v bash >/dev/null 2>&1 || fail "bash is required"

operation="${1:-verify}"
shift || true

# Cradle exposes only reviewed task groups. Arbitrary task injection is rejected.
case "$operation" in
  test)
    [[ "$#" -eq 0 ]] || fail "test accepts no extra arguments"
    set -- :app:testDebugUnitTest
    ;;
  assemble)
    [[ "$#" -eq 0 ]] || fail "assemble accepts no extra arguments"
    set -- :app:assembleDebug
    ;;
  verify)
    [[ "$#" -eq 0 ]] || fail "verify accepts no extra arguments"
    set -- :app:testDebugUnitTest :app:assembleDebug
    ;;
  tasks)
    [[ "$#" -eq 0 ]] || fail "tasks accepts no extra arguments"
    set -- tasks
    ;;
  *)
    fail "unknown operation '$operation'; allowed: test, assemble, verify, tasks"
    ;;
esac

printf 'CRADLE: operation=%s\n' "$operation"
printf 'CRADLE: engine=Gradle Wrapper; external dispatch=disabled\n'
printf 'CRADLE: executing'
printf ' %q' "$@"
printf '\n'

if [[ ! -x "$GRADLE_WRAPPER" ]]; then
  chmod +x "$GRADLE_WRAPPER" || fail "cannot make Gradle wrapper executable"
fi

exec "$GRADLE_WRAPPER" --no-daemon --stacktrace "$@"
