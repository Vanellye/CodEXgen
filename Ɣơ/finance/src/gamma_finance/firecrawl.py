"""Firecrawl adapter with exact-host and final-URL validation.

Public-page evidence only. No wildcard TLDs, private hosts, or side-effect actions.
"""
from dataclasses import dataclass
import hashlib
import ipaddress
import json
import os
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen

_BLOCKED_SUFFIXES = (".local", ".localhost", ".internal", ".test", ".invalid", ".example")
_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")

@dataclass(frozen=True)
class CrawlEvidence:
    source_url: str
    final_url: str
    domain: str
    content_sha256: str
    markdown: str
    provider: str = "firecrawl"
    mode: str = "SOURCE_EVIDENCE_ONLY"

def _host_from_https_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("only HTTPS URLs are accepted")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("URL credentials are not accepted")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("invalid URL port") from exc
    if port not in (None, 443):
        raise ValueError("only the standard HTTPS port is accepted")
    host = parsed.hostname.rstrip(".").lower()
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = None
    if ip is not None:
        if not ip.is_global:
            raise ValueError("non-public IP destinations are not accepted")
        return host
    if any(host == s.lstrip(".") or host.endswith(s) for s in _BLOCKED_SUFFIXES):
        raise ValueError("local, internal, and reserved test hostnames are not accepted")
    try:
        ascii_host = host.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise ValueError("invalid internationalized hostname") from exc
    labels = ascii_host.split(".")
    if len(labels) < 2 or any(not _LABEL.fullmatch(label) for label in labels):
        raise ValueError("a fully-qualified public hostname is required")
    return ascii_host

def _normalize_allowlist(allowed_domains: set[str]) -> set[str]:
    normalized = set()
    for candidate in allowed_domains:
        if not isinstance(candidate, str) or not candidate or "*" in candidate or "/" in candidate or ":" in candidate:
            raise ValueError("allowlist entries must be exact bare hostnames; wildcards are forbidden")
        normalized.add(_host_from_https_url("https://" + candidate))
    return normalized

def scrape(url: str, *, allowed_domains: set[str], timeout_seconds: int = 20) -> CrawlEvidence:
    domain = _host_from_https_url(url)
    approved = _normalize_allowlist(allowed_domains)
    if domain not in approved:
        raise ValueError("hostname is not explicitly allowlisted")
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        raise RuntimeError("HOLD: FIRECRAWL_API_KEY is not configured")
    body = json.dumps({"url": url, "formats": ["markdown"], "onlyMainContent": True}).encode("utf-8")
    req = Request(
        "https://api.firecrawl.dev/v2/scrape",
        data=body,
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not payload.get("success"):
        raise RuntimeError("Firecrawl did not return success")
    data = payload.get("data") or {}
    metadata = data.get("metadata") or {}
    source_url = metadata.get("sourceURL")
    final_url = metadata.get("url")
    if not isinstance(source_url, str) or not isinstance(final_url, str):
        raise RuntimeError("HOLD: Firecrawl omitted sourceURL or final url; redirect provenance cannot be verified")
    source_host = _host_from_https_url(source_url)
    final_host = _host_from_https_url(final_url)
    if source_host != domain or source_host not in approved or final_host not in approved:
        raise RuntimeError("HOLD: Firecrawl source or final redirect hostname is outside the exact allowlist")
    markdown = data.get("markdown")
    if not isinstance(markdown, str) or not markdown:
        raise RuntimeError("Firecrawl response contains no markdown")
    return CrawlEvidence(
        source_url=source_url,
        final_url=final_url,
        domain=final_host,
        content_sha256=hashlib.sha256(markdown.encode("utf-8")).hexdigest(),
        markdown=markdown,
    )
