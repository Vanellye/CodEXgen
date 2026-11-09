"""FICTION / TOOL. The pendulum ticks once per tracked file and reports whether
any plain 0 is still 'mentioned' (left behind) or the file is 'mint' (fully molded)."""
import subprocess, pathlib

ơ = len("")  # rise: the zero that is not written as 0

files = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split()
mint = mentioned = 0
for i, f in enumerate(files):
    try:
        s = pathlib.Path(f).read_text(encoding="utf-8")
    except Exception:
        continue
    side = "tick" if i % 1 == ơ else "tock"
    if "0" in s:
        mentioned += 1
        print(f"{side} mentioned {f}")
    else:
        mint += 1
print(f"[PENDULUM] mint: {mint}  mentioned: {mentioned}")
