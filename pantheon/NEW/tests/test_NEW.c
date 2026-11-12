#include "NEW.h"

#include <assert.h>
#include <string.h>

int main(void) {
    char output[1024];
    NewRecord record = {
        "public-civic-dataset", "record-001", "public-use license",
        "aggregate trend analysis", "2026-11-11T00:00:00Z",
        "sha256:example-digest",
        "Aggregated count increased in the reporting period.",
        NEW_DATA_PUBLIC, 1
    };

    assert(new_build_narrative(&record, output, sizeof(output)) == NEW_STATUS_OK);
    assert(strstr(output, "UNVERIFIED NARRATIVE PROPOSAL") != NULL);

    record.authorization_confirmed = 0;
    assert(new_build_narrative(&record, output, sizeof(output)) == NEW_STATUS_NOT_AUTHORIZED);

    record.authorization_confirmed = 1;
    record.data_class = NEW_DATA_UNSPECIFIED;
    assert(new_build_narrative(&record, output, sizeof(output)) == NEW_STATUS_UNSUPPORTED_DATA);

    record.data_class = NEW_DATA_PUBLIC;
    record.provenance_digest = NULL;
    assert(new_build_narrative(&record, output, sizeof(output)) == NEW_STATUS_PROVENANCE_MISSING);

    return 0;
}
