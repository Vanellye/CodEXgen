#include "NEW.h"

#include <stdio.h>

static int present(const char *value) {
    return value != NULL && value[0] != '\0';
}

NewStatus new_build_narrative(const NewRecord *record,
                              char *output,
                              size_t output_capacity) {
    int written;

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

    written = snprintf(output, output_capacity,
        "UNVERIFIED NARRATIVE PROPOSAL\n"
        "Source: %s\nRecord: %s\nCaptured: %s\n"
        "Provenance digest: %s\nPurpose: %s\n"
        "Observation for human review: %s\n"
        "Limit: This is an interpretation, not an established fact. "
        "Verify it against the source and preserve uncertainty before use.\n",
        record->source_id, record->record_id, record->captured_at,
        record->provenance_digest, record->purpose, record->content_summary);

    if (written < 0 || (size_t)written >= output_capacity) {
        output[0] = '\0';
        return NEW_STATUS_OUTPUT_TOO_SMALL;
    }
    return NEW_STATUS_OK;
}
