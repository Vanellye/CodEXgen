#include "NEW.h"

#include <assert.h>
#include <string.h>

static int test_digest(const unsigned char *bytes, size_t length, char output[65], void *context) {
    size_t i;
    const char *digest = (const char *)context;
    if (bytes == NULL || length == 0U || digest == NULL) return 0;
    for (i = 0; i < 64U; ++i) output[i] = digest[i];
    output[64] = '\0';
    return 1;
}

static PonsCProof verified_proof;

static NewRecord sample_record(void) {
    NewRecord record = {
        .source_id = "public-civic-dataset",
        .record_id = "record-001",
        .permission_basis = "public-use license",
        .purpose = "aggregate trend analysis",
        .captured_at = "2026-11-11T00:00:00Z",
        .provenance_digest = "sha256:example-digest",
        .content_summary = "Aggregated count increased in the reporting period.",
        .proof_reference = NULL,
        .proof_method = NULL,
        .proof_checked_at = NULL,
        .data_class = NEW_DATA_PUBLIC,
        .evidence_status = NEW_EVIDENCE_SOURCE_REPORTED,
        .authorization_confirmed = 1,
        .pons_proof = &verified_proof
    };
    return record;
}

int main(void) {
    char output[2048];
    NewRecord record;
    static const unsigned char source[] = "fixture";
    static const char digest[] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    PonsCManifestPin pin = {
        "pantheon.new", "reviewed-ref", "pantheon/NEW/NEW.c", digest,
        PONS_CANONICAL_ANCHOR_ID, PONS_CANONICAL_ANCHOR_REF
    };
    assert(pons_c_verify(&pin, source, sizeof(source) - 1U,
                         test_digest, (void *)digest, &verified_proof) == PONS_C_VERIFIED);
    record = sample_record();

    record.pons_proof = NULL;
    assert(new_build_narrative(&record, output, sizeof(output)) == NEW_STATUS_PONS_HOLD);
    record.pons_proof = &verified_proof;

    assert(new_build_narrative(&record, output, sizeof(output)) == NEW_STATUS_OK);
    assert(strstr(output, "SOURCE-REPORTED") != NULL);
    assert(strstr(output, "Provenance digest") != NULL);
    assert(strstr(output, "Proof reference: NONE") != NULL);
    assert(strstr(output, "not upgraded to fact") != NULL);

    record.evidence_status = NEW_EVIDENCE_HYPOTHESIS;
    assert(new_build_narrative(&record, output, sizeof(output)) == NEW_STATUS_OK);
    assert(strstr(output, "HYPOTHESIS") != NULL);

    record.evidence_status = NEW_EVIDENCE_INDEPENDENTLY_CORROBORATED;
    assert(new_build_narrative(&record, output, sizeof(output)) ==
           NEW_STATUS_PROOF_REFERENCE_MISSING);

    record.proof_reference = "public-report-2026-17";
    record.proof_method = "independent cross-check against published dataset";
    record.proof_checked_at = "2026-11-11T12:00:00Z";
    assert(new_build_narrative(&record, output, sizeof(output)) == NEW_STATUS_OK);
    assert(strstr(output, "INDEPENDENTLY CORROBORATED") != NULL);
    assert(strstr(output, "public-report-2026-17") != NULL);

    record.authorization_confirmed = 0;
    assert(new_build_narrative(&record, output, sizeof(output)) ==
           NEW_STATUS_NOT_AUTHORIZED);

    record.authorization_confirmed = 1;
    record.data_class = NEW_DATA_UNSPECIFIED;
    assert(new_build_narrative(&record, output, sizeof(output)) ==
           NEW_STATUS_UNSUPPORTED_DATA);

    record.data_class = NEW_DATA_PUBLIC;
    record.provenance_digest = NULL;
    assert(new_build_narrative(&record, output, sizeof(output)) ==
           NEW_STATUS_PROVENANCE_MISSING);

    record.provenance_digest = "sha256:example-digest";
    assert(new_build_narrative(&record, output, 8U) ==
           NEW_STATUS_OUTPUT_TOO_SMALL);

    return 0;
}
