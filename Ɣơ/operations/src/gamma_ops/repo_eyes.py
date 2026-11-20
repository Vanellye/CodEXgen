"""Recursive, read-only repository inventory with onion-layer and commit identity."""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import re
from typing import Any

EXCLUDED_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "env", "node_modules",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".gradle", ".idea", ".tox",
}
SENSITIVE_NAME = re.compile(r"(^|[/_.-])(\.env(?:\.|$)|secrets?|credentials?|private[-_.]?keys?|id_rsa|id_ed25519|keystore|keychain|passwords?)([/_.-]|$)", re.IGNORECASE)
SECRET_PATTERNS = [
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
]
TEXT_SUFFIXES = {".py",".pyi",".kt",".kts",".java",".c",".h",".cc",".cpp",".hpp",".rs",".go",".js",".mjs",".cjs",".ts",".tsx",".jsx",".html",".htm",".css",".scss",".sh",".bash",".zsh",".yml",".yaml",".json",".jsonl",".toml",".ini",".cfg",".conf",".md",".txt",".xml",".gradle",".properties",".sql",".proto",".cmake",".mk",".ps1",".bat",".coddoc",".grsp",".adpt",".graphql"}
BINARY_SUFFIXES = {".so",".a",".o",".obj",".apk",".aab",".dex",".jar",".class",".wasm",".bin",".exe",".dll",".dylib",".png",".jpg",".jpeg",".gif",".webp",".pdf",".zip",".7z",".gz",".sqlite",".db"}
ONION_LAYERS = [
    ("L0", "Repository boundary and identity"),
    ("L1", "Source files and authored assets"),
    ("L2", "Contracts, schemas, manifests and interfaces"),
    ("L3", "Modules, libraries and adapters"),
    ("L4", "Dependencies, workflows and build wiring"),
    ("L5", "Runtime, authorization and capability gates"),
    ("L6", "History, provenance and lineage"),
    ("L7", "Tests, CI evidence and generated reports"),
]

def _layer_ids(relative: str) -> list[str]:
    p=Path(relative); parts={part.lower() for part in p.parts}; layers=["L0"]
    if len(p.parts)==1 or p.suffix.lower() in TEXT_SUFFIXES|BINARY_SUFFIXES: layers.append("L1")
    if any(part in parts for part in {"schema","schemas","contracts","contract","interfaces","manifests","manifest"}) or p.name.lower().endswith(("-schema.json","-contract.json","-manifest.json")): layers.append("L2")
    if any(part in parts for part in {"src","source","lib","libs","modules","module","adapters","adapter","native","app","pantheon"}): layers.append("L3")
    if any(part in parts for part in {".github","workflows","workflow","gradle","scripts","build"}) or p.name.lower() in {"pyproject.toml","package.json","build.gradle","settings.gradle","cmakelists.txt"}: layers.append("L4")
    if any(token in relative.lower() for token in ("runtime","authorization","authorisation","security","gate","executor","permission")): layers.append("L5")
    if any(part in parts for part in {"history","archive","archives","provenance","lineage","events","ledger"}): layers.append("L6")
    if any(part in parts for part in {"tests","test","fixtures","fixture","ci","artifacts","reports","evidence"}): layers.append("L7")
    return list(dict.fromkeys(layers))

def _hash_file(path: Path) -> tuple[str|None,str|None]:
    digest=hashlib.sha256(); tail=b""
    try:
        with path.open("rb") as stream:
            while chunk:=stream.read(1024*1024):
                probe=tail+chunk
                if any(pattern.search(probe) for pattern in SECRET_PATTERNS): return None,"sensitive-content-marker"
                digest.update(chunk); tail=probe[-256:]
        return digest.hexdigest(),None
    except OSError as exc: return None,f"read-error:{type(exc).__name__}"

