#!/usr/bin/env python3
"""Loopback-only HTTP bridge for the read-only Æị inspector."""
from __future__ import annotations
import argparse, json, shlex
from types import SimpleNamespace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from eria_pantheon.aei import AeiError, inspect_file
from eria_pantheon.interface import ERIAPantheonInterface
from eria_pantheon.resonance import synthesize_tone, InboxMonitor, load_config, ResonanceHold
from eria_pantheon.approval import verify_signed_grant, ApprovalError
from eria_pantheon.relay_lifecycle import RelayLifecycle
from eria_pantheon.patch_executor import execute_exact_patch, PatchHold
import os, threading
REMOTE_APPROVAL_LOCK=threading.Lock()
MAX_BODY=4096
UI_FILE=Path(__file__).resolve().parents[1]/"interfaces"/"aei-interface.html"
def make_handler(repository: Path):
    root=repository.resolve(strict=True)
    inbox_monitor=InboxMonitor(root)
    relay_lifecycle=RelayLifecycle(root,inbox_monitor)
    class Handler(BaseHTTPRequestHandler):
        server_version="ERIA-AEI/0.1"
        def _local_host(self):
            allowed = {
                f"127.0.0.1:{self.server.server_port}",
                f"localhost:{self.server.server_port}",
            }
            return self.headers.get("Host", "").lower() in allowed
        def _json(self,status,payload):
            data=json.dumps(payload,ensure_ascii=False).encode("utf-8")
            self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8")
            self.send_header("Content-Length",str(len(data))); self.send_header("Cache-Control","no-store")
            self.end_headers(); self.wfile.write(data)
        def do_GET(self):
            if not self._local_host():
                self._json(403,{"status":"HOLD","error":"Host header is not a permitted loopback host"}); return
            parsed=urlparse(self.path)
            route=parsed.path
            if route=="/api/resonance/tone":
                try:
                    query=parse_qs(parsed.query)
                    frequency=float(query.get("frequency",["440"])[0])
                    duration=float(query.get("duration",["1"])[0])
                    volume=float(query.get("volume",["25"])[0])
                    payload=synthesize_tone(frequency,duration,volume)
                except (ValueError, TypeError) as exc:
                    self._json(400,{"status":"HOLD","error":str(exc)}); return
                self.send_response(200); self.send_header("Content-Type","audio/wav")
                self.send_header("Content-Length",str(len(payload))); self.send_header("Cache-Control","no-store")
                self.end_headers(); self.wfile.write(payload); return
            if route=="/api/acquisition/status":
                self._json(200,inbox_monitor.status()); return
            if route=="/api/status":
                self._json(200,{"service":"ERIA Æị","status":"ready","mode":"source-read-only; derived-storage-enabled","conversation":"Âï via Pantheon/PONS","acquisition":inbox_monitor.status(),"endpoints":["/api/aei/inspect","/api/ai/ask","/api/aei/compile","/api/acquisition/start","/api/acquisition/pause","/api/acquisition/status","/api/resonance/tone","/api/pons/relay/start","/api/pons/relay/stop","/api/pons/relay/status","/api/pons/execute-patch"],"relay":relay_lifecycle.status(),"repository":str(root)}); return
            if route in {"/","/portal","/resonance-portal"}:
                portal_file=Path(__file__).resolve().parents[1]/"interfaces"/"eria-resonance-portal.html"
                try: page=portal_file.read_bytes()
                except OSError:
                    self._json(500,{"status":"HOLD","error":"ERIA Resonance Portal unavailable"}); return
                self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8")
                self.send_header("Content-Length",str(len(page))); self.send_header("Cache-Control","no-store")
                self.end_headers(); self.wfile.write(page); return
            if route=="/aei-interface.html":
                try: page=UI_FILE.read_bytes()
                except OSError:
                    self._json(500,{"status":"HOLD","error":"Æị interface file unavailable"}); return
                self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8")
                self.send_header("Content-Length",str(len(page))); self.send_header("Cache-Control","no-store")
                self.end_headers(); self.wfile.write(page); return
            self._json(404,{"status":"HOLD","error":"Not found"})
        def do_POST(self):
            if not self._local_host():
                self._json(403,{"status":"HOLD","error":"Host header is not a permitted loopback host"}); return
            origin=self.headers.get("Origin")
            allowed_origins={f"http://127.0.0.1:{self.server.server_port}",f"http://localhost:{self.server.server_port}"}
            if origin and origin not in allowed_origins:
                self._json(403,{"status":"HOLD","error":"Cross-origin requests are not permitted"}); return
            route=urlparse(self.path).path
            if route not in {"/api/aei/inspect","/api/ai/ask","/api/aei/compile","/api/acquisition/start","/api/acquisition/pause","/api/pons/remote-approve","/api/pons/relay/start","/api/pons/relay/stop","/api/pons/execute-patch"}:
                self._json(404,{"status":"HOLD","error":"Not found"}); return
            if self.headers.get("Content-Type","").split(";")[0].strip().lower()!="application/json":
                self._json(415,{"status":"HOLD","error":"Content-Type must be application/json"}); return
            try: length=int(self.headers.get("Content-Length","0"))
            except ValueError:
                self._json(400,{"status":"HOLD","error":"Invalid Content-Length"}); return
            if length<1 or length>1_100_000:
                self._json(413,{"status":"HOLD","error":"Request body size is outside the allowed limit"}); return
            try:
                request=json.loads(self.rfile.read(length).decode("utf-8"))
                if not isinstance(request,dict): raise ValueError("JSON object required.")
                if route=="/api/pons/relay/start":\n                    self._json(200,relay_lifecycle.start()); return\n                if route=="/api/pons/relay/stop":\n                    self._json(200,relay_lifecycle.stop()); return\n                if route=="/api/pons/execute-patch":\n                    result=execute_exact_patch(root,relative_path=request.get("path"),\n                        replacement=request.get("replacement"),grant=request.get("grant"),\n                        signing_key=os.environ.get("ERIA_PONS_APPROVAL_KEY",""))\n                    self._json(200,result); return\n                if route=="/api/pons/remote-approve":
                    key=os.environ.get("ERIA_PONS_APPROVAL_KEY","")
                    grant=verify_signed_grant(request.get("grant"),key,
                        capability="eria.acquire",scope="storage/inbox/")
                    approval_dir=root/"storage"/"approvals"
                    if approval_dir.is_symlink():
                        raise ApprovalError("Approval ledger directory cannot be a symlink.")
                    approval_dir.mkdir(parents=True,exist_ok=True)
                    if root not in approval_dir.resolve(strict=True).parents:
                        raise ApprovalError("Approval ledger path escapes repository.")
                    ledger=approval_dir/"consumed-grants.jsonl"
                    with REMOTE_APPROVAL_LOCK:
                        if ledger.exists():
                            for line in ledger.read_text(encoding="utf-8").splitlines():
                                try:
                                    if json.loads(line).get("grant_id")==grant["grant_id"]:
                                        raise ApprovalError("PONS grant has already been consumed.")
                                except json.JSONDecodeError:
                                    raise ApprovalError("Approval ledger is malformed; remote approval held.")
                        record={"grant_id":grant["grant_id"],"capability":grant["capability"],
                            "scope":grant["scope"],"consumed_at":__import__("datetime").datetime.now(
                            __import__("datetime").timezone.utc).isoformat(),"status":"verified"}
                        fd=os.open(ledger,os.O_WRONLY|os.O_CREAT|os.O_APPEND|getattr(os,"O_NOFOLLOW",0),0o600)
                        with os.fdopen(fd,"a",encoding="utf-8") as stream:
                            stream.write(json.dumps(record,sort_keys=True)+"\\n")
                            stream.flush()
                            os.fsync(stream.fileno())
                    settings=root/"storage"/"settings.json"
                    config=load_config(root)
                    config["automatic_capture"]["enabled"]=True
                    config["automatic_capture"]["approval_reference"]="pons:"+grant["grant_id"]
                    temp=settings.with_suffix(".json.tmp")
                    temp.write_text(json.dumps(config,indent=2)+"\\n",encoding="utf-8")
                    os.replace(temp,settings)
                    status=inbox_monitor.start("pons:"+grant["grant_id"])
                    self._json(200,{"approval":"VERIFIED","grant_id":grant["grant_id"],
                        "capability":grant["capability"],"scope":grant["scope"],
                        "monitor":status,"status":"RUNNING" if status.get("state")=="running" else "HOLD"})
                    return
                if route=="/api/acquisition/start":
                    reference=request.get("approval_reference")
                    if not isinstance(reference,str) or not reference.strip(): raise ResonanceHold("Explicit approval reference required.")
                    settings=root/"storage"/"settings.json"
                    config=load_config(root)
                    config["automatic_capture"]["enabled"]=True
                    config["automatic_capture"]["approval_reference"]=reference.strip()
                    temp=settings.with_suffix(".json.tmp")
                    temp.write_text(json.dumps(config,indent=2)+"\n",encoding="utf-8")
                    os.replace(temp,settings)
                    self._json(200,inbox_monitor.start(reference)); return
                if route=="/api/acquisition/pause":
                    result=inbox_monitor.pause()
                    settings=root/"storage"/"settings.json"
                    config=load_config(root)
                    config["automatic_capture"]["enabled"]=False
                    temp=settings.with_suffix(".json.tmp")
                    temp.write_text(json.dumps(config,indent=2)+"\n",encoding="utf-8")
                    os.replace(temp,settings)
                    self._json(200,result); return
                relative=request.get("path")
                if not isinstance(relative,str) or not relative.strip(): raise ValueError("Provide a repository-relative path.")
                if route in {"/api/ai/ask","/api/aei/compile"}:
                    adapter=ERIAPantheonInterface(SimpleNamespace(root=root))
                    if route=="/api/ai/ask":
                        question=request.get("question")
                        if not isinstance(question,str): raise ValueError("Provide a question for Âï.")
                        command="ai.ask "+shlex.join([relative.strip(),"--question",question])
                    else:
                        command="aei.compile "+shlex.quote(relative.strip())
                    response=adapter.handle(command)
                    try:
                        result=json.loads(response)
                    except json.JSONDecodeError:
                        raise ValueError("Pantheon returned a non-JSON response.")
                else:
                    result=inspect_file(root,relative.strip()).to_dict()
            except (UnicodeDecodeError,json.JSONDecodeError,ValueError,AeiError,ResonanceHold,ApprovalError,PatchHold,OSError,RuntimeError) as exc:
                self._json(400,{"translator":"ERIA","status":"HOLD","error":str(exc)}); return
            self._json(200,result.to_dict() if hasattr(result,"to_dict") else result)
        def log_message(self,_format,*_args): return
    return Handler
def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",default=".",help="repository root to inspect")
    parser.add_argument("--port",type=int,default=8970); args=parser.parse_args(argv)
    if not 1024<=args.port<=65535: parser.error("--port must be between 1024 and 65535")
    root=Path(args.root).expanduser().resolve(strict=True)
    if not root.is_dir(): parser.error("--root must be a directory")
    server=ThreadingHTTPServer(("127.0.0.1",args.port),make_handler(root))
    print(f"Æị local interface: http://127.0.0.1:{args.port}/")
    print(f"Repository root: {root}"); print("Loopback only · read-only · press Ctrl+C to stop")
    try: server.serve_forever()
    except KeyboardInterrupt: print("\nÆị stopped.")
    finally: server.server_close()
    return 0
if __name__=="__main__": raise SystemExit(main())
