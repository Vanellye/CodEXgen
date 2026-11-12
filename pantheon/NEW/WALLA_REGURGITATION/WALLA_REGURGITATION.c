#include "WALLA_REGURGITATION.h"

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

WallaTruResult walla_tru_meet(const WallaTruRequest *r)
{
    WallaTruResult out;
    out.status = WALLA_TRU_HOLD;
    out.pinned_proposal_id = r != 0 ? r->proposal_id : 0;
    out.meet_point = "TRU_MEET_POINT";
    out.decision = "HOLD";
    out.reason = "Owner/system records or required protection evidence need review.";

    if (r == 0 || !present(r->proposal_id) ||
        !present(r->wallet_reference) || !present(r->owner_reference) ||
        !present(r->origin_record_reference) ||
        !present(r->provenance_reference) ||
        !present(r->owner_record_reference) ||
        !present(r->system_record_reference) ||
        !present(r->review_reference) ||
        r->evidence_class < WALLA_EVIDENCE_VERIFIED_REFERENCE ||
        r->evidence_class > WALLA_EVIDENCE_INTERPRETATION) {
        out.status = WALLA_TRU_INVALID;
        out.reason = "Invalid or incomplete pinned proposal/reconciliation references.";
        return out;
    }

    if (!same_scope(r->requested_scope, r->authorized_scope) ||
        !r->owner_confirms_match || !r->system_record_available ||
        !r->consent_verified || !r->security_verified ||
        !r->safety_verified || !r->ownership_verified ||
        !r->approval_verified || !r->transaction_history_preserved) {
        out.reason = "TRU meet point unresolved; a protection or reconciliation gate failed.";
        return out;
    }

    out.status = WALLA_TRU_READY_FOR_REVIEW;
    out.decision = "RECONCILED_PROPOSAL_READY_FOR_HUMAN_REVIEW";
    out.reason = "References align within declared scope; no wallet reconnection or financial action occurred.";
    return out;
}
