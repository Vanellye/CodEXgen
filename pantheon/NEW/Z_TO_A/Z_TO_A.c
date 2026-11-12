#include "Z_TO_A.h"

#include <stdio.h>
#include <string.h>

static int present(const char *value) {
    return value != NULL && value[0] != '\0';
}

static const char *evidence_label(Z2AEvidenceClass value) {
    switch (value) {
        case Z2A_EVIDENCE_SOURCE_REPORTED:
            return "SOURCE-REPORTED; not independently corroborated";
        case Z2A_EVIDENCE_CORROBORATED:
            return "CORROBORATED; inspect referenced supporting evidence";
        case Z2A_EVIDENCE_HYPOTHESIS:
            return "HYPOTHESIS; not established fact";
        case Z2A_EVIDENCE_INTERPRETATION:
            return "INTERPRETATION; not established fact";
        case Z2A_EVIDENCE_UNKNOWN:
        default:
            return "UNKNOWN; do not infer";
    }
}

Z2AStatus z2a_audit(const Z2AEnvelope *e,
                    char *output,
                    size_t capacity) {
    int written;

    if (e == NULL || output == NULL || capacity == 0U) {
        return Z2A_INVALID;
    }
    output[0] = '\0';

    if (!e->authorization_confirmed ||
        !present(e->purpose) ||
        !present(e->authorized_scope) ||
        !present(e->requested_scope) ||
        strcmp(e->authorized_scope, e->requested_scope) != 0) {
        return Z2A_NOT_AUTHORIZED;
    }
    if (e->data_class != Z2A_DATA_PUBLIC &&
        e->data_class != Z2A_DATA_CONSENTED_AGGREGATE) {
        return Z2A_UNSUPPORTED_DATA;
    }
    if (!present(e->source_id) || !present(e->record_id) ||
        !present(e->original_forum_ref) || !present(e->provenance_ref)) {
        return Z2A_PROVENANCE_MISSING;
    }
    if (!present(e->evidence_ref) || !present(e->claim_or_output)) {
        return Z2A_EVIDENCE_MISSING;
    }

    written = snprintf(
        output, capacity,
        "Z_TO_A REVERSE AUDIT\\n"
        "Claim/output: %s\\n"
        "Produced from record: %s\\n"
        "Source: %s\\n"
        "Original forum: %s\\n"
        "Provenance reference: %s\\n"
        "Evidence reference: %s\\n"
        "Evidence class: %s\\n"
        "Purpose: %s\\n"
        "Known uncertainty: %s\\n"
        "Audit direction: output -> evidence -> provenance -> original forum\\n"
        "LIMIT: references and authorization are caller-supplied; this formatter "
        "does not verify their truth or authenticity. Preserve source records; "
        "do not upgrade uncertainty into fact.\\n",
        e->claim_or_output,
        e->record_id,
        e->source_id,
        e->original_forum_ref,
        e->provenance_ref,
        e->evidence_ref,
        evidence_label(e->evidence_class),
        e->purpose,
        present(e->known_uncertainty) ? e->known_uncertainty : "NOT RECORDED"
    );

    if (written < 0 || (size_t)written >= capacity) {
        output[0] = '\0';
        return Z2A_OUTPUT_TOO_SMALL;
    }
    return Z2A_OK;
}
