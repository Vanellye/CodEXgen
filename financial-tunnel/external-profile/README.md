# ERIA External Profile Service

A standalone identity-profile and authorization-evidence service with an independently deployed API and PostgreSQL evidence store. It does **not** execute transactions.

## Boundaries

- Identity is authenticated by an external OIDC issuer (JWT signature, issuer, audience, expiry and allowed algorithm are verified against its JWKS).
- Roles are stored server-side; token-supplied role claims are ignored.
- New identities receive only the `member` role. An existing `profile_admin` provisions roles through the admin API.
- Authorization decisions require `financial_approver` or `profile_admin`, a fresh preview and an exact SHA-256 hash of the canonical preview.
- Every decision, including denials, is appended to the evidence table. Evidence and profile-role events reject UPDATE/DELETE.
- The service returns a decision and evidence identifier only. A separate financial execution adapter must verify the evidence and apply its own execution controls.
- No provider SDKs, wallet keys, or live transaction calls.

## Configuration

Apply `schema.sql` to a dedicated PostgreSQL database, then set:

- `DATABASE_URL`
- `OIDC_ISSUER`
- `OIDC_AUDIENCE`
- `OIDC_JWKS_URL`
- Optional: `DATABASE_SSL=true`, `EXTERNAL_PROFILE_HOST=127.0.0.1`, `EXTERNAL_PROFILE_PORT=8787`

No default issuer, credentials, admin profile, or production endpoint is supplied. The service fails startup if OIDC configuration is absent. Keep the database private and use TLS in deployed environments.

## API

- `GET /healthz` — liveness only; no identity required.
- `GET /v1/profiles/me` — sync and return the authenticated external profile.
- `PUT /v1/admin/profiles/:profileId/roles` — admin-only role provisioning; role changes are separately recorded.
- `POST /v1/authorization-decisions` — create ALLOW/DENY evidence for an allowlisted action and preview.
- `GET /v1/authorization-decisions/:evidenceId` — retrieve evidence owned by the caller or visible to a profile admin.

Authorization request body:

```json
{
  "action": "transfer.execute",
  "preview": {
    "amountMinor": 1250,
    "currency": "USD",
    "destinationRef": "synthetic-destination-001",
    "network": "internal",
    "expiresAt": "2030-01-01T00:00:00.000Z"
  },
  "previewHash": "<64 lowercase hex SHA-256 from hashTransactionPreview>"
}
```

## Run

After applying the schema and setting the environment:

`node --experimental-strip-types financial-tunnel/external-profile/service.ts`

This is an implementation scaffold, not a connected identity tenant. No OIDC issuer, database, user, or external profile has been provisioned or tested in this commit. The API binds to loopback by default.
