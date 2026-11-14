#!/usr/bin/env python3
"""ERIA-PACT/1: PONS-authorized, declarative change transaction language."""
from __future__ import annotations
import hashlib, json, os, re, shlex, sqlite3, subprocess, urllib.error, urllib.request, uuid
from datetime import datetime, timezone
from pathlib import Path
try:
    from .eria_pantheon.pons import CapabilityGrant, Decision, Pons
except ImportError:
    from eria_pantheon.pons import CapabilityGrant, Decision, Pons

OPS=("APPLY","COMMIT","PUSH","MERGE","DEPLOY")
MAIN={"main","master"}
def now(): return datetime.now(timezone.utc).isoformat()
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def git(root,*args):
    p=subprocess.run(["git","-C",str(root),*args],capture_output=True,text=True,timeout=60)
    if p.returncode: raise RuntimeError("Git operation failed: "+" ".join(args[:2]))
    return p.stdout.strip()

def parse_program(source):
    if not isinstance(source,str) or not source.strip() or len(source.encode())>16000:
        raise ValueError("PACT program must be non-empty and under 16 KiB.")
    commands=[]
    for no,line in enumerate(source.splitlines(),1):
        if not line.strip(): continue
        try: t=shlex.split(line)
        except ValueError as e: raise ValueError(f"PACT line {no}: invalid quoting.") from e
        op=t[0].upper() if t else ""
        if op=="APPLY" and len(t)==3 and t[1].upper()=="PATCH":
            x={"op":"APPLY","patch_grant_id":t[2]}
        elif op=="COMMIT" and len(t)==3 and t[1].upper()=="MESSAGE" and 0<len(t[2])<=160:
            x={"op":"COMMIT","message":t[2]}
        elif op=="PUSH" and len(t)==5 and t[1].upper()=="BRANCH" and t[3].upper()=="EXPECT":
            x={"op":"PUSH","branch":t[2],"expected_remote_sha":t[4]}
        elif op=="MERGE" and len(t)==7 and t[1].upper()=="PR" and t[3].upper()=="METHOD" and t[5].upper()=="EXPECT" and t[4] in {"merge","squash","rebase"} and t[2].isdigit():
            x={"op":"MERGE","pr":int(t[2]),"method":t[4],"expected_head_sha":t[6]}
        elif op=="DEPLOY" and len(t)==5 and t[1].upper()=="WORKFLOW" and t[3].upper()=="REF":
            x={"op":"DEPLOY","workflow":t[2],"ref":t[4]}
        else: raise ValueError(f"PACT line {no}: unsupported syntax; arbitrary commands are forbidden.")
        commands.append(x)
    seq=[x["op"] for x in commands]
    if not seq or seq[0]!="APPLY": raise ValueError("Program must begin APPLY PATCH <grant-id>.")
    if len(seq)!=len(set(seq)) or seq!=sorted(seq,key=OPS.index): raise ValueError("Operations must be unique and ordered APPLY, COMMIT, PUSH, MERGE, DEPLOY.")
    if "PUSH" in seq and "COMMIT" not in seq: raise ValueError("PUSH requires COMMIT.")
    if "MERGE" in seq and "PUSH" not in seq: raise ValueError("MERGE requires PUSH.")
    if "DEPLOY" in seq and "MERGE" not in seq: raise ValueError("DEPLOY requires MERGE.")
    return commands

