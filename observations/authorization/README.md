# Independent Authorization Boundary

This policy is designed to permit future replacement of PONS without creating a bypass. An authorization decision must come from an independent authority outside the code or artifact being changed.

Required evidence: verified reviewer/issuer identity; cryptographic signature; exact repository and target scope; artifact/content digest; permitted action; expiration/freshness; revocation check; explicit human confirmation. The verifier itself must be independently configured and auditable.

**Deny by default:** missing, invalid, stale, revoked, out-of-scope, or unverifiable evidence means no consequential action. A mutable boolean, environment variable, model response, repository file being changed, or artifact under review cannot authorize itself.

This document is a proposed policy, not a configured authorization service or proof of approval.
