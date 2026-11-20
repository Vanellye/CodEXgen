# TRUE DANCER — Intelligence foundation

Status: isolated implementation candidate; synthetic tests only. This branch is based on `recovery/eria-ci-green-2026-11-18` and does not modify `main`.

## Scope

- Intelligence-first build with a PostgreSQL read-only adapter.
- Fixed, reviewed query templates for shop sales and inventory summaries.
- PONS authorization is checked for each query against a scope and exact source revision. A trusted independent signature/revocation verifier must be injected by the host; this package does not mint approvals.
- AVS validates payload digest, provenance fields, source revision, freshness, and an injected independent attestation verifier.
- The adapter sets `SET TRANSACTION READ ONLY`, executes only allowlisted SELECT templates, then rolls back and closes the connection.

## Explicit non-capabilities

No transfer, withdrawal, credit posting, wallet signing, order placement, customer messaging, marketing spend, arbitrary SQL, DDL/DML, shell execution, or provider write API is implemented. This is not a production-ready security certification. PostgreSQL credentials must be provisioned externally with SELECT-only privileges on dedicated intelligence views. Network policy, TLS, secret management, database role grants, and independent trust services remain deployment responsibilities.

## Environment

The application accepts a DSN supplied by the host. Do not commit credentials. Install `psycopg[binary]` in the runtime environment. The test suite uses synthetic fixtures and a fake connection; it does not connect to a live database.

## Tests

```sh
python -m unittest discover -s true_dancer/intelligence/tests -v
```

A passing synthetic test is not evidence that production PONS keys, revocation service, AVS attestation service, or PostgreSQL permissions are configured. Missing trust services must remain fail-closed.
