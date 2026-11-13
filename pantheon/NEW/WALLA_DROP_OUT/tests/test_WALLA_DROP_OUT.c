#include <assert.h>
#include <stdio.h>
#include "WALLA_DROP_OUT.h"

static WallaRequest valid_request(void)
{
    WallaRequest r = {
        "wallet:local-01", "owner:account-01", "provider:service-01",
        "wallet.disconnect", "wallet.disconnect", "approval:case-11",
        1, 1, 1, 1, 1, 1, 1
    };
    return r;
}

int main(void)
{
    WallaRequest r = valid_request();
    WallaResult out = walla_prepare_disconnect(&r);
    assert(out.status == WALLA_DISCONNECT_PROPOSED);
    assert(out.replacement_label[0] == 'W');

    r = valid_request(); r.consent_verified = 0;
    assert(walla_prepare_disconnect(&r).status == WALLA_HOLD);
    r = valid_request(); r.security_verified = 0;
    assert(walla_prepare_disconnect(&r).status == WALLA_HOLD);
    r = valid_request(); r.safety_verified = 0;
    assert(walla_prepare_disconnect(&r).status == WALLA_HOLD);
    r = valid_request(); r.ownership_verified = 0;
    assert(walla_prepare_disconnect(&r).status == WALLA_HOLD);
    r = valid_request(); r.approval_verified = 0;
    assert(walla_prepare_disconnect(&r).status == WALLA_HOLD);
    r = valid_request(); r.preserve_transaction_history = 0;
    assert(walla_prepare_disconnect(&r).status == WALLA_HOLD);
    r = valid_request(); r.preserve_audit_provenance = 0;
    assert(walla_prepare_disconnect(&r).status == WALLA_HOLD);
    r = valid_request(); r.authorized_scope = "wallet.transfer";
    assert(walla_prepare_disconnect(&r).status == WALLA_HOLD);
    assert(walla_prepare_disconnect(0).status == WALLA_INVALID);

    puts("PASS: Walla disconnect protection tests");
    return 0;
}
