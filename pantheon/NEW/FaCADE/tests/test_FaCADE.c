#include "FaCADE.h"

#include <assert.h>
#include <string.h>

int main(void) {
    FaCADE_Correction correction = {
        .notice_id = "notice-17",
        .source_record_id = "record-original",
        .target_record_id = "record-corrected",
        .evidence_reference = "evidence-22",
        .reason = "Earlier notice omitted a linked public record.",
        .recorded_at = "2026-11-11T18:00:00Z",
        .reviewer_id = "reviewer-1",
        .relation = FACADE_RELATION_CORRECTS,
        .source_authorized = 1,
        .link_verified = 1
    };
    char output[1024];

    assert(facade_build_correction(&correction, output, sizeof(output)) ==
           FACADE_STATUS_OK);
    assert(strstr(output, "CORRECTS-PRIOR-NOTICE") != NULL);
    assert(strstr(output, "ADDITIVE LINK") != NULL);
    assert(strstr(output, "not a voice or identity claim") != NULL);

    correction.relation = FACADE_RELATION_RESTORES;
    assert(facade_build_correction(&correction, output, sizeof(output)) ==
           FACADE_STATUS_OK);
    assert(strstr(output, "RESTORES-REFERENCE") != NULL);

    correction.source_authorized = 0;
    assert(facade_build_correction(&correction, output, sizeof(output)) ==
           FACADE_STATUS_NOT_AUTHORIZED);

    correction.source_authorized = 1;
    correction.link_verified = 0;
    assert(facade_build_correction(&correction, output, sizeof(output)) ==
           FACADE_STATUS_LINK_UNVERIFIED);

    correction.link_verified = 1;
    correction.evidence_reference = NULL;
    assert(facade_build_correction(&correction, output, sizeof(output)) ==
           FACADE_STATUS_PROVENANCE_MISSING);

    correction.evidence_reference = "evidence-22";
    assert(facade_build_correction(&correction, output, 4U) ==
           FACADE_STATUS_OUTPUT_TOO_SMALL);

    return 0;
}
