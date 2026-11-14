"""Opt-in lifecycle manager joining HTTPS PONS relay to the Termux inbox monitor."""
from __future__ import annotations
import os, threading
from typing import Any
from .relay import PonsRelayClient, RelayHold
from .approval import ApprovalError
from .resonance import InboxMonitor, load_config

class RelayLifecycle:
    def __init__(self, repository, monitor: InboxMonitor):
        self.root = repository
        self.monitor = monitor
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread = None
        self._state = "disabled"
        self._last_error = None
        self._client = None
    def status(self):
        with self._lock:
            return {"state":self._state,"enabled":self._state in ("running","idle"),
                    "last_error":self._last_error,"monitor":self.monitor.status(),
                    "transport":"phone-initiated HTTPS"}
    def start(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                return self.status()
            if os.environ.get("ERIA_PONS_RELAY_ENABLED") != "1":
                self._state="disabled"
                raise RelayHold("Set ERIA_PONS_RELAY_ENABLED=1 to opt in.")
            self._client=PonsRelayClient.from_environment()
            self._stop.clear()
            self._state="starting"
            self._thread=threading.Thread(target=self._run,name="eria-pons-relay",daemon=True)
            self._thread.start()
            return self.status()
    def stop(self):
        self._stop.set()
        thread=self._thread
        if thread and thread.is_alive(): thread.join(timeout=3)
        with self._lock:
            if thread and thread.is_alive(): self._state="stopping"
            else: self._state="stopped"
            return self.status()
    def _handle_grant(self, grant: dict[str,Any]):
        # relay.poll_once has already cryptographically verified exact scope.
        grant_id=grant["grant_id"]
        config=load_config(self.root)
        config["automatic_capture"]["enabled"]=True
        config["automatic_capture"]["approval_reference"]="pons:"+grant_id
        # Atomic settings replacement; secret material never enters settings.
        import json, os, tempfile
        settings=self.root/"storage"/"settings.json"
        fd,name=tempfile.mkstemp(prefix=".settings-",dir=str(settings.parent))
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as stream:
                json.dump(config,stream,indent=2); stream.write("\\n"); stream.flush(); os.fsync(stream.fileno())
            os.replace(name,settings)
        except Exception:
            try: os.unlink(name)
            except OSError: pass
            raise
        status=self.monitor.start("pons:"+grant_id)
        return {"monitor_state":status.get("state"),"approval_reference":"pons:"+grant_id}
    def _run(self):
        with self._lock: self._state="running"
        while not self._stop.is_set():
            try:
                result=self._client.poll_once(self._handle_grant)
                with self._lock:
                    self._state="running" if result.get("status") in ("idle","processed") else "error"
                    self._last_error=None
            except (RelayHold,ApprovalError,OSError,ValueError) as exc:
                with self._lock:
                    self._state="error"; self._last_error=str(exc)
            self._stop.wait(15)
        with self._lock: self._state="stopped"
