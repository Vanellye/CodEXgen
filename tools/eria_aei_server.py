#!/usr/bin/env python3
"""Loopback-only HTTP bridge for the read-only Æị inspector."""
from __future__ import annotations
import argparse, json, shlex
from types import SimpleNamespace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from eria_pantheon.aei import AeiError, inspect_file
from eria_pantheon.interface import ERIAPantheonInterface
MAX_BODY=4096
UI_FILE=Path(__file__).resolve().parents[1]/"interfaces"/"aei-interface.html"
def make_handler(repository: Path):
    root=repository.resolve(strict=True)
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
            route=urlparse(self.path).path
            if route=="/api/status":
                self._json(200,{"service":"ERIA Æị","status":"ready","mode":"read-only","conversation":"Âï via Pantheon/PONS","endpoints":["/api/aei/inspect","/api/ai/ask","/api/aei/compile"],"repository":str(root)}); return
            if route in {"/","/aei-interface.html"}:
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
            if route not in {"/api/aei/inspect","/api/ai/ask"}:
                self._json(404,{"status":"HOLD","error":"Not found"}); return
            if self.headers.get("Content-Type","").split(";")[0].strip().lower()!="application/json":
                self._json(415,{"status":"HOLD","error":"Content-Type must be application/json"}); return
            try: length=int(self.headers.get("Content-Length","0"))
            except ValueError:
                self._json(400,{"status":"HOLD","error":"Invalid Content-Length"}); return
            if length<1 or length>MAX_BODY:
                self._json(413,{"status":"HOLD","error":"Request body size is outside the allowed limit"}); return
            try:
                request=json.loads(self.rfile.read(length).decode("utf-8"))
                relative=request.get("path") if isinstance(request,dict) else None
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
                        raise ValueError("Pantheon returned a non-JSON Âï response.")
                else:
                    result=inspect_file(root,relative.strip()).to_dict()
            except (UnicodeDecodeError,json.JSONDecodeError,ValueError,AeiError,OSError) as exc:
                self._json(400,{"translator":"ERIA","status":"HOLD","error":str(exc)}); return
            self._json(200,result.to_dict() if hasattr(result,"to_dict") else result)
        def log_message(self,_format,*_args): return
    return Handler
def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",default=".",help="repository root to inspect")
    parser.add_argument("--port",type=int,default=8765); args=parser.parse_args(argv)
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