def scan_repository(root: str|Path, *, max_hash_bytes: int=8*1024*1024,
                    exclude_paths: set[str]|None=None, repository_name: str|None=None,
                    branch: str|None=None, checkout_commit_sha: str|None=None,
                    pull_request_head_sha: str|None=None, base_sha: str|None=None,
                    event_name: str|None=None) -> dict[str,Any]:
    base=Path(root).resolve(strict=True)
    if not base.is_dir(): raise ValueError("repository scan root must be a directory")
    excluded=set(exclude_paths or ()); entries=[]; errors=[]; directory_count=0; stack=[base]
    while stack:
        directory=stack.pop()
        try:
            with os.scandir(directory) as iterator: children=sorted(iterator,key=lambda entry:entry.name.lower(),reverse=True)
        except OSError as exc:
            errors.append({"path":directory.relative_to(base).as_posix() or ".","error":type(exc).__name__}); continue
        for child in children:
            path=Path(child.path); relative=path.relative_to(base).as_posix()
            if relative in excluded: continue
            try:
                if child.is_symlink():
                    entries.append({"path":relative,"kind":"symlink","classification":"RED_HOLD_SYMLINK","size_bytes":None,"sha256":None,"onion_layers":_layer_ids(relative)}); continue
                if child.is_dir(follow_symlinks=False):
                    directory_count+=1
                    if child.name not in EXCLUDED_DIRS: stack.append(path)
                    continue
                if not child.is_file(follow_symlinks=False):
                    entries.append({"path":relative,"kind":"special","classification":"RED_HOLD_SPECIAL_FILE","size_bytes":None,"sha256":None,"onion_layers":_layer_ids(relative)}); continue
                size=child.stat(follow_symlinks=False).st_size
                row={"path":relative,"kind":"file","size_bytes":size,"sha256":None,"onion_layers":_layer_ids(relative)}
                if SENSITIVE_NAME.search(relative): row["classification"]="RED_HOLD_SENSITIVE_NAME"
                elif size>max_hash_bytes: row["classification"]="AMBER_SIZE_LIMIT"
                else:
                    digest,marker=_hash_file(path)
                    if marker=="sensitive-content-marker": row["classification"]="RED_HOLD_SENSITIVE_CONTENT"
                    elif marker: row["classification"]="AMBER_UNREADABLE"; row["detail"]=marker
                    else:
                        row["sha256"]=digest; suffix=path.suffix.lower()
                        if suffix in TEXT_SUFFIXES: row["classification"]="GREEN_READABLE_SOURCE"
                        elif suffix in BINARY_SUFFIXES: row["classification"]="AMBER_BINARY_REVIEW"
                        else: row["classification"]="AMBER_UNKNOWN_FORMAT"
                entries.append(row)
            except OSError as exc: errors.append({"path":relative,"error":type(exc).__name__})
    entries.sort(key=lambda item:item["path"].casefold()); layers=[]
    for layer_id,title in ONION_LAYERS:
        members=[item["path"] for item in entries if layer_id in item["onion_layers"]]
        layers.append({"id":layer_id,"title":title,"file_count":len(members),"paths":members})
    counts={}
    for item in entries:
        key=item["classification"]; counts[key]=counts.get(key,0)+1
    return {
        "format":"ERIA_REPOSITORY_EYES","version":1,"mode":"READ_ONLY_NO_EXECUTION",
        "repository":{"name":repository_name,"branch":branch,"checkout_commit_sha":checkout_commit_sha,
            "pull_request_head_sha":pull_request_head_sha,"base_sha":base_sha,"event_name":event_name,
            "scope":"checked-out working tree only; not all branches or repositories"},
        "root":base.as_posix(),"files_scanned":len(entries),"directories_seen":directory_count,
        "classifications":counts,"layers":layers,"entries":entries,"scan_errors":errors,
        "policy":{"symlinks_followed":False,"file_contents_returned":False,"sensitive_paths_hashed":False,
            "secret_markers_persisted":False,"source_files_executed":False,
            "excluded_directory_names":sorted(EXCLUDED_DIRS),"max_hash_bytes":max_hash_bytes},
    }
