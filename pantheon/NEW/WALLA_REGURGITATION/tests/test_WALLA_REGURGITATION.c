#include <assert.h>
#include <stdio.h>
#include "WALLA_REGURGITATION.h"

static WallaTruRequest valid_request(void)
{
    WallaTruRequest r = {
        "proposal-17", "wallet-ref-3", "owner-ref-8", "origin-22",
        "provenance-22", "owner-record-5", "system-record-5",
        "wallet.reconcile", "wallet.reconcile", "review-91",
        WALLA_EVIDENCE_VERIFIED_REFERENCE,
        1, 1, 1, 1, 1, 1, 1, 1
    };
    return r;
}

int main(void)
{
    WallaTruRequest r = valid_request();
    WallaTruResult out = walla_tru_meet(&r);
    assert(out.status == WALLA_TRU_READY_FOR_REVIEW);
    assert(out.pinned_proposal_id[0] == 'p');

    r = valid_request(); r.owner_confirms_match = 0;
    assert(walla_tru_meet(&r).status == WALLA_TRU_HOLD);
    r = valid_request(); r.system_record_available = 0;
    assert(walla_tru_meet(&r).status == WALLA_TRU_HOLD);
    r = valid_request(); r.consent_verified = 0;
    assert(walla_tru_meet(&r).status == WALLA_TRU_HOLD);
    r = valid_request(); r.security_verified = 0;
    assert(walla_tru_meet(&r).status == WALLA_TRU_HOLD);
    r = valid_request(); r.safety_verified = 0;
    assert(walla_tru_meet(&r).status == WALLA_TRU_HOLD);
    r = valid_request(); r.ownership_verified = 0;
    assert(walla_tru_meet(&r).status == WALLA_TRU_HOLD);
    r = valid_request(); r.approval_verified = 0;
    assert(walla_tru_meet(&r).status == WALLA_TRU_HOLD);
    r = valid_request(); r.transaction_history_preserved = 0;
    assert(walla_tru_meet(&r).status == WALLA_TRU_HOLD);
    r = valid_request(); r.authorized_scope = "wallet.disconnect";
    assert(walla_tru_meet(&r).status == WALLA_TRU_HOLD);
    r = valid_request(); r.evidence_class = WALLA_EVIDENCE_UNSPECIFIED;
    assert(walla_tru_meet(&r).status == WALLA_TRU_INVALID);
    assert(walla_tru_meet(0).status == WALLA_TRU_INVALID);

    puts("PASS: Walla TRU meet-point tests");
    return 0;
}
