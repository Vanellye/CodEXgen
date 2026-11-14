#!/usr/bin/env python3
"""Local loopback web console for ERIA Æi conversational intelligence."""
from __future__ import annotations
import argparse, json, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
UI = HERE / "eria_aei_interface.html"
sys.path.insert(0, str(HERE))
from eria_aei_conversation import ÆiConversation

MAX_BODY = 16_384

class App:
    def __init__(self, repo):
        self.agent = ÆiConversation(repo)
        self.root = str(self.agent.repository.root)

class Handler(BaseHTTPRequestHandler):
    server_version = "ERIA-AEi-Local/1.0"
    def log_message(self, fmt, *args):
        sys.stderr.write("ERIA Æi HTTP: " + (fmt % args).split("?")[0] + "\n")
    @property
    def app(self):
        return self.server.app
    def send_bytes(self, code, data, mime):
        self.send_response(code)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)
    def send_json(self, code, obj):
        self.send_bytes(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                        "application/json; charset=utf-8")
    def do_GET(self):
        route = urlparse(self.path).path
        if route == "/":
            try:
                self.send_bytes(200, UI.read_bytes(), "text/html; charset=utf-8")
            except OSError:
                self.send_json(404, {"error":"Interface HTML not found"})
        elif route == "/api/status":
            self.send_json(200, {
                "status":"ready", "engine":"ERIA Æi",
                "repository":self.app.root,
                "mode":"read-only deterministic conversation",
                "source_mutation":False, "code_execution":False
            })
        else:
            self.send_json(404, {"error":"Not found"})
    def do_POST(self):
        if urlparse(self.path).path != "/api/chat":
            self.send_json(404, {"error":"Not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > MAX_BODY:
                raise ValueError("Request body missing or too large")
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(body, dict) or not isinstance(body.get("message"), str):
                raise ValueError("Expected JSON with a message string")
            message = body["message"].strip()
            if not message or len(message) > 8000:
                raise ValueError("Message must contain 1–8000 characters")
            result = self.app.agent.respond(message)
            self.send_json(200, result)
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self.send_json(400, {"status":"error","error":str(exc)})
        except Exception as exc:
            self.send_json(500, {"status":"error","error":str(exc)})
    def do_OPTIONS(self):
        self.send_json(405, {"error":"Method not allowed"})

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repository", nargs="?", default=".")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8770)
    args = ap.parse_args()
    if args.host not in ("127.0.0.1", "localhost", "::1"):
        ap.error("Only loopback binding is allowed")
    app = App(args.repository)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.app = app
    print(f"ERIA Æi interface: http://127.0.0.1:{args.port}")
    print(f"Repository: {app.root}")
    print("Loopback only. Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping ERIA Æi.")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