class PactRuntime:
    def __init__(self, approvals, repository_full_name=None, policy_path=None):
        self.approvals=approvals; self.root=approvals.root.resolve(); self.database=approvals.database
        self.repo=repository_full_name or os.environ.get("ERIA_GITHUB_REPOSITORY","")
        self.policy=Path(policy_path or Path.home()/".eria"/"executor-policy.json")
        with self.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS pact_requests(request_id TEXT PRIMARY KEY,patch_grant_id TEXT NOT NULL,program TEXT NOT NULL,plan_json TEXT NOT NULL,plan_sha256 TEXT NOT NULL,created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS pact_grants(grant_id TEXT PRIMARY KEY,request_id TEXT NOT NULL,plan_sha256 TEXT NOT NULL,capabilities_json TEXT NOT NULL,decision TEXT NOT NULL,approved_at TEXT NOT NULL,confirmation TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS pact_events(event_id TEXT PRIMARY KEY,grant_id TEXT NOT NULL,operation TEXT NOT NULL,outcome TEXT NOT NULL,detail_json TEXT NOT NULL,created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS pact_runs(run_id TEXT PRIMARY KEY,grant_id TEXT NOT NULL UNIQUE,started_at TEXT NOT NULL);
            CREATE TRIGGER IF NOT EXISTS pact_run_u BEFORE UPDATE ON pact_runs BEGIN SELECT RAISE(ABORT,'PACT run claims append-only'); END;
            CREATE TRIGGER IF NOT EXISTS pact_run_d BEFORE DELETE ON pact_runs BEGIN SELECT RAISE(ABORT,'PACT run claims append-only'); END;
            CREATE UNIQUE INDEX IF NOT EXISTS pact_one_grant ON pact_grants(request_id);
            CREATE TRIGGER IF NOT EXISTS pact_req_u BEFORE UPDATE ON pact_requests BEGIN SELECT RAISE(ABORT,'PACT requests append-only'); END;
            CREATE TRIGGER IF NOT EXISTS pact_req_d BEFORE DELETE ON pact_requests BEGIN SELECT RAISE(ABORT,'PACT requests append-only'); END;
            CREATE TRIGGER IF NOT EXISTS pact_grant_u BEFORE UPDATE ON pact_grants BEGIN SELECT RAISE(ABORT,'PACT grants append-only'); END;
            CREATE TRIGGER IF NOT EXISTS pact_grant_d BEFORE DELETE ON pact_grants BEGIN SELECT RAISE(ABORT,'PACT grants append-only'); END;
            CREATE TRIGGER IF NOT EXISTS pact_event_u BEFORE UPDATE ON pact_events BEGIN SELECT RAISE(ABORT,'PACT events append-only'); END;
            CREATE TRIGGER IF NOT EXISTS pact_event_d BEFORE DELETE ON pact_events BEGIN SELECT RAISE(ABORT,'PACT events append-only'); END;
            """)
    def connect(self):
        db=sqlite3.connect(str(self.database),timeout=15); db.row_factory=sqlite3.Row; return db
    def state(self):
        b=git(self.root,"branch","--show-current"); h=git(self.root,"rev-parse","HEAD")
        if not b or not h: raise ValueError("Git branch/HEAD unavailable.")
        return b,h
    def clean(self):
        if git(self.root,"status","--porcelain"): raise ValueError("Working tree/index must be clean.")
    def patch(self,grant_id):
        with self.approvals.connect() as db:
            g=db.execute("SELECT * FROM patch_approval_grants WHERE patch_grant_id=?",(grant_id,)).fetchone()
            if not g: raise ValueError("Approved patch grant not found.")
            r=db.execute("SELECT * FROM patch_approval_requests WHERE patch_request_id=?",(g["patch_request_id"],)).fetchone()
        if not r: raise ValueError("Patch request record missing.")
        return g,r["patch_text"]
    def create_request(self,program):
        commands=parse_program(program); pgid=commands[0]["patch_grant_id"]
        prow,patch_text=self.patch(pgid); verified=self.approvals.verify_patch_grant(pgid,patch_text)
        branch,head=self.state()
        if branch.lower() in MAIN: raise ValueError("main/master writes are prohibited; use a feature branch.")
        self.clean()
        for c in commands:
            if c["op"]=="PUSH":
                if c["branch"]!=branch or c["branch"].lower() in MAIN: raise ValueError("PUSH only permits the current non-main branch.")
                if not re.fullmatch(r"[0-9a-f]{40}",c["expected_remote_sha"]): raise ValueError("PUSH requires full expected remote SHA.")
            if c["op"]=="MERGE" and not re.fullmatch(r"[0-9a-f]{40}",c["expected_head_sha"]): raise ValueError("MERGE requires full PR head SHA.")
            if c["op"]=="DEPLOY" and (not re.fullmatch(r"[A-Za-z0-9_.-]+",c["workflow"]) or c["ref"]!=branch): raise ValueError("Invalid deployment workflow/ref.")
        caps=["repository.patch.apply"]+[{"COMMIT":"git.commit","PUSH":"git.push","MERGE":"github.pull_request.merge","DEPLOY":"github.workflow.dispatch"}[c["op"]] for c in commands[1:]]
        plan={"language":"ERIA-PACT/1","program_sha256":hashlib.sha256(program.encode()).hexdigest(),"repository":str(self.root),"branch":branch,"head":head,
              "patch_grant_id":pgid,"patch_sha256":prow["patch_sha256"],"paths":verified["paths"],
              "commands":commands,"capabilities":caps,
              "limitations":["No arbitrary shell or executable statements","main/master writes and merge targets prohibited",
                "Remote operations require explicit credentials and deployment allowlist",
                "GitHub branch and environment protections remain authoritative"]}
        encoded=canon(plan); digest=hashlib.sha256(encoded.encode()).hexdigest(); rid=str(uuid.uuid4())
        with self.connect() as db: db.execute("INSERT INTO pact_requests VALUES(?,?,?,?,?,?)",(rid,pgid,program,encoded,digest,now()))
        return {"request_id":rid,"plan":plan,"plan_sha256":digest,"confirmation_phrase":"AUTHORIZE EXECUTION "+digest[:12],"status":"HOLD"}
    def approve(self,rid,digest,confirmation):
        with self.connect() as db:
            r=db.execute("SELECT * FROM pact_requests WHERE request_id=?",(rid,)).fetchone()
            prior=db.execute("SELECT grant_id FROM pact_grants WHERE request_id=?",(rid,)).fetchone()
        if not r or prior: raise ValueError("PACT request missing or already approved.")
        actual=hashlib.sha256(r["plan_json"].encode()).hexdigest()
        if actual!=r["plan_sha256"] or digest!=actual: raise ValueError("PACT plan hash mismatch.")
        expected="AUTHORIZE EXECUTION "+actual[:12]
        if confirmation!=expected: raise ValueError("Exact PACT confirmation phrase does not match.")
        plan=json.loads(r["plan_json"]); branch,head=self.state()
        if (branch,head)!=(plan["branch"],plan["head"]): raise ValueError("Branch/HEAD changed; create a new request.")
        pgid=r["patch_grant_id"]; _,patch_text=self.patch(pgid); self.approvals.verify_patch_grant(pgid,patch_text)
        for cap in plan["capabilities"]:
            cg=CapabilityGrant(cap,actual,actual,rid,verified_by_adapter=True)
            if Pons.authorize_source_write(cg,cap,actual) is not Decision.REVIEW_READY: raise ValueError("PONS denied "+cap)
        gid=str(uuid.uuid4())
        with self.connect() as db: db.execute("INSERT INTO pact_grants VALUES(?,?,?,?,?,?,?)",(gid,rid,actual,canon(plan["capabilities"]),"REVIEW_READY",now(),expected))
        return {"grant_id":gid,"decision":"REVIEW_READY","plan_sha256":actual,"capabilities":plan["capabilities"],"executed":False}
    def event(self,gid,op,outcome,detail):
        with self.connect() as db: db.execute("INSERT INTO pact_events VALUES(?,?,?,?,?,?)",(str(uuid.uuid4()),gid,op,outcome,canon(detail),now()))
    def execute(self,gid):
        with self.connect() as db:
            g=db.execute("SELECT * FROM pact_grants WHERE grant_id=?",(gid,)).fetchone()
            r=db.execute("SELECT * FROM pact_requests WHERE request_id=?",(g["request_id"],)).fetchone() if g else None
        if not g or not r or g["decision"]!="REVIEW_READY": raise ValueError("No PACT execution grant.")
        digest=hashlib.sha256(r["plan_json"].encode()).hexdigest()
        if digest!=g["plan_sha256"]: raise ValueError("Approved PACT plan changed.")
        with self.connect() as db:
            prior=db.execute("SELECT run_id FROM pact_runs WHERE grant_id=?",(gid,)).fetchone()
            if prior: raise ValueError("PACT grant is one-shot and has already been consumed.")
            db.execute("INSERT INTO pact_runs VALUES(?,?,?)",(str(uuid.uuid4()),gid,now()))
        p=json.loads(r["plan_json"]); branch,head=self.state()
        if branch.lower() in MAIN or (branch,head)!=(p["branch"],p["head"]): raise ValueError("Branch/HEAD invalidated approval.")
        _,patch_text=self.patch(p["patch_grant_id"]); self.approvals.verify_patch_grant(p["patch_grant_id"],patch_text); self.clean()
        results=[]
        for c in p["commands"]:
            op=c["op"]
            try:
                if op=="APPLY":
                    for args in (["apply","--check","-"],["apply","-"]):
                        q=subprocess.run(["git","-C",str(self.root),*args],input=patch_text,text=True,capture_output=True,timeout=60)
                        if q.returncode: raise RuntimeError("git apply rejected the approved patch.")
                    changed=sorted(filter(None,git(self.root,"diff","--name-only").splitlines()))
                    if changed!=sorted(p["paths"]): raise RuntimeError("Applied patch changed an out-of-scope path.")
                    detail={"paths":changed,"patch_sha256":p["patch_sha256"]}
                elif op=="COMMIT":
                    if git(self.root,"diff","--cached","--name-only"): raise ValueError("Unexpected staged changes.")
                    changed=sorted(filter(None,git(self.root,"diff","--name-only").splitlines()))
                    if changed!=sorted(p["paths"]): raise ValueError("Working diff differs from approved paths.")
                    git(self.root,"add","--",*p["paths"]); git(self.root,"commit","-m",c["message"])
                    detail={"commit":git(self.root,"rev-parse","HEAD"),"paths":p["paths"]}
                elif op=="PUSH":
                    if self.state()[0]!=c["branch"]: raise ValueError("Branch changed before push.")
                    refs=git(self.root,"ls-remote","--heads","origin","refs/heads/"+c["branch"]).split()
                    remote=refs[0] if refs else "0"*40
                    if remote!=c["expected_remote_sha"]: raise ValueError("Remote branch moved; push refused.")
                    git(self.root,"push","origin","HEAD:refs/heads/"+c["branch"])
                    detail={"branch":c["branch"],"previous_remote_sha":remote,"new_head":git(self.root,"rev-parse","HEAD")}
                elif op=="MERGE": detail=self.merge(c,p)
                elif op=="DEPLOY": detail=self.deploy(c,p)
                self.event(gid,op,"SUCCESS",detail); results.append({"operation":op,"status":"SUCCESS","detail":detail})
            except Exception as e:
                self.event(gid,op,"FAILED",{"type":type(e).__name__,"message":str(e)[:300]})
                results.append({"operation":op,"status":"FAILED","error":str(e)[:300]})
                return {"grant_id":gid,"status":"PARTIAL_OR_FAILED","results":results,"automatic_rollback":False}
        return {"grant_id":gid,"status":"COMPLETED","results":results,"automatic_rollback":False}
    def github(self,method,path,payload=None):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",self.repo): raise ValueError("Set ERIA_GITHUB_REPOSITORY=owner/repository.")
        token=os.environ.get("GITHUB_TOKEN","")
        if not token: raise ValueError("GITHUB_TOKEN missing; remote operation refused.")
        data=json.dumps(payload).encode() if payload is not None else None
        req=urllib.request.Request("https://api.github.com/repos/"+self.repo+path,data=data,method=method,
            headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=30) as res: return json.loads(res.read(1048576).decode()) if res.status!=204 else {}
        except urllib.error.HTTPError as e: raise RuntimeError("GitHub returned HTTP "+str(e.code)) from e
    def merge(self,c,p):
        pr=self.github("GET","/pulls/"+str(c["pr"]))
        if pr.get("state")!="open" or pr.get("base",{}).get("ref","").lower() in MAIN: raise ValueError("PR closed or main/master merge target prohibited.")
        if pr.get("head",{}).get("ref")!=p["branch"] or pr.get("head",{}).get("sha")!=c["expected_head_sha"] or c["expected_head_sha"]!=git(self.root,"rev-parse","HEAD"): raise ValueError("PR head does not match approved branch and SHA.")
        result=self.github("PUT","/pulls/"+str(c["pr"])+"/merge",{"merge_method":c["method"],"sha":c["expected_head_sha"]})
        if not result.get("merged"): raise RuntimeError("GitHub did not confirm merge.")
        return {"pr":c["pr"],"merge_sha":result.get("sha"),"base":pr["base"]["ref"]}
    def deploy(self,c,p):
        try: policy=json.loads(self.policy.read_text())
        except (OSError,json.JSONDecodeError): raise ValueError("Deployment disabled; configure ~/.eria/executor-policy.json.")
        if policy.get("allow_deployments") is not True or c["workflow"] not in policy.get("allowed_deployment_workflows",[]): raise ValueError("Workflow is not allowlisted for deployment.")
        if c["ref"]!=p["branch"]: raise ValueError("Deployment ref changed.")
        self.github("POST","/actions/workflows/"+c["workflow"]+"/dispatches",{"ref":c["ref"]})
        return {"workflow":c["workflow"],"ref":c["ref"],"dispatched":True,"environment_protection":"GitHub remains authoritative"}
    def history(self,limit=50):
        with self.connect() as db:
            req=db.execute("SELECT request_id,patch_grant_id,plan_sha256,created_at FROM pact_requests ORDER BY created_at DESC LIMIT ?",(max(1,min(int(limit),200)),)).fetchall()
            grants=db.execute("SELECT grant_id,request_id,plan_sha256,capabilities_json,decision,approved_at FROM pact_grants ORDER BY approved_at DESC LIMIT ?",(max(1,min(int(limit),200)),)).fetchall()
            events=db.execute("SELECT grant_id,operation,outcome,detail_json,created_at FROM pact_events ORDER BY created_at DESC LIMIT ?",(max(1,min(int(limit),500)),)).fetchall()
        return {"requests":[dict(x) for x in req],"grants":[dict(x) for x in grants],"events":[dict(x) for x in events]}
