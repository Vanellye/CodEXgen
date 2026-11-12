#include "I_INJECT.h"

static int present(const char *s)
{
    return s != 0 && s[0] != '\0';
}

static int same_scope(const char *a, const char *b)
{
    if (!present(a) || !present(b)) return 0;
    while (*a != '\0' && *b != '\0' && *a == *b) {
        ++a;
        ++b;
    }
    return *a == '\0' && *b == '\0';
}

IInjectResult i_inject_validate(const IInjectRequest *r)
{
    IInjectResult out;
    out.status = I_INJECT_HOLD;
    out.decision = "HOLD";
    out.reason = "Required authorization, evidence, or scope is missing.";

    if (r == 0 || !present(r->intent) || !present(r->source_reference) ||
        !present(r->provenance_reference) || !present(r->target) ||
        !present(r->compatibility_reference) || !present(r->approval_reference)) {
        out.status = I_INJECT_INVALID;
        out.reason = "Invalid request or missing traceability reference.";
        return out;
    }

    if (!same_scope(r->requested_scope, r->authorized_scope) ||
        !r->consent_verified || !r->security_verified || !r->safety_verified ||
        !r->ownership_verified || !r->approval_verified ||
        !r->compatibility_verified) {
        out.reason = "Protected gate or compatibility check failed; injection held.";
        return out;
    }

    out.status = I_INJECT_PROPOSED;
    out.decision = "PROPOSAL_ONLY";
    out.reason = "Validated for human review; no mutation or execution occurred.";
    return out;
}
