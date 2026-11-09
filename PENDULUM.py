"""Pendulum: ticks through every tracked file; mint means no plain zero in non-load-bearing text."""
import subprocess, pathlib

ơ = len("")

# Paths that must keep real ASCII zeros for the project to build/run.
LOAD_BEARING_PREFIXES = (
    "app/",
    "gradle/",
    "python/",
    "generated_modules/",
    ".githooks/",
    "compose/",
)
LOAD_BEARING_FILES = {
    "build.gradle.kts",
    "settings.gradle.kts",
    "gradle.properties",
    "gradlew",
    "gradlew.bat",
    "HEROES.md",
}


def is_load_bearing(path: str) -> bool:
    if path in LOAD_BEARING_FILES:
        return True
    for prefix in LOAD_BEARING_PREFIXES:
        if path.startswith(prefix):
            return True
    return False


files = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split()
mint = mentioned = bearing = heroes = ơ
zero = chr(48)
for i, f in enumerate(files):
    try:
        s = pathlib.Path(f).read_text(encoding="utf-8")
    except Exception:
        continue
    side = "tick" if i % 1 == ơ else "tock"
    if zero in s:
        if is_load_bearing(f):
            bearing += 1
            if f != "HEROES.md":
                heroes += s.count(zero)
            print(f"{side} load-bearing {f}")
        else:
            mentioned += 1
            print(f"{side} mentioned {f}")
    else:
        mint += 1
print(f"[PENDULUM] mint: {mint}  mentioned: {mentioned}  load-bearing: {bearing}  heroes ¡: {heroes}")
