# ERIA Wiki Drop-Link API

A small, dependency-free Node.js API for the ERIA Wiki Drop-Link workflow. It adds authenticated, persistent link capture and a tamper-evident event ledger while keeping external publication and dispatch disabled.

## Requirements

- Node.js 20 or newer
- A persistent writable data directory
- A high-entropy API token of at least 32 characters
- TLS termination at the hosting platform or reverse proxy

## Run locally

```bash
export ERIA_API_TOKEN="$(openssl rand -hex 32)"
export ERIA_DATA_DIR="./data"
node services/eria-wiki-drop-link/server.mjs
```

The service listens on `PORT` (default `8787`). Keep `ERIA_API_TOKEN` out of source control and do not put it in browser JavaScript. The `data/` directory contains the append-only event log and should be backed up with the host's persistent-volume mechanism.

## API

All `/api/*` routes require `Authorization: Bearer $ERIA_API_TOKEN`. `GET /health` is public and returns a minimal health response.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/links` | List active links; optional `?q=` filter |
| POST | `/api/links` | Add a validated HTTP(S) link |
| DELETE | `/api/links/:id` | Archive a link; original events remain in the ledger |
| GET | `/api/audit` | Read the event ledger after its startup integrity check |
| POST | `/api/authorization-intents` | Record a narrowly scoped human intent; never enables execution |

### Create a link

```bash
curl -X POST "$ERIA_BASE_URL/api/links" \
  -H "Authorization: Bearer $ERIA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"ERIA reference","url":"https://example.com/eria","category":"Reference","description":"Reference material","source":"manual"}'
```

Supported categories: Reference, Architecture, Research, Governance, Implementation, Other.

### Authorization boundary

The intent endpoint accepts only `publish_wiki` and `background_dispatch`, and requires the caller to repeat the exact scope in `confirmation`. It writes an audit event with `executionEnabled: false`. There is deliberately no publish, webhook-dispatch, or external execution endpoint in this first version. An intent record is not a PONS grant and does not establish runtime authority.

## Data and integrity

Events are stored as JSON Lines in `events.jsonl`. Each event includes a sequence number, timestamp, event type, payload, previous hash, and SHA-256 hash. Startup verifies the complete chain and refuses to serve if it detects a malformed or modified entry. This is tamper-evident, not immutable: an administrator with write access to the host can replace the file and recompute the chain. For stronger assurance, replicate signed checkpoints to an independently controlled append-only store.

The service serializes writes within one Node.js process. Run one instance per data directory; do not mount the same ledger read-write into multiple replicas. Back up the persistent volume and restrict filesystem permissions.

## Tests

```bash
node --test services/eria-wiki-drop-link/server.test.mjs
```

## Current frontend status

The supplied `eria_wiki_drop_link.html` is a browser-local prototype. It stores links and audit records in that browser's local storage and does not call this API. Do not put the API token in that HTML. A same-origin authenticated session/proxy adapter is a separate integration step; until then, the API can be used by trusted server-side clients or authenticated command-line requests.

## Deployment note

GitHub stores the source; it does not run this Node.js service. Deploy it to a Node.js host with a persistent volume, configure `ERIA_API_TOKEN`, `ERIA_DATA_DIR`, and `PORT`, and expose it only over HTTPS. A serverless host with ephemeral filesystem storage is not suitable for the event ledger without an external durable database or storage adapter.
