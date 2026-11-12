# ERIA Walla Regurgitation — TRU Meet Point

A disconnected wallet's **proposal and traceable records** can be brought back
for reconciliation. "Regurgitation" here means returning records for review,
not restoring wallet access, secrets, or funds.

## TRU Meet Point

The owner record and system record are compared against the pinned proposal.
The module requires references to the proposal, wallet, owner, original record,
provenance, both sides of the comparison, and the review record.

Evidence is explicitly classified as:
- verified reference;
- unverified claim; or
- interpretation.

A reference label does not itself prove the underlying statement is true.
Unverified claims and interpretations must remain labeled as such.

## Protected decision

A proposal is ready for human review only when:
- the owner confirms the match;
- the system-side record is available;
- requested and authorized scopes match exactly;
- consent, security, safety, ownership, and approval are all verified;
- transaction history remains preserved; and
- the evidence class and traceability references are present.

Any missing or conflicting condition returns HOLD. The module never reconnects
a wallet, restores credentials, changes provider state, accepts the proposal,
or moves funds. Those actions require separate provider-specific implementation,
fresh authorization, and independent review.

## Build tests

```sh
cc -std=c99 -Wall -Wextra -Werror -I. WALLA_REGURGITATION.c tests/test_WALLA_REGURGITATION.c -o walla-tru-test
./walla-tru-test
```

The module is a proposal-reconciliation contract, not a live wallet connector.
