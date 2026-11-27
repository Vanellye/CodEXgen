#include "Z_TO_A.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static Z2AEnvelope valid_envelope(void) {
    Z2AEnvelope e = {
        "source-01", "record-09", "forum://origin/09",
        "prov://chain/09", "evidence://item/09",
        "A claim to audit", "research", "aggregate-only", "aggregate-only",
        "sample is incomplete", Z2A_DATA_CONSENTED_AGGREGATE,
        Z2A_EVIDENCE_SOURCE_REPORTED, 1
    };
    return e;
}

int main(void) {
    Z2AEnvelope e = valid_envelope();
    char output[2048];

    assert(z2a_audit(&e, output, sizeof(output)) == Z2A_OK);
    assert(strstr(output, "output -> evidence -> provenance -> original forum") != NULL);
    assert(strstr(output, "SOURCE-REPORTED") != NULL);
    assert(strstr(output, "sample is incomplete") != NULL);
    assert(strstr(output, "does not verify their truth") != NULL);

    e.authorization_confirmed = 0;
    assert(z2a_audit(&e, output, sizeof(output)) == Z2A_NOT_AUTHORIZED);

    e = valid_envelope();
    e.requested_scope = "individual-profiling";
    assert(z2a_audit(&e, output, sizeof(output)) == Z2A_NOT_AUTHORIZED);

    e = valid_envelope();
    e.data_class = Z2A_DATA_UNSPECIFIED;
    assert(z2a_audit(&e, output, sizeof(output)) == Z2A_UNSUPPORTED_DATA);

    e = valid_envelope();
    e.original_forum_ref = "";
    assert(z2a_audit(&e, output, sizeof(output)) == Z2A_PROVENANCE_MISSING);

    e = valid_envelope();
    e.evidence_ref = NULL;
    assert(z2a_audit(&e, output, sizeof(output)) == Z2A_EVIDENCE_MISSING);

    e = valid_envelope();
    assert(z2a_audit(&e, output, 8U) == Z2A_OUTPUT_TOO_SMALL);
    assert(output[0] == '\0');

    puts("PASS: Z_TO_A contract tests");
    return 0;
}
