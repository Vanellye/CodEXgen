#!/usr/bin/env python3
"""ERIA Code Aura .glob discovery and PONS-gated new-file bootstrap."""
from __future__ import annotations
import fnmatch, hashlib, json, os, re, sqlite3, subprocess, uuid
from eria_pantheon.pons import CapabilityGrant, Decision, Pons
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

DEFAULT_EXCLUDES={".git",".gradle",".idea",".venv","venv","__pycache__","node_modules","build","dist",".tox",".mypy_cache"}
SENSITIVE=re.compile(r"(?:^|[._-])(secret|credential|token|password|private[_-]?key)(?:[._-]|$)|^\\.env(?:\\.|$)",re.I)
MAX_FILE_BYTES=512*1024
MAX_TOTAL_BYTES=2*1024*1024

def _now(): return datetime.now(timezone.utc).isoformat()
def _canonical(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _safe_rel(v):
    if not isinstance(v,str) or not v or len(v)>500 or "\\" in v or v.startswith("/") or "\x00" in v: raise ValueError("Unsafe repository-relative path.")
    p=PurePosixPath(v)
    if p.is_absolute() or any(x in {"",".",".."} for x in p.parts): raise ValueError("Path traversal is not allowed.")
    return p.as_posix()

class GlobEngine:
    """Deterministic, bounded, read-only repository discovery."""
    def __init__(self,root,excludes=None):
        self.root=Path(root).expanduser().resolve()
        if not self.root.is_dir(): raise ValueError("Repository root must be an existing directory.")
        self.excludes=set(DEFAULT_EXCLUDES)
        for x in excludes or []:
            if not isinstance(x,str) or not x or "/" in x or "\\" in x: raise ValueError("Exclusions must be simple names.")
            self.excludes.add(x)
    @staticmethod
    def validate_patterns(patterns):
        if isinstance(patterns,str): patterns=[patterns]
        if not isinstance(patterns,list) or not 1<=len(patterns)<=32: raise ValueError("Supply 1 to 32 patterns.")
        out=[]
        for p in patterns:
            if not isinstance(p,str) or not p.strip() or len(p)>240: raise ValueError("Patterns must be non-empty and at most 240 characters.")
            p=p.strip()
            if p.startswith("/") or "\\" in p or "\x00" in p or p.startswith("~") or re.match(r"^[A-Za-z]:",p) or ".." in p.split("/"): raise ValueError("Only safe relative POSIX glob patterns are allowed.")
            if p not in out: out.append(p)
        return out
    @staticmethod
    def _matches(rel,pattern):
        return PurePosixPath(rel).match(pattern) or (pattern.startswith("**/") and fnmatch.fnmatchcase(rel,pattern[3:]))
    def scan(self,patterns,*,excludes=None,limit=500):
        patterns=self.validate_patterns(patterns)
        if not isinstance(limit,int) or isinstance(limit,bool) or not 1<=limit<=5000: raise ValueError("limit must be between 1 and 5000.")
        excluded=set(self.excludes)
        for x in excludes or []:
            if not isinstance(x,str) or not x or "/" in x or "\\" in x: raise ValueError("Exclusions must be simple names.")
            excluded.add(x)
        matches=[]; visited=0
        for current,dirs,files in os.walk(self.root,topdown=True,followlinks=False):
            base=Path(current)
            dirs[:]=sorted(x for x in dirs if x not in excluded and not (base/x).is_symlink())
            for name in sorted(files):
                candidate=base/name
                if candidate.is_symlink() or SENSITIVE.search(name): continue
                try:
                    resolved=candidate.resolve(strict=True); rel=resolved.relative_to(self.root).as_posix()
                    stat=candidate.stat(follow_symlinks=False)
                except (OSError,ValueError): continue
                if not candidate.is_file(): continue
                visited+=1
                if any(self._matches(rel,p) for p in patterns):
                    matches.append({"path":rel,"size_bytes":stat.st_size,"modified_at":stat.st_mtime,"extension":candidate.suffix.lower()})
                    if len(matches)>=limit: return {"patterns":patterns,"matches":matches,"count":len(matches),"truncated":True,"visited":visited,"read_only":True}
        matches.sort(key=lambda x:x["path"])
        return {"patterns":patterns,"matches":matches,"count":len(matches),"truncated":False,"visited":visited,"read_only":True}

class GlobBootstrap:
    """One-shot approval for creating exact, previously absent text files."""
    CAPABILITY="repository.new_file.create"
    def __init__(self,root,database):
        self.root=Path(root).expanduser().resolve(); self.database=Path(database).expanduser().resolve()
        self.database.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS requests(request_id TEXT PRIMARY KEY,scope_json TEXT NOT NULL,scope_sha256 TEXT NOT NULL,files_json TEXT NOT NULL,created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS grants(grant_id TEXT PRIMARY KEY,request_id TEXT NOT NULL UNIQUE,scope_sha256 TEXT NOT NULL,decision TEXT NOT NULL,approved_at TEXT NOT NULL,confirmation TEXT NOT NULL,consumed_at TEXT);
            CREATE TRIGGER IF NOT EXISTS requests_no_update BEFORE UPDATE ON requests BEGIN SELECT RAISE(ABORT,'bootstrap requests are append-only'); END;
            CREATE TRIGGER IF NOT EXISTS requests_no_delete BEFORE DELETE ON requests BEGIN SELECT RAISE(ABORT,'bootstrap requests are append-only'); END;
            """)
    def connect(self):
        db=sqlite3.connect(str(self.database),timeout=15); db.row_factory=sqlite3.Row; return db
    def _git(self,*args):
        return subprocess.run(["git","-C",str(self.root),*args],check=True,capture_output=True,text=True,timeout=8).stdout.strip()
    def _provenance(self):
        branch=self._git("rev-parse","--abbrev-ref","HEAD")
        if branch in {"main","master"}: raise ValueError("Bootstrap creation is prohibited on main/master.")
        return {"repository":str(self.root),"branch":branch,"head_commit":self._git("rev-parse","HEAD")}
    def _validate_files(self,files):
        if not isinstance(files,list) or not 1<=len(files)<=20: raise ValueError("Request must contain 1 to 20 new files.")
        result=[]; total=0; seen=set()
        for item in files:
            if not isinstance(item,dict): raise ValueError("Each file requires path and content.")
            rel=_safe_rel(item.get("path")); content=item.get("content")
            if not isinstance(content,str) or "\x00" in content: raise ValueError("Only UTF-8 text files are eligible.")
            raw=content.encode("utf-8"); total+=len(raw)
            if len(raw)>MAX_FILE_BYTES or total>MAX_TOTAL_BYTES: raise ValueError("Bootstrap size limit exceeded.")
            if rel in seen: raise ValueError("Duplicate target path.")
            seen.add(rel); target=self.root/rel
            if self.root not in target.resolve(strict=False).parents: raise ValueError("Target escapes repository.")
            if target.exists() or target.is_symlink(): raise ValueError("Bootstrap may create new files only; target exists: "+rel)
            if SENSITIVE.search(Path(rel).name): raise ValueError("Sensitive-looking filenames are not eligible.")
            result.append({"path":rel,"content":content,"sha256":hashlib.sha256(raw).hexdigest()})
        return sorted(result,key=lambda x:x["path"])
    def create_request(self,files,purpose):
        if not isinstance(purpose,str) or not purpose.strip() or len(purpose)>500: raise ValueError("Bootstrap purpose is required.")
        items=self._validate_files(files); provenance=self._provenance()
        scope={"capability":self.CAPABILITY,**provenance,"purpose":purpose.strip(),"files":[{"path":x["path"],"sha256":x["sha256"]} for x in items],"limits":["create-only; no overwrite or delete","no execution","no Git staging, commit, push, merge or deployment","one-time grant; exact paths and content hashes only"]}
        digest=hashlib.sha256(_canonical(scope).encode()).hexdigest(); rid=str(uuid.uuid4())
        with self.connect() as db: db.execute("INSERT INTO requests VALUES(?,?,?,?,?)",(rid,_canonical(scope),digest,_canonical(items),_now()))
        return {"request_id":rid,"scope":scope,"scope_sha256":digest,"confirmation_phrase":"AUTHORIZE NEW FILES "+digest[:12],"status":"HOLD"}
    def approve(self,rid,digest,confirmation):
        with self.connect() as db:
            row=db.execute("SELECT * FROM requests WHERE request_id=?",(rid,)).fetchone()
            prior=db.execute("SELECT grant_id FROM grants WHERE request_id=?",(rid,)).fetchone()
        if not row or prior: raise ValueError("Unknown request or grant already exists.")
        if row["scope_sha256"]!=digest: raise ValueError("Bootstrap scope hash mismatch.")
        expected="AUTHORIZE NEW FILES "+digest[:12]
        if not isinstance(confirmation,str) or confirmation.strip()!=expected: raise ValueError("Exact new-file confirmation phrase does not match.")
        scope=json.loads(row["scope_json"])
        if self._provenance()!={k:scope[k] for k in ("repository","branch","head_commit")}: raise ValueError("Repository, branch, or HEAD changed; recreate request.")
        self._validate_files(json.loads(row["files_json"]))
        capability=CapabilityGrant(self.CAPABILITY,digest,digest,rid,verified_by_adapter=True)
        decision=Pons.authorize_source_write(capability,self.CAPABILITY,digest)
        if decision is not Decision.REVIEW_READY: raise ValueError("PONS denied new-file bootstrap; request remains HOLD.")
        gid=str(uuid.uuid4())
        with self.connect() as db: db.execute("INSERT INTO grants(grant_id,request_id,scope_sha256,decision,approved_at,confirmation) VALUES(?,?,?,?,?,?)",(gid,rid,digest,decision.value,_now(),expected))
        return {"grant_id":gid,"decision":"REVIEW_READY","scope_sha256":digest,"source_modified":False,"execution_started":False}
    def apply(self,gid):
        with self.connect() as db:
            grant=db.execute("SELECT * FROM grants WHERE grant_id=?",(gid,)).fetchone()
            if not grant or grant["decision"]!="REVIEW_READY" or grant["consumed_at"]: raise ValueError("No unused approved bootstrap grant; PONS HOLD.")
            req=db.execute("SELECT * FROM requests WHERE request_id=?",(grant["request_id"],)).fetchone()
        scope=json.loads(req["scope_json"]); items=json.loads(req["files_json"])
        if grant["scope_sha256"]!=req["scope_sha256"] or hashlib.sha256(_canonical(scope).encode()).hexdigest()!=grant["scope_sha256"]: raise ValueError("Bootstrap scope integrity check failed.")
        if self._provenance()!={k:scope[k] for k in ("repository","branch","head_commit")}: raise ValueError("Repository, branch, or HEAD changed after approval.")
        self._validate_files(items); created=[]
        for item in items:
            target=self.root/item["path"]; target.parent.mkdir(parents=True,exist_ok=True)
            fd=os.open(str(target),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,"w",encoding="utf-8",newline="") as stream:
                stream.write(item["content"]); stream.flush(); os.fsync(stream.fileno())
            created.append(item["path"])
        with self.connect() as db: db.execute("UPDATE grants SET consumed_at=? WHERE grant_id=? AND consumed_at IS NULL",(_now(),gid))
        return {"status":"CREATED","paths":created,"grant_id":gid,"git_staged":False,"committed":False,"source_records_modified":False}
    def history(self):
        with self.connect() as db:
            req=[dict(x) for x in db.execute("SELECT request_id,scope_sha256,created_at FROM requests ORDER BY created_at DESC LIMIT 100")]
            grants=[dict(x) for x in db.execute("SELECT grant_id,request_id,scope_sha256,decision,approved_at,consumed_at FROM grants ORDER BY approved_at DESC LIMIT 100")]
        return {"requests":req,"grants":grants}
