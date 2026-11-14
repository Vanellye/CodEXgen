#include "NEW.h"

#include <stdio.h>

static int present(const char *value) {
    return value != NULL && value[0] != '\0';
}

static const char *evidence_label(NewEvidenceStatus status) {
    switch (status) {
        case NEW_EVIDENCE_SOURCE_REPORTED:
            return "SOURCE-REPORTED; not independently corroborated";
        case NEW_EVIDENCE_INDEPENDENTLY_CORROBORATED:
            return "INDEPENDENTLY CORROBORATED; see supporting record";
        case NEW_EVIDENCE_HYPOTHESIS:
            return "HYPOTHESIS; not an established fact";
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

    if (!pons_c_proof_is_valid(record->pons_proof, "pantheon.new")) {
        return NEW_STATUS_PONS_HOLD;
    }

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

    if (record->evidence_status == NEW_EVIDENCE_INDEPENDENTLY_CORROBORATED &&
        (!present(record->proof_reference) ||
         !present(record->proof_method) ||
         !present(record->proof_checked_at))) {
        return NEW_STATUS_PROOF_REFERENCE_MISSING;
    }

    written = snprintf(output, output_capacity,
        "UNREVIEWED EVIDENCE NARRATIVE\n"
        "Claim status: %s\n"
        "Source: %s\nRecord: %s\nCaptured: %s\n"
        "Provenance digest (origin/integrity reference): %s\n"
        "Permission basis: %s\nPurpose: %s\n"
        "Source statement (not upgraded to fact): %s\n"
        "Proof reference: %s\nProof method: %s\nProof checked at: %s\n"
        "Interpretation: NOT ESTABLISHED BY THIS MODULE.\n"
        "Limits: A digest can help detect alteration; it does not prove "
        "truth, consent, completeness, or representativeness. Corroboration "
        "supports a claim but does not make it infallible. Hypotheses remain "
        "hypotheses. Human review and uncertainty disclosure are required.\n",
        label, record->source_id, record->record_id, record->captured_at,
        record->provenance_digest, record->permission_basis, record->purpose,
        record->content_summary,
        present(record->proof_reference) ? record->proof_reference : "NONE",
        present(record->proof_method) ? record->proof_method : "NONE",
        present(record->proof_checked_at) ? record->proof_checked_at : "NONE");

    if (written < 0 || (size_t)written >= output_capacity) {
        output[0] = '\0';
        return NEW_STATUS_OUTPUT_TOO_SMALL;
    }
    return NEW_STATUS_OK;
}
