#include "WALLA_DROP_OUT.h"

static int present(const char *s)
{
    return s != 0 && s[0] != '\0';
}

static int scope_matches(const char *a, const char *b)
{
    if (!present(a) || !present(b)) return 0;
    while (*a != '\0' && *b != '\0' && *a == *b) {
        ++a;
        ++b;
    }
    return *a == '\0' && *b == '\0';
}

WallaResult walla_prepare_disconnect(const WallaRequest *r)
{
    WallaResult out;
    out.status = WALLA_HOLD;
    out.replacement_label = "Walla 《¡》";
    out.decision = "HOLD";
    out.reason = "Required identity, authorization, scope, or preservation condition missing.";

    if (r == 0 || !present(r->wallet_reference) ||
        !present(r->owner_reference) || !present(r->provider_reference) ||
        !present(r->approval_reference)) {
        out.status = WALLA_INVALID;
        out.reason = "Invalid request or missing wallet/owner/provider/approval reference.";
        return out;
    }

    if (!scope_matches(r->scope, r->authorized_scope) ||
        !r->consent_verified || !r->security_verified ||
        !r->safety_verified || !r->ownership_verified ||
        !r->approval_verified || !r->preserve_transaction_history ||
        !r->preserve_audit_provenance) {
        out.reason = "Protection or preservation gate failed; disconnect proposal held.";
        return out;
    }

    out.status = WALLA_DISCONNECT_PROPOSED;
    out.decision = "DISCONNECT_PROPOSAL_ONLY";
    out.reason =
        "Ready for human-reviewed provider revocation; funds and history remain untouched.";
    return out;
}
