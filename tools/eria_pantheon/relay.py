"""Phone-initiated HTTPS polling transport for signed PONS approval grants.

Disabled unless explicitly configured. This client never opens an inbound port.
It validates grants locally before invoking a caller-supplied handler.
"""
from __future__ import annotations

import json
import os
import time
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .approval import ApprovalError, verify_signed_grant


class RelayHold(RuntimeError):
    """Remote relay configuration or response is not acceptable."""


class PonsRelayClient:
    MAX_RESPONSE_BYTES = 16 * 1024

    def __init__(self, base_url: str, bearer_token: str, signing_key: str | bytes,
                 *, timeout: float = 8.0, opener: Callable[..., Any] = urlopen):
        parsed = urlparse(base_url)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise RelayHold("Relay URL must be an HTTPS origin without embedded credentials.")
        if parsed.query or parsed.fragment:
            raise RelayHold("Relay base URL cannot contain a query or fragment.")
        if not bearer_token or len(bearer_token) < 24:
            raise RelayHold("Relay bearer token is missing or too short.")
        if isinstance(signing_key, str):
            signing_key = signing_key.encode("utf-8")
        if not isinstance(signing_key, bytes) or len(signing_key) < 32:
            raise RelayHold("PONS signing key must contain at least 32 bytes.")
        self.base_url = base_url.rstrip("/")
        self.token = bearer_token
        self.key = signing_key
        self.timeout = max(2.0, min(float(timeout), 20.0))
        self.opener = opener

    @classmethod
    def from_environment(cls, *, opener: Callable[..., Any] = urlopen):
        url = os.environ.get("ERIA_PONS_RELAY_URL", "")
        token = os.environ.get("ERIA_PONS_RELAY_TOKEN", "")
        key = os.environ.get("ERIA_PONS_APPROVAL_KEY", "")
        if not (url and token and key):
            raise RelayHold("Remote relay is disabled; set all three ERIA_PONS_RELAY_* credentials.")
        return cls(url, token, key, opener=opener)

    def _request(self, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        if path not in ("/v1/requests/next", "/v1/requests/ack"):
            raise RelayHold("Unsupported relay path.")
        data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
        req = Request(self.base_url + path, data=data, method="GET" if data is None else "POST",
                      headers={"Authorization": "Bearer " + self.token,
                               "Accept": "application/json",
                               **({"Content-Type": "application/json"} if data is not None else {})})
        try:
            with self.opener(req, timeout=self.timeout) as response:
                raw = response.read(self.MAX_RESPONSE_BYTES + 1)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise RelayHold("Relay request failed; no action was taken.") from exc
        if len(raw) > self.MAX_RESPONSE_BYTES:
            raise RelayHold("Relay response exceeds size limit.")
        try:
            result = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RelayHold("Relay response is not valid UTF-8 JSON.") from exc
        if not isinstance(result, dict):
            raise RelayHold("Relay response must be a JSON object.")
        return result

    def poll_once(self, handler: Callable[[dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
        """Fetch one queued request, verify it, run handler, then acknowledge outcome."""
        envelope = self._request("/v1/requests/next")
        if envelope.get("status") == "empty":
            return {"status": "idle"}
        request_id = envelope.get("request_id")
        grant = envelope.get("grant")
        if not isinstance(request_id, str) or not request_id or not isinstance(grant, dict):
            raise RelayHold("Relay response lacks request identity or signed grant.")
        try:
            verified = verify_signed_grant(grant, self.key,
                capability="eria.acquire", scope="storage/inbox/")
        except ApprovalError as exc:
            self._request("/v1/requests/ack", {"request_id": request_id,
                "status": "rejected", "reason": "grant_verification_failed"})
            raise RelayHold("Remote grant rejected by local PONS verification.") from exc
        outcome = handler(verified)
        if not isinstance(outcome, dict):
            raise RelayHold("Local PONS handler must return an outcome object.")
        # Acknowledgement is informational; local action is governed by PONS.
        self._request("/v1/requests/ack", {"request_id": request_id,
            "status": "processed", "outcome": outcome})
        return {"status": "processed", "request_id": request_id, "outcome": outcome}

    def run(self, handler: Callable[[dict[str, Any]], dict[str, Any]], *,
            stop_event, poll_interval: float = 15.0) -> None:
        """Phone-initiated polling loop. Stops cleanly when stop_event is set."""
        interval = max(5.0, min(float(poll_interval), 300.0))
        while not stop_event.is_set():
            try:
                self.poll_once(handler)
            except RelayHold:
                # Fail closed; the caller can expose the error via its own status.
                pass
            stop_event.wait(interval)
