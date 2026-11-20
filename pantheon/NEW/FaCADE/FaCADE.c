#include "FaCADE.h"

#include <stdio.h>

static int present(const char *value) {
    return value != NULL && value[0] != '\0';
}

static const char *relation_name(FaCADE_Relation relation) {
    switch (relation) {
        case FACADE_RELATION_RESTORES: return "RESTORES-REFERENCE";
        case FACADE_RELATION_CORRECTS: return "CORRECTS-PRIOR-NOTICE";
        case FACADE_RELATION_SUPERSEDES: return "SUPERSEDES-REPRESENTATION";
        case FACADE_RELATION_CONTRADICTS: return "CONTRADICTS";
        case FACADE_RELATION_DERIVED_FROM: return "DERIVED-FROM";
        default: return NULL;
    }
}

FaCADE_Status facade_build_correction(const FaCADE_Correction *correction,
                                      char *output,
                                      size_t output_capacity) {
    int written;
    const char *relation;

    if (correction == NULL || output == NULL || output_capacity == 0U) {
        return FACADE_STATUS_INVALID;
    }
    output[0] = '\0';

    if (!correction->source_authorized) {
        return FACADE_STATUS_NOT_AUTHORIZED;
    }
    if (!present(correction->notice_id) ||
        !present(correction->source_record_id) ||
        !present(correction->target_record_id) ||
        !present(correction->evidence_reference) ||
        !present(correction->reason) ||
        !present(correction->recorded_at) ||
        !present(correction->reviewer_id)) {
        return FACADE_STATUS_PROVENANCE_MISSING;
    }

    relation = relation_name(correction->relation);
    if (relation == NULL) return FACADE_STATUS_INVALID;
    if (!correction->link_verified) return FACADE_STATUS_LINK_UNVERIFIED;

    written = snprintf(output, output_capacity,
        "FACADE CORRECTION PROPOSAL\n"
        "Notice: %s\nRelation: %s\n"
        "Source record: %s\nTarget record: %s\n"
        "Evidence reference: %s\nReason: %s\n"
        "Recorded at: %s\nReviewed by: %s\n"
        "Disposition: ADDITIVE LINK; preserve source and prior notice.\n"
        "Portal: direction to the referenced record only; not a voice or identity claim.\n"
        "Limit: link verification does not prove the underlying account true.\n",
        correction->notice_id, relation,
        correction->source_record_id, correction->target_record_id,
        correction->evidence_reference, correction->reason,
        correction->recorded_at, correction->reviewer_id);

    if (written < 0 || (size_t)written >= output_capacity) {
        output[0] = '\0';
        return FACADE_STATUS_OUTPUT_TOO_SMALL;
    }
    return FACADE_STATUS_OK;
}
