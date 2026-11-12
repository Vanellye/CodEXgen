#include "NEW.h"

#include <stdio.h>

static int present(const char *value) {
    return value != NULL && value[0] != '\0';
}

static const char *evidence_label(NewEvidenceStatus status) {
    switch (status) {
        case NEW_EVIDENCE_SOURCE_REPORTED:
            return "SOURCE-REPORTED (not independently verified)";
        case NEW_EVIDENCE_INDEPENDENTLY_VERIFIED:
            return "INDEPENDENTLY VERIFIED (see verifier metadata)";
        case NEW_EVIDENCE_HYPOTHESIS:
            return "HYPOTHESIS (not an established fact)";
        default:
            return NULL;
    }
}

NewStatus new_build_narrative(const NewRecord *record,
                              char *output,
                              size_t output_capacity) {
    int written;
    const char *label;

    if (record == NULL || output == NULL || output_capacity == 0U) {
        return NEW_STATUS_INVALID;
    }
    output[0] = '\0';

    if (!record->authorization_confirmed ||
        !present(record->permission_basis) ||
        !present(record->purpose)) {
        return NEW_STATUS_NOT_AUTHORIZED;
    }

    if (record->data_class != NEW_DATA_PUBLIC &&
        record->data_class != NEW_DATA_CONSENTED_AGGREGATE) {
        return NEW_STATUS_UNSUPPORTED_DATA;
    }

    if (!present(record->source_id) ||
        !present(record->record_id) ||
        !present(record->captured_at) ||
        !present(record->provenance_digest)) {
        return NEW_STATUS_PROVENANCE_MISSING;
    }

    if (!present(record->content_summary)) {
        return NEW_STATUS_INVALID;
    }

    label = evidence_label(record->evidence_status);
    if (label == NULL) {
        return NEW_STATUS_INVALID;
    }

    if (record->evidence_status == NEW_EVIDENCE_INDEPENDENTLY_VERIFIED &&
        (!present(record->verifier_id) ||
         !present(record->verification_method) ||
         !present(record->verified_at))) {
        return NEW_STATUS_VERIFICATION_DETAILS_MISSING;
    }

    written = snprintf(output, output_capacity,
        "UNREVIEWED NARRATIVE PROPOSAL\n"
        "Evidence classification: %s\n"
        "Source: %s\nRecord: %s\nCaptured: %s\n"
        "Provenance digest: %s\nPermission basis: %s\nPurpose: %s\n"
        "Evidence statement (not rewritten as fact): %s\n"
        "%s"
        "Interpretation: NOT PROVIDED BY THIS MODULE; human analysis required.\n"
        "Limits: A provenance digest checks integrity, not truth, consent, "
        "or completeness. Source-reported content is not independent proof. "
        "A hypothesis is not a fact. Human review is required before use.\n",
        label, record->source_id, record->record_id, record->captured_at,
        record->provenance_digest, record->permission_basis, record->purpose,
        record->content_summary,
        record->evidence_status == NEW_EVIDENCE_INDEPENDENTLY_VERIFIED
            ? "Verifier: " : "");

    if (written < 0 || (size_t)written >= output_capacity) {
        output[0] = '\0';
        return NEW_STATUS_OUTPUT_TOO_SMALL;
    }

    if (record->evidence_status == NEW_EVIDENCE_INDEPENDENTLY_VERIFIED) {
        size_t used = (size_t)written;
        int extra = snprintf(output + used, output_capacity - used,
            "Verification method: %s\nVerified at: %s\n",
            record->verification_method, record->verified_at);
        if (extra < 0 || (size_t)extra >= output_capacity - used) {
            output[0] = '\0';
            return NEW_STATUS_OUTPUT_TOO_SMALL;
        }
        /* verifier_id is retained as a separate provenance field in the input;
         * print it explicitly in a stable, escaped-by-format-string position. */
        used += (size_t)extra;
        extra = snprintf(output + used, output_capacity - used,
            "Verifier ID: %s\n", record->verifier_id);
        if (extra < 0 || (size_t)extra >= output_capacity - used) {
            output[0] = '\0';
            return NEW_STATUS_OUTPUT_TOO_SMALL;
        }
    }

    return NEW_STATUS_OK;
}
