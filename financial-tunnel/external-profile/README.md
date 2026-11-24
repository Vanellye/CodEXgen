# ERIA External Profile Service

A standalone identity-profile and authorization-evidence service with an independently deployed API and PostgreSQL evidence store. It does **not** execute transactions.

## Integration target: Auth0 development tenant

The service uses standard OIDC access-token validation and is provider-neutral. The tenant domain and ERIA API Identifier below were supplied for the development integration. Repository configuration does not itself prove that the Auth0 API exists, that a client is configured, or that authentication has succeeded.

1. In the Auth0 development tenant, confirm the tenant domain is `dev-ekleezvw1eidw3w4.us.auth0.com`.
2. Under **Applications → APIs**, create or select an API named `ERIA External Profile Sandbox`. Its Identifier must exactly equal `https://eria-financial-tunnel-sandbox.example/api`. Use RS256 signing. Do not use the Auth0 Management API audience (`https://TENANT/api/v2/`) for ERIA.
3. Create a Native or SPA application for the test client. Use Authorization Code Flow with PKCE; do not enable the Resource Owner Password flow.
4. Configure the client to request an access token for the ERIA API Identifier audience. The client should request only the scopes it needs. Do not put a client secret in this service.
5. The issuer and JWKS endpoint are derived from the tenant domain and are configured in `.env.example`. The issuer includes its trailing slash.
6. Obtain an access token through the provider's hosted login flow and call `GET /v1/profiles/me`. The service creates a `member` profile on first login. It ignores role claims supplied by the token.
7. Provision the initial `profile_admin` out-of-band through a reviewed database operation after verifying the exact issuer and subject. There is deliberately no self-service admin bootstrap endpoint.

Configured OIDC values:

- `OIDC_ISSUER=https://dev-ekleezvw1eidw3w4.us.auth0.com/`
- `OIDC_AUDIENCE=https://eria-financial-tunnel-sandbox.example/api`
- `OIDC_JWKS_URL=https://dev-ekleezvw1eidw3w4.us.auth0.com/.well-known/jwks.json`

Auth0's API audience must match the access token's `aud` claim exactly. The issuer must match its `iss` claim exactly. Do not use an ID token as the API bearer token.

## Boundaries and authorization

- Identity is authenticated by an external OIDC issuer (JWT signature, issuer, audience, expiry and allowed algorithm are verified against its JWKS).
- OIDC issuer and JWKS endpoints must use HTTPS.
- Roles are stored server-side; token-supplied role claims are ignored.
- New identities receive only the `member` role. A trusted operator provisions the first administrator out-of-band; existing admins may provision subsequent roles.
- Authorization decisions require `financial_approver` or `profile_admin`, a fresh preview, a matching SHA-256 hash, and an approver subject different from the transaction initiator.
- Every decision, including denials, is appended to the evidence table. Evidence and profile-role events reject UPDATE/DELETE.
- The service returns a decision and evidence identifier only. A separate financial execution adapter must verify the evidence and apply its own execution controls.
- No provider SDKs, wallet keys, bank connections, or live transaction calls are included. Financial execution remains disabled.

## Database and environment

Apply `schema.sql` to a dedicated PostgreSQL database, then copy `.env.example` to a private local environment file and set:

- `DATABASE_URL`
- `OIDC_ISSUER`
- `OIDC_AUDIENCE`
- `OIDC_JWKS_URL`

Optional: `DATABASE_SSL=true`, `EXTERNAL_PROFILE_HOST=127.0.0.1`, `EXTERNAL_PROFILE_PORT=8787`.

Never commit access tokens, client secrets, or database credentials. Keep the database private and use TLS in deployed environments. Configure the application database role with least privilege; the immutable triggers do not protect against a database owner or superuser.

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
    "initiatedBySubject": "OIDC_SUBJECT_OF_TRANSACTION_INITIATOR",
    "amountMinor": 1250,
    "currency": "USD",
    "destinationRef": "synthetic-destination-001",
    "network": "internal",
    "expiresAt": "2030-01-01T00:00:00.000Z"
  },
  "previewHash": "<64 lowercase hex SHA-256 from hashTransactionPreview>"
}
```

## Run and verify

After applying the schema and setting the environment:

`node --experimental-strip-types financial-tunnel/external-profile/service.ts`

Run the focused tests with:

`node --experimental-strip-types --test financial-tunnel/external-profile/service.test.ts`

The API binds to loopback by default. A successful health check does not mean an identity tenant is connected; verify with a real sandbox-issued access token and `GET /v1/profiles/me`. The supplied tenant and audience values are configured, but provider connectivity remains unverified until a token is obtained and validated and the database is provisioned.
