#!/usr/bin/env python3
"""Æị standalone web host and same-origin ERIA API reverse proxy."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent / "www"
API_ORIGIN = os.environ.get("ERIA_API_ORIGIN", "http://127.0.0.1:8778").rstrip("/")
HOST = os.environ.get("AIE_HOST", "127.0.0.1")
PORT = int(os.environ.get("AIE_PORT", "8780"))

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self.proxy()
        if self.path in ("/", "/index.html"):
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            return self.proxy()
        self.send_error(404, "Only /api/* POST routes are proxied")

    def proxy(self):
        path = self.path
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else None
        headers = {"Content-Type": self.headers.get("Content-Type", "application/json")}
        req = Request(API_ORIGIN + path, data=body, headers=headers,
                      method=self.command)
        try:
            with urlopen(req, timeout=30) as response:
                payload = response.read()
                status = response.status
                content_type = response.headers.get("Content-Type", "application/json")
        except HTTPError as exc:
            payload, status = exc.read(), exc.code
            content_type = exc.headers.get("Content-Type", "application/json")
        except (URLError, TimeoutError) as exc:
            payload = ('{"error":"ERIA API unavailable","detail":' +
                       __import__("json").dumps(str(exc)) + '}').encode()
            status, content_type = 502, "application/json"
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

if __name__ == "__main__":
    if not (ROOT / "index.html").is_file():
        raise SystemExit("Missing standalone www/index.html")
    print(f"Æị standalone: http://{HOST}:{PORT}/")
    print(f"ERIA API proxy: {API_ORIGIN}/api/*")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
