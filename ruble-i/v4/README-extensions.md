# v4 extensions: English interpretation, cryptographic review, provider parameters

- `crypto_reviewer.py` verifies Ed25519 signatures against an externally governed public-key registry. Revocation and freshness are checked. The `cryptography` dependency must be installed in the deployment environment. Missing keys, missing crypto library, malformed signatures, expired artifacts, or revoked keys fail closed.
- `interpret.py` provides a three-part output: plain-English interpretation, reviewer-verification status, and provider-transmission readiness. It never transmits.
- `provider-parameters.example.json` describes Wise Platform and Plaid sandbox parameter references. Credentials are secret-manager references only; values are deliberately blank.
- `history_journal.py` appends successful/failed authentication and transfer lifecycle events as a SHA-256 hash chain. A local hash chain detects modification but is not immutable against a privileged filesystem rewrite; production requires external signed checkpoints, access controls, durable storage, and reconciliation.
- `history-event.schema.json` defines the event shape. The checked-in v4 index remains an empty schema/index: no actual authentication or transfer successes are fabricated.

Provider adapter code remains prepare-only. The configuration describes future integration parameters, not active provider connections. No IBAN lookup authorizes withdrawals. No funds are routed through a portal by this code.
