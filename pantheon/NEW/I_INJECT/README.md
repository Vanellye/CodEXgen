# ERIA I-INJECT — Protected Injection Layer

**Purpose:** accept a proposed input for review without silently changing the target.

## Contract

Intent → Identify source → Preserve provenance → Check target compatibility →
Verify exact scope → Verify protections → Produce proposal → Human review →
Separately authorized integration → Test → Record outcome.

The C99 module returns `PROPOSAL_ONLY`; it never performs the integration.
It requires non-empty intent, source/provenance/target/compatibility/approval
references, exact requested-to-authorized scope equality, and affirmative
upstream verification of all protections:

1. Consent
2. Security
3. Safety
4. Ownership
5. Approval

Compatibility is an additional hold gate. Missing or conflicting information
fails closed. The original source and its history remain untouched.

## Copy and compile

Copy `I_INJECT.h` and `I_INJECT.c` into the project, then include the header.
Compile the contract tests from this directory:

```sh
cc -std=c99 -Wall -Wextra -Werror -I. I_INJECT.c tests/test_I_INJECT.c -o i-inject-test
./i-inject-test
```

## Grave protections

- No bypass of consent, security, safety, ownership, or approval.
- No silent overwrite, destructive replacement, publication, financial transfer,
  external collection, or execution.
- No promotion of an interpretation into fact.
- Keep source, provenance, authorization, compatibility evidence, scope, and
  decision in an append-only audit record.
- Treat caller-supplied verification flags as assertions, not cryptographic proof.
  The integration must authenticate reviewers and validate references upstream.
- Use a versioned checkpoint and tested rollback before any separately approved
  write operation.

This module is a portable validation boundary, not a system-wide runtime hook.
It is staged beside Y_BYPASS and is not wired into every ERIA module or branch.
