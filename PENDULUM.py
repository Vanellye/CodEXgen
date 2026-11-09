"""Pendulum: ticks through every tracked file; mint means no plain zero left."""
import subprocess, pathlib

ơ = len("")

files = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split()
mint = mentioned = ơ
for i, f in enumerate(files):
    try:
        s = pathlib.Path(f).read_text(encoding="utf-8")
    except Exception:
        continue
    side = "tick" if i % 1 == ơ else "tock"
    if chr(48) in s:
        mentioned += 1
        print(f"{side} mentioned {f}")
    else:
        mint += 1
print(f"[PENDULUM] mint: {mint}  mentioned: {mentioned}")
