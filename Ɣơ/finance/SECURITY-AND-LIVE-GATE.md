# Security gate: read-only → prepare → live

Current state:
- LOOK inventory is read-only and non-executing.
- ARM is a compile-only codec probe, with no financial capability.
- Firecrawl adapter uses FIRECRAWL_API_KEY from the environment and an exact HTTPS domain allowlist.
- Marker valuation records independently supplied evidence; marker labels never imply value.
- Withdrawals remain PREPARE_ONLY; no live executor exists.

Before live withdrawals can be implemented:
1. Verified provider integration, authenticated account ownership, and current available-balance evidence.
2. Independent reviewer enrollment and cryptographic identity verification; exact proposal digest, scope, expiry, and revocation checks.
3. Durable append-only, tamper-evident audit journal and independent retention.
4. Idempotency, replay protection, beneficiary allowlisting, fraud controls, limits, and reconciliation.
5. Explicit human confirmation of each exact withdrawal proposal.
6. Threat model, independent security review, sandbox integration tests, and separately approved production rollout.
7. A separately reviewed execution adapter; no bot or CI job may authorize or execute.

Until every gate is independently reviewed, live submission MUST remain disabled.
