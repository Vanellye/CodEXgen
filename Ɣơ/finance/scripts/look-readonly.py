#!/usr/bin/env python3
"""Read-only source/binary inventory. Never executes or modifies inventoried files."""
import argparse, hashlib, json, os
from pathlib import Path
TEXT={".py",".c",".cc",".cpp",".h",".hpp",".kt",".java",".rs",".go",".sh",".md",".json",".toml",".yml",".yaml",".xml"}
BINARY={".so",".a",".o",".obj",".dll",".dylib",".exe",".apk",".aab",".bin",".elf"}
SENSITIVE={"keystore",".env","id_rsa","id_ed25519","credentials","secrets"}
def classify(path):
    name=path.name.lower()
    if any(x in name for x in SENSITIVE): return "RED_HOLD_SENSITIVE_NAME"
    if path.is_symlink(): return "RED_HOLD_SYMLINK"
    if path.suffix.lower() in BINARY: return "AMBER_BINARY_REVIEW"
    if path.suffix.lower() in TEXT: return "GREEN_READABLE_SOURCE"
    return "AMBER_UNKNOWN_FORMAT"
def main():
    p=argparse.ArgumentParser()
    p.add_argument("root",type=Path); p.add_argument("--output",type=Path)
    a=p.parse_args(); root=a.root.resolve(strict=True); records=[]
    for current,dirs,names in os.walk(root,followlinks=False):
        dirs[:]=sorted(d for d in dirs if d!=".git" and not (Path(current)/d).is_symlink())
        for name in sorted(names):
            path=Path(current)/name; state=classify(path)
            item={"path":path.relative_to(root).as_posix(),"state":state,"size_bytes":None,"sha256":None}
            if state not in {"RED_HOLD_SENSITIVE_NAME","RED_HOLD_SYMLINK"} and path.is_file():
                item["size_bytes"]=path.stat().st_size; h=hashlib.sha256()
                with path.open("rb") as f:
                    for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
                item["sha256"]=h.hexdigest()
            records.append(item)
    report={"format":"GAMMA_READ_ONLY_INVENTORY","version":1,"root":str(root),"records":records,
            "summary":{s:sum(x["state"]==s for x in records) for s in sorted({x["state"] for x in records})}}
    rendered=json.dumps(report,indent=2,sort_keys=True)
    if a.output: a.output.write_text(rendered+"\n",encoding="utf-8")
    else: print(rendered)
if __name__=="__main__": main()
