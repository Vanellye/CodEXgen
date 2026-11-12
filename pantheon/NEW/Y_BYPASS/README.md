# ERIA Y Bypass — Copy/Paste Protection

**Y is a scoped continuation token, not a replacement value and not a universal override.**

This header-only C99 contract can be copied into another project as `Y_BYPASS.h`.
It distinguishes three explicitly declared input conditions:

- `Y_INPUT_ZERO`: a caller has identified a zero-valued optional field.
- `Y_INPUT_NULL`: a caller has identified an absent optional reference.
- `Y_INPUT_EMPTY`: a caller has identified an empty optional field.

It does **not** infer these conditions from arbitrary memory, rewrite the source value,
or collapse them into one representation. Numeric zero may be meaningful data.

## Permit rule

Y is returned only when the field is declared optional, the requested scope exactly
matches the allowed scope, and all five protections are affirmatively verified:
consent, security, safety, ownership, and approval. Missing, false, or mismatched
conditions return HOLD/DENIED. A missing audit reference makes the request INVALID.

The caller must verify those conditions upstream. The helper does not authenticate
identity, inspect permissions, establish consent, or cryptographically validate an
authorization reference. Never pass untrusted booleans as verified facts.

## Copy and compile

```c
#include "Y_BYPASS.h"

YBypassRequest request = {
    Y_INPUT_NULL, "optional_caption", "report.preview", "report.preview",
    "caption is optional", "approval-record-42",
    1, /* optional */
    1, /* consent verified */
    1, /* security verified */
    1, /* safety verified */
    1, /* ownership verified */
    1  /* approval verified */
};
YBypassResult result = y_bypass_resolve(&request);
/* Continue only if result.status == Y_STATUS_BYPASS_Y.
   Keep the original NULL/value unchanged and retain the audit record. */
```

Compile a translation unit that includes the header with strict C99 warnings:
`cc -std=c99 -Wall -Wextra -Werror -c your_file.c`

## Non-negotiable boundaries

- Never bypass consent, security, safety, ownership, or approval.
- Never treat Y as permission to access private data, publish, transfer value, or mutate source records.
- Never turn zero into truthy data or NULL into a valid pointer.
- Keep original input, provenance, reason, scope, authorization reference, and decision in the caller's append-only audit trail.
- A denied or ambiguous request remains HOLD; do not guess.
- Y authorizes only the explicitly declared optional-field continuation, not downstream consequential actions.

This is a portable guard contract, not a system-wide patch. Each integration must map its own
optional fields and verified gate results, add tests, and undergo review. It is not yet wired
into every ERIA module or runtime.
