#!/usr/bin/env python3
"""Ruble-I v4 IC: inspect local evidence and fail closed without self-approval."""
from __future__ import annotations
import json, os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
V4=ROOT/"ruble-i"/"v4"
def read_json(path):
    with path.open(encoding="utf-8") as stream: return json.load(stream)
def run():
    findings=[]
    def add(name,state,detail): findings.append({"check":name,"state":state,"detail":detail})
    required=[V4/"history-index.json",V4/"allowance-list.json",V4/"allowance.example.json",V4/"reviewer-registry.example.json",V4/"coordinator.py",V4/"crypto_reviewer.py",V4/"adapters.py"]
    missing=[str(p.relative_to(ROOT)) for p in required if not p.is_file()]
    add("source_inventory","FAIL" if missing else "PASS",{"missing":missing})
    try:
        idx=read_json(V4/"history-index.json"); items=read_json(V4/"allowance-list.json")
        add("index_schema","PASS" if idx.get("mode")=="PREPARE_ONLY" and items.get("mode")=="PREPARE_ONLY" else "FAIL",{"history_schema":idx.get("schema"),"allowance_schema":items.get("schema")})
        keep=idx.get("preservation_policy",{})
        add("historical_preservation","PASS" if keep.get("delete_historical_records") is False and keep.get("rewrite_existing_indexes") is False else "FAIL",idx.get("preserved_indexes",[]))
        add("empty_grant_register","PASS" if items.get("entries")==[] else "HOLD",{"entries":len(items.get("entries",[]))})
    except Exception as exc: add("index_parse","FAIL",str(exc))
    try:
        policy=read_json(V4/"allowance.example.json")
        safe=policy.get("mode")=="PREPARE_ONLY" and policy.get("live_submission_enabled") is False and policy.get("configured") is False
        add("policy_scope","PASS" if safe else "FAIL",{"mode":policy.get("mode"),"configured":policy.get("configured"),"live_submission_enabled":policy.get("live_submission_enabled")})
    except Exception as exc: add("policy_scope","FAIL",str(exc))
    try:
        coord=(V4/"coordinator.py").read_text(encoding="utf-8"); crypto=(V4/"crypto_reviewer.py").read_text(encoding="utf-8"); adapters=(V4/"adapters.py").read_text(encoding="utf-8")
        gate=all(x in coord for x in ("verifier is None","verifier(prepared, approval_artifact)","LIVE_SUBMISSION_ENABLED = False","def submit_live_transfer"))
        ed=all(x in crypto for x in ("Ed25519PublicKey","_revoked","intent_sha256","policy_version"))
        off="LiveExecutionDisabled" in adapters and "PREPARE_ONLY" in adapters
        add("authorization_gates","PASS" if gate and ed else "FAIL",{"trusted_verifier_required":gate,"ed25519_scope_and_revocation":ed})
        add("provider_execution_disabled","PASS" if off else "FAIL",{"live_submission_disabled":off})
    except Exception as exc: add("authorization_gates","FAIL",str(exc))
    tests=list((V4/"tests").glob("test_*.py")); marker=Path(os.environ.get("RUBLE_I_TEST_MARKER",str(ROOT/"ruble-i-v4-tests.passed")))
    add("unit_test_results","PASS" if tests and marker.is_file() else "FAIL",{"test_files":len(tests),"test_marker_present":marker.is_file()})
    sha=os.environ.get("GITHUB_SHA",""); ref=os.environ.get("GITHUB_REF",""); event=os.environ.get("GITHUB_EVENT_NAME","")
    add("run_provenance","PASS" if sha and ref and event else "HOLD",{"commit_sha":sha or None,"ref":ref or None,"event":event or None})
    try:
        reg=read_json(V4/"reviewer-registry.example.json"); enrolled=bool(reg.get("reviewers")) and bool(reg.get("governance_signature"))
        add("external_reviewer_enrollment","PASS" if enrolled else "HOLD","No externally signed production registry; enrollment requires independent human governance")
    except Exception as exc: add("external_reviewer_enrollment","HOLD",str(exc))
    states=[f["state"] for f in findings]; decision="FAIL" if "FAIL" in states else ("HOLD" if "HOLD" in states else "PASS")
    report={"schema":"ruble-i.v4.ic-report.v1","decision":decision,"mode":"PREPARE_ONLY","live_submission_enabled":False,"self_approval_permitted":False,"findings":findings}
    out=Path(os.environ.get("RUBLE_I_IC_REPORT",str(ROOT/"ruble-i-v4-ic-report.json")))
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
    return 1 if decision=="FAIL" else 0
if __name__=="__main__": sys.exit(run())
