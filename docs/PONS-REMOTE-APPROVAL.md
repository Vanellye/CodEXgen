# PONS remote approval contract

## Current implementation

ERIA now has an HMAC-SHA256 capability-envelope verifier in
`tools/eria_pantheon/approval.py`. It enforces:

- exact capability and scope matching;
- a short expiry window (15 minutes maximum by default);
- signed grant identity and nonce;
- optional exact SHA-256 patch binding for source-write grants;
- constant-time signature comparison.

The local server exposes `POST /api/pons/remote-approve` for the narrowly
scoped `eria.acquire` capability on `storage/inbox/`. A consumed-grant
ledger is written under `storage/approvals/consumed-grants.jsonl`, and
replayed grant IDs are held. The route returns the monitor's observed state;
it does not synthesize a successful state.

## Key provisioning

Set `ERIA_PONS_APPROVAL_KEY` in the Termux process environment using a
random secret of at least 32 bytes. Do not commit the secret, put it in the
portal HTML, or print it in logs. A workflow signer must use the same secret
from a protected secret store. Rotate the key if it is exposed.

Example key creation in Termux:

```sh
export ERIA_PONS_APPROVAL_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

The workflow signer creates a grant over the unsigned canonical JSON payload
using `sign_grant`. Submit the resulting signed object as
`{"grant": ...}` to `/api/pons/remote-approve`.

## Source-writing boundary

The verifier supports the capability name `eria.source.write` only when the
grant is bound to an exact repository-relative scope and a 64-character
lowercase SHA-256 patch hash. This is a verification primitive, not a source
writing executor. No shell execution, arbitrary file writing, Git commit,
push, merge, deployment, or automatic patch application is enabled by this
change. A future executor must independently verify the patch bytes, reject
path traversal and symlinks, stage only the exact approved path, record an
append-only audit event, and require a separate commit/push authorization.

## Remote reachability limitation

The ERIA HTTP server remains bound to `127.0.0.1` and enforces loopback Host
and Origin checks. Therefore a GitHub-hosted workflow cannot reach this endpoint
directly. A remote relay/tunnel or phone-initiated polling transport, with
mutual authentication and replay protection, must be designed and reviewed
before remote workflow execution is enabled. Do not expose port 8970 directly
to the public internet.

## Operational truth

The API reports `RUNNING` only when the local monitor object reports
`state=running`. This is an in-process thread and stops when the Termux
server exits or Android terminates it. A response from the verifier alone is
not proof that an inbox scan succeeded.


## Phone-initiated relay transport (client adapter)

The optional client adapter is `tools/eria_pantheon/relay.py`. It initiates
outbound HTTPS requests from the phone; it does not open an inbound port.
It accepts only HTTPS base URLs, uses bearer authentication, bounds response
size and timeout, verifies the signed grant locally, and acknowledges the
outcome after the local handler returns. Polling is opt-in and requires all
three environment variables:

- `ERIA_PONS_RELAY_URL`
- `ERIA_PONS_RELAY_TOKEN`
- `ERIA_PONS_APPROVAL_KEY`

The relay service must implement:
- `GET /v1/requests/next` -> `{"status":"empty"}` or
  `{"request_id":"...","grant":{...signed PONS grant...}}`
- `POST /v1/requests/ack` with request_id, status and outcome.

The remote relay service is not hosted or deployed by this repository change,
and the adapter is not yet wired into the Termux server lifecycle. Until a
separately deployed relay service and reviewed server integration exist,
remote polling is a tested transport component only; the local portal workflow
continues to operate independently. Never expose the HMAC key to browser code.
