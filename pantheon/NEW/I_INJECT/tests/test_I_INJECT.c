#include <assert.h>
#include <stdio.h>
#include "I_INJECT.h"

static IInjectRequest valid_request(void)
{
    IInjectRequest r = {
        "add reviewed optional field", "source:record-7", "prov:sha256:abc",
        "report.preview", "report.preview", "report.preview", "compat:review-2",
        "approval:ticket-9", 1, 1, 1, 1, 1, 1
    };
    return r;
}

int main(void)
{
    IInjectRequest r = valid_request();
    IInjectResult out = i_inject_validate(&r);
    assert(out.status == I_INJECT_PROPOSED);
    assert(out.decision[0] == 'P');

    r = valid_request(); r.consent_verified = 0;
    assert(i_inject_validate(&r).status == I_INJECT_HOLD);
    r = valid_request(); r.security_verified = 0;
    assert(i_inject_validate(&r).status == I_INJECT_HOLD);
    r = valid_request(); r.safety_verified = 0;
    assert(i_inject_validate(&r).status == I_INJECT_HOLD);
    r = valid_request(); r.ownership_verified = 0;
    assert(i_inject_validate(&r).status == I_INJECT_HOLD);
    r = valid_request(); r.approval_verified = 0;
    assert(i_inject_validate(&r).status == I_INJECT_HOLD);
    r = valid_request(); r.compatibility_verified = 0;
    assert(i_inject_validate(&r).status == I_INJECT_HOLD);
    r = valid_request(); r.authorized_scope = "other.scope";
    assert(i_inject_validate(&r).status == I_INJECT_HOLD);
    r = valid_request(); r.provenance_reference = "";
    assert(i_inject_validate(&r).status == I_INJECT_INVALID);
    assert(i_inject_validate(0).status == I_INJECT_INVALID);

    puts("PASS: I-INJECT protection contract tests");
    return 0;
}
