# ERIA Wiki Drop-Link API (Go)

A dependency-free Go HTTP service for ERIA Wiki Drop-Link. It provides authenticated link capture, archive-with-provenance behavior, and a tamper-evident JSONL event ledger. Publication and background dispatch remain disabled.

## Requirements

- Go 1.22 or newer
- A persistent writable data directory
- A high-entropy API token of at least 32 characters
- HTTPS termination at the hosting platform or reverse proxy

## Run locally

```sh
export ERIA_API_TOKEN="$(openssl rand -hex 32)"
export ERIA_DATA_DIR="./data"
export PORT=8787
cd services/eria-wiki-drop-link
go test ./...
go run .
```

Keep `ERIA_API_TOKEN` out of source control and browser JavaScript. The `data/` directory contains the append-only event log; back it up using the host's persistent-volume mechanism. The process listens on `PORT` (default `8787`).

## API

All `/api/*` routes require `Authorization: Bearer $ERIA_API_TOKEN`. `GET /health` is public and returns a minimal health response.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/links` | List active links; optional `?q=` filter |
| POST | `/api/links` | Add a validated HTTP(S) link |
| DELETE | `/api/links/:id` | Archive a link; original events remain in the ledger |
| GET | `/api/audit` | Read the event ledger after startup integrity verification |
| POST | `/api/authorization-intents` | Record a narrowly scoped human intent; never enables execution |

Supported categories: `Reference`, `Architecture`, `Research`, `Governance`, `Implementation`, `Other`.

## cURL client

Set the base URL and token in the shell:

```sh
export ERIA_BASE_URL="https://your-eria-host.example"
export ERIA_API_TOKEN="replace-with-a-secret-of-32-or-more-characters"
```

Health check:

```sh
curl --fail-with-body -sS "$ERIA_BASE_URL/health"
```

List and search:

```sh
curl --fail-with-body -sS -H "Authorization: Bearer $ERIA_API_TOKEN" \
  "$ERIA_BASE_URL/api/links"

curl --fail-with-body -sS -G -H "Authorization: Bearer $ERIA_API_TOKEN" \
  --data-urlencode "q=architecture" "$ERIA_BASE_URL/api/links"
```

Create a link:

```sh
curl --fail-with-body -sS -X POST "$ERIA_BASE_URL/api/links" \
  -H "Authorization: Bearer $ERIA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"ERIA reference","url":"https://example.com/eria","category":"Reference","description":"Reference material","source":"manual"}'
```

Archive a link (replace the UUID):

```sh
curl --fail-with-body -sS -X DELETE "$ERIA_BASE_URL/api/links/00000000-0000-4000-8000-000000000000" \
  -H "Authorization: Bearer $ERIA_API_TOKEN"
```

Read the audit ledger:

```sh
curl --fail-with-body -sS -H "Authorization: Bearer $ERIA_API_TOKEN" \
  "$ERIA_BASE_URL/api/audit"
```

Record an authorization intent (this is an audit record only):

```sh
curl --fail-with-body -sS -X POST "$ERIA_BASE_URL/api/authorization-intents" \
  -H "Authorization: Bearer $ERIA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"scope":"publish_wiki","confirmation":"publish_wiki","reason":"Reviewed request"}'
```

A runnable command wrapper is provided at `curl-examples.sh`; it requires `curl` and `jq`. Run it with `health`, `list`, `search QUERY`, `add TITLE URL [CATEGORY]`, `archive UUID`, `audit`, or `intent SCOPE [REASON]`.

## Authorization boundary

The intent endpoint accepts only `publish_wiki` and `background_dispatch`, and requires the caller to repeat the exact scope in `confirmation`. It writes an event with `executionEnabled: false`. There is deliberately no publish, webhook-dispatch, or external-execution endpoint in this version. An intent record is not a PONS grant and does not establish runtime authority. Any future privileged integration must independently verify a valid, scoped PONS grant at the actual mutation boundary.

## Data and integrity

Events are stored as JSON Lines in `events.jsonl`. Each event includes a sequence number, timestamp, event type, payload, previous hash, and SHA-256 hash. Startup verifies the entire chain and refuses to serve if an entry is malformed or modified. Writes are serialized within one process and synced before the in-memory sequence advances.

This is tamper-evident, not immutable: an administrator with write access to the host can replace the file and recompute the chain. For stronger assurance, replicate signed checkpoints to an independently controlled append-only store. Run one instance per data directory; do not share the same ledger read-write across replicas. Back up the persistent volume and restrict filesystem permissions.

## Tests

```sh
cd services/eria-wiki-drop-link
go test ./...
```

Tests cover authentication, link creation/listing/archiving, unsafe URL rejection, non-executable authorization intents, and fail-closed ledger tampering detection.

## Frontend and deployment status

The supplied `eria_wiki_drop_link.html` remains a browser-local prototype; it stores data in browser local storage and does not call this API. Do not put the API token in browser JavaScript. A same-origin authenticated session/proxy adapter is a separate integration step. Until then, use trusted server-side clients or authenticated command-line requests.

GitHub stores this source; it does not run the service. Deploy the Go binary to a host with a persistent volume, configure `ERIA_API_TOKEN`, `ERIA_DATA_DIR`, and `PORT`, and expose it only over HTTPS. A host with ephemeral filesystem storage is unsuitable for this ledger without a durable external storage adapter.

## Deploy to Fly.io

This service is deployed from this directory (the directory containing this `go.mod`). The included `Dockerfile` builds a static Go binary, and `fly.toml` configures HTTPS, the health check, Chicago region, and a persistent volume mounted at `/data`.

1. Install and authenticate `flyctl`.
2. Replace the placeholder `app` value in `fly.toml` with a globally unique Fly app name.
3. From this directory, create the app without deploying: `fly launch --no-deploy --region ord`.
4. Create the persistent volume in the same region: `fly volumes create eria_data --region ord --size 1 --app YOUR_APP_NAME`.
5. Set the API secret locally (do not commit or paste it): `fly secrets set ERIA_API_TOKEN="$(openssl rand -hex 32)" --app YOUR_APP_NAME`. To retain a client-side copy, generate and save the token locally before setting it.
6. Deploy: `fly deploy --app YOUR_APP_NAME`.
7. Verify: `curl --fail-with-body https://YOUR_APP_NAME.fly.dev/health`.

The JSONL ledger is local to one Fly Volume. Run one Machine only; do not scale this service to multiple Machines or attach the same volume to multiple writers. Keep the API token out of browser code. The supplied browser prototype is not yet integrated with this API.

Fly.io volumes are persistent local storage and are not a substitute for an independent backup. Back up the volume and test restoration before storing important records.
