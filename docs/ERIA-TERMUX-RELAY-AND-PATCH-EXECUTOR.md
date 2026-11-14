# ERIA Termux PONS relay and exact-patch executor

## Relay lifecycle

The Termux server exposes `POST /api/pons/relay/start`, `POST /api/pons/relay/stop`, and `GET /api/pons/relay/status`. Relay polling is opt-in and remains disabled unless `ERIA_PONS_RELAY_ENABLED=1` and all three credentials are present: `ERIA_PONS_RELAY_URL` (HTTPS), `ERIA_PONS_RELAY_TOKEN`, and `ERIA_PONS_APPROVAL_KEY`. The phone initiates outbound HTTPS polling; this does not make the loopback server remotely reachable. A separately hosted relay service implementing `/v1/requests/next` and `/v1/requests/ack` is still required.

The relay client accepts only signed `eria.acquire` grants scoped exactly to `storage/inbox/`. The lifecycle callback enables the inbox monitor only after the relay client's HMAC verification. The monitor runs only while the Termux server process remains alive. Stop the relay poller with `/api/pons/relay/stop`; pause inbox capture separately with `/api/acquisition/pause`.

## Exact-patch executor

`tools/eria_pantheon/patch_executor.py` accepts a complete UTF-8 replacement (not a shell command or arbitrary diff), a repository-relative existing file path, and a signed grant. The grant must have capability `eria.source.write`, scope exactly equal to the target path, and `patch_sha256` equal to SHA-256 of the exact replacement bytes. Grants expire under the existing 15-minute PONS policy.

Writes are confined to existing files under `tools/`, `tests/`, `docs/`, or `interfaces/`. Absolute paths, traversal, symlinks, `.git`, and `storage/` are rejected. The executor stages bytes beside the target and uses atomic replacement. It never runs the patched code, invokes a shell, or performs Git operations. Each attempt writes a JSONL audit record under `storage/approvals/patch-executions.jsonl`; consumed grant IDs/nonces cannot be replayed from that ledger.

## Operational boundaries

- `main` is not a target of this implementation; all repository changes are on the named feature branch.
- No automatic commit, push, merge, deployment, or arbitrary command execution is provided.
- The patch endpoint is loopback-only through the existing Termux server. Keep the HMAC key out of the browser, repository, logs, and settings file.
- HMAC uses a shared secret; it is not human identity verification. Protect key issuance and relay service credentials out-of-band.
- Validate with `python -m unittest discover -s tests -p 'test_eria_*.py'` on the Termux host before enabling relay polling or using source-write grants.
