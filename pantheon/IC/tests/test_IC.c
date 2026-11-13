#include <assert.h>
#include "IC.h"

int main(void) {
    ICAeddChecks complete_aedd = { 1, 1, 1, 1, 1, 1, 1 };
    ICAeddChecks missing_consent = { 1, 0, 1, 1, 1, 1, 1 };
    ICGate observe = { IC_STAGE_PENDING, IC_APPROVAL_UNSET, 0 };
    ICGate protected_gate = { IC_STAGE_PENDING, IC_APPROVAL_UNSET, 1 };
    ICGate denied_gate = { IC_STAGE_PENDING, IC_APPROVAL_DENIED, 0 };

    /* Aðð fails closed unless all seven checks are present. */
    assert(ic_aedd_qualifies(&complete_aedd));
    assert(!ic_aedd_qualifies(&missing_consent));
    assert(!ic_aedd_qualifies(0));

    /* Ordinary read-only validation can start when dependencies pass. */
    assert(ic_can_start(&observe, 1));
    assert(!ic_can_start(&observe, 0));
    assert(ic_start(&observe, 1));
    assert(!ic_start(&observe, 1));
    assert(ic_finish(&observe, 1));
    assert(observe.state == IC_STAGE_PASSED);

    /* Passing checks alone never authorizes publication. */
    assert(!ic_can_publish(&observe, 1));

    /* A protected gate holds until its own explicit approval is granted. */
    assert(!ic_can_start(&protected_gate, 1));
    assert(!ic_start(&protected_gate, 1));
    assert(protected_gate.state == IC_STAGE_BLOCKED);

    protected_gate.state = IC_STAGE_PENDING;
    protected_gate.approval = IC_APPROVAL_GRANTED;
    assert(ic_can_start(&protected_gate, 1));
    assert(ic_start(&protected_gate, 1));
    assert(ic_finish(&protected_gate, 1));
    assert(ic_can_publish(&protected_gate, 1));
    assert(!ic_can_publish(&protected_gate, 0));

    /* Explicit denial is fail-closed even without a protected flag. */
    assert(!ic_can_start(&denied_gate, 1));
    assert(!ic_start(&denied_gate, 1));
    assert(denied_gate.state == IC_STAGE_BLOCKED);

    /* Failed checks cannot be promoted to publication. */
    observe.state = IC_STAGE_RUNNING;
    assert(ic_finish(&observe, 0));
    assert(observe.state == IC_STAGE_FAILED);
    assert(!ic_can_publish(&observe, 1));

    assert(!ic_can_start(0, 1));
    assert(!ic_start(0, 1));
    assert(!ic_finish(0, 1));
    assert(!ic_can_publish(0, 1));
    return 0;
}
