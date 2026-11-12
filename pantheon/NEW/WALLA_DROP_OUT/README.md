# ERIA Walla 《¡》 — Wallet Drop-Out

This module prepares a controlled wallet-disconnection proposal and labels the
replacement interface **Walla 《¡》**. It does not transfer, withdraw, destroy,
or migrate funds. It does not call a wallet provider or revoke credentials.

## Protected sequence

1. Identify wallet, owner, and provider references.
2. Confirm the exact disconnect scope.
3. Verify consent, security, safety, ownership, and approval.
4. Require preservation of transaction history and audit provenance.
5. Return a disconnect proposal for human review.
6. A separately reviewed provider adapter may perform revocation only after
   fresh authorization and provider-specific confirmation.

Any missing or conflicting condition returns HOLD. Missing identifiers return
INVALID. No gate can be bypassed.

## Preservation rules

- Disconnecting an integration is not closing the underlying financial account.
- Funds remain with the wallet provider; this module never moves them.
- Transaction history, receipts, provenance, and ownership records are retained.
- Secrets, seed phrases, private keys, and credentials must not be copied into
  this module or its logs.
- A disconnected wallet must not be silently reconnected under the Walla label.
- Provider revocation and reconnect behavior require a separately audited adapter.

## Build tests

```sh
cc -std=c99 -Wall -Wextra -Werror -I. WALLA_DROP_OUT.c tests/test_WALLA_DROP_OUT.c -o walla-test
./walla-test
```

This is a proposal-only contract, not an executed disconnection or a system-wide
wallet migration. Integration must be reviewed and tested independently.
