#include <assert.h>
#include <stdio.h>
#include "Y_BYPASS.h"

static YBypassRequest valid_request(void)
{
    YBypassRequest r = {
        Y_INPUT_NULL, "optional_caption", "report.preview", "report.preview",
        "caption is optional", "approval-42", 1, 1, 1, 1, 1, 1
    };
    return r;
}

int main(void)
{
    YBypassRequest r = valid_request();
    YBypassResult out = y_bypass_resolve(&r);
    assert(out.status == Y_STATUS_BYPASS_Y);
    assert(out.token[0] == 'Y');

    r = valid_request(); r.consent_verified = 0;
    assert(y_bypass_resolve(&r).status == Y_STATUS_DENIED);

    r = valid_request(); r.security_verified = 0;
    assert(y_bypass_resolve(&r).status == Y_STATUS_DENIED);

    r = valid_request(); r.safety_verified = 0;
    assert(y_bypass_resolve(&r).status == Y_STATUS_DENIED);

    r = valid_request(); r.ownership_verified = 0;
    assert(y_bypass_resolve(&r).status == Y_STATUS_DENIED);

    r = valid_request(); r.approval_verified = 0;
    assert(y_bypass_resolve(&r).status == Y_STATUS_DENIED);

    r = valid_request(); r.field_is_optional = 0;
    assert(y_bypass_resolve(&r).status == Y_STATUS_DENIED);

    r = valid_request(); r.allowed_scope = "different.scope";
    assert(y_bypass_resolve(&r).status == Y_STATUS_DENIED);

    r = valid_request(); r.authorization_ref = "";
    assert(y_bypass_resolve(&r).status == Y_STATUS_INVALID);

    r = valid_request(); r.input_kind = (YInputKind)99;
    assert(y_bypass_resolve(&r).status == Y_STATUS_INVALID);

    puts("PASS: Y bypass protection contract tests");
    return 0;
}
