"""Authenticated HTTP bridge between the Android JOB dashboard and Stride integrations.

Run with: STRIDE_BRIDGE_TOKEN='...' PYTHONPATH=python python -m stride_core.android_bridge --db stride_jobs.sqlite3
The default listener is loopback-only. Non-loopback binds require TLS certificate/key.
"""
from __future__ import annotations

import argparse
import hmac
import json
import os
import re
import ssl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

from stride_core.job_engine import JobStore
from stride_core.job_integrations import (
    connect_faculty_run, connect_geometry_experiment, list_artifacts, import_android_job_transfer,
)

MAX_BODY = 2 * 1024 * 1024


def make_server(store: JobStore, token: str, host: str = "127.0.0.1",
                port: int = 8765, certfile: str | None = None,
                keyfile: str | None = None):
    if not token or len(token) < 24:
        raise ValueError("bridge token must contain at least 24 characters")
    if host not in {"127.0.0.1", "::1", "localhost"} and not (certfile and keyfile):
        raise ValueError("non-loopback bridge binds require TLS certificate and key")

    class Handler(BaseHTTPRequestHandler):
        server_version = "StrideBridge/1"

        def _reply(self, status: int, value: dict):
            data = json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _authorized(self) -> bool:
            supplied = self.headers.get("Authorization", "")
            expected = "Bearer " + token
            if not hmac.compare_digest(supplied, expected):
                self._reply(401, {"error": "unauthorized"})
                return False
            return True

        def _body(self):
            raw_length = self.headers.get("Content-Length", "")
            if not raw_length.isdigit() or int(raw_length) > MAX_BODY:
                raise ValueError("invalid or oversized request body")
            raw = self.rfile.read(int(raw_length))
            value = json.loads(raw.decode("utf-8"))
            if not isinstance(value, dict):
                raise ValueError("request JSON must be an object")
            return value

        def do_GET(self):
            if not self._authorized():
                return
            match = re.fullmatch(r"/v1/jobs/([^/]+)/artifacts", self.path)
            if not match:
                self._reply(404, {"error": "not found"})
                return
            try:
                job_id = unquote(match.group(1))
                self._reply(200, {"artifacts": list_artifacts(store, job_id)})
            except Exception as exc:
                self._reply(400, {"error": str(exc)})

        def do_POST(self):
            if not self._authorized():
                return
            if self.path == "/v1/jobs/import-android":
                try:
                    count = import_android_job_transfer(store, self._body())
                    self._reply(201, {"imported_jobs": count, "policy": "duplicates are rejected; existing JOBs are never overwritten"})
                except Exception as exc:
                    self._reply(400, {"error": str(exc)})
                return
            match = re.fullmatch(r"/v1/jobs/([^/]+)/(faculty|geometry)", self.path)
            if not match:
                self._reply(404, {"error": "not found"})
                return
            try:
                job_id = unquote(match.group(1))
                payload = self._body()
                if match.group(2) == "faculty":
                    required = {"observations", "concepts", "prediction", "measured", "channels"}
                    if not required.issubset(payload):
                        raise ValueError("Faculty payload requires observations, concepts, prediction, measured, channels")
                    result = connect_faculty_run(
                        store, job_id, payload["observations"], payload["concepts"],
                        float(payload["prediction"]), float(payload["measured"]),
                        payload["channels"])
                    self._reply(200, result)
                else:
                    result = connect_geometry_experiment(store, job_id, payload)
                    self._reply(201, result)
            except Exception as exc:
                self._reply(400, {"error": str(exc)})

        def log_message(self, fmt, *args):
            return

    server = ThreadingHTTPServer((host, port), Handler)
    if certfile and keyfile:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile, keyfile)
        server.socket = context.wrap_socket(server.socket, server_side=True)
    return server


def main():
    parser = argparse.ArgumentParser(description="Stride Android JOB integration bridge")
    parser.add_argument("--db", default="stride_jobs.sqlite3")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--cert")
    parser.add_argument("--key")
    args = parser.parse_args()
    token = os.environ.get("STRIDE_BRIDGE_TOKEN", "")
    store = JobStore(args.db)
    server = make_server(store, token, args.host, args.port, args.cert, args.key)
    try:
        print("Stride bridge listening on %s:%s" % (args.host, args.port))
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
