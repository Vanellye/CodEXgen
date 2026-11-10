# Local channel router integration

This integration branch is cut from `main` and contains only the local router implementation, its focused tests, and a dedicated CI job.

## Scope

- SQLite-backed local channels with owner-managed membership.
- Separate publish and read grants.
- Push and pull are distinct operations.
- Idempotency keys reject duplicate event creation and mismatched key reuse.
- Consequential requests require explicit recipient acceptance.
- Revocation blocks later pulls and acceptance.
- Event and decision rows are append-only at the SQLite trigger layer.

## Deliberate limits

This is local-only. It opens no network sockets, has no realm-to-realm transport, and does not execute action payloads. The SQLite database is not tamper-proof against a database owner who can alter the file or schema. A later network design requires a separate security review covering identity, transport security, replay resistance, per-hop authorization, payload limits, audit integrity, and revocation races.

## Validation

The dedicated workflow compiles only `python/channel_router.py` and `tests/test_channel_router.py`, then runs the focused test module. This isolates router validation from unrelated legacy syntax failures elsewhere in the repository. Repository-wide compile failures remain visible in the general CI workflow and are tracked separately in issue #6.

## Provenance

The router and tests are copied from PR #5 at commit `68d83bf0c8e4b3d38cdf189123f27f66336e57de`. This is an additive integration proposal; it does not merge PR #5 or modify its base branch.
