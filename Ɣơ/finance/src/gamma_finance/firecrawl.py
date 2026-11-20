"""Firecrawl REST adapter; requires explicit HTTPS domain allowlist and external API key."""
from dataclasses import dataclass
import hashlib, json, os
from urllib.parse import urlparse
from urllib.request import Request, urlopen
@dataclass(frozen=True)
class CrawlEvidence:
    source_url: str
    domain: str
    content_sha256: str
    markdown: str
    provider: str = "firecrawl"
    mode: str = "SOURCE_EVIDENCE_ONLY"
def scrape(url: str, *, allowed_domains: set[str], timeout_seconds: int = 20) -> CrawlEvidence:
    parsed = urlparse(url)
    domain = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not domain or domain not in {d.lower() for d in allowed_domains}:
        raise ValueError("only HTTPS URLs on the explicit domain allowlist are accepted")
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        raise RuntimeError("HOLD: FIRECRAWL_API_KEY is not configured")
    body = json.dumps({"url": url, "formats": ["markdown"]}).encode()
    req = Request("https://api.firecrawl.dev/v1/scrape", data=body,
                  headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
                  method="POST")
    with urlopen(req, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not payload.get("success"):
        raise RuntimeError("Firecrawl did not return success")
    markdown = (payload.get("data") or {}).get("markdown")
    if not isinstance(markdown, str) or not markdown:
        raise RuntimeError("Firecrawl response contains no markdown")
    return CrawlEvidence(url, domain, hashlib.sha256(markdown.encode()).hexdigest(), markdown)
