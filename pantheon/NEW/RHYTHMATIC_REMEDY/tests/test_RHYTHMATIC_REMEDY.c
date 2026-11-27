#include "../RHYTHMATIC_REMEDY.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static RrCycle sample_cycle(void) {
    RrCycle cycle = {
        "cycle-001",
        "owner-ref-001",
        "pattern-ref-001",
        "evidence-ref-001",
        "2026-11-11T00:00:00Z",
        "recurring over-allocation",
        "balanced owner-defined allocation",
        "pause, review, and reallocate with consent",
        "frequency and cause are not yet fully established",
        65U,
        1,
        1
    };
    return cycle;
}

int main(void) {
    RrCycle cycle = sample_cycle();
    char output[2048];

    assert(rr_advance(&cycle, RR_OBSERVE, RR_ACCOUNT,
                     output, sizeof(output)) == RR_OK);
    assert(strstr(output, "Observe -> Account") != NULL);
    assert(strstr(output, "not a truth or worth score") != NULL);
    assert(strstr(output, "owner retains control") != NULL);

    assert(rr_advance(&cycle, RR_OBSERVE, RR_REFLECT,
                     output, sizeof(output)) == RR_BAD_TRANSITION);

    cycle.owner_authorized = 0;
    assert(rr_advance(&cycle, RR_OBSERVE, RR_ACCOUNT,
                     output, sizeof(output)) == RR_NOT_AUTHORIZED);
    cycle.owner_authorized = 1;

    cycle.evidence_reference = "";
    assert(rr_advance(&cycle, RR_OBSERVE, RR_ACCOUNT,
                     output, sizeof(output)) == RR_PROVENANCE_MISSING);
    cycle.evidence_reference = "evidence-ref-001";

    assert(rr_advance(&cycle, RR_RECONCILE, RR_OBSERVE,
                     output, sizeof(output)) == RR_OK);

    assert(rr_advance(&cycle, RR_OBSERVE, RR_ACCOUNT,
                     output, 8U) == RR_OUTPUT_TOO_SMALL);

    puts("PASS: TeSt rhythmatic remedy contract tests");
    return 0;
}
