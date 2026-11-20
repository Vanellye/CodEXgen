#include "THOUGHT_TOTT.h"
#include <assert.h>
#include <string.h>

int main(void) {
    TottLesson l = {
        "lesson-1", "correction-7", "record-before", "record-after",
        "evidence-9", "A correction omitted source lineage.",
        "Restore the source reference and retain the earlier notice.",
        "Every correction must link to its source and preserve the prior notice.",
        "Correction notices in this module", "reviewer-1",
        "2026-11-12T00:00:00Z", TOTT_ACCEPTED, 1
    };
    char out[1024];
    assert(tott_build_lesson(&l, out, sizeof out) == TOTT_OK);
    assert(strstr(out, "ACCEPTED WITHIN STATED SCOPE") != NULL);
    assert(strstr(out, "not a universal fact") != NULL);
    l.authorized = 0;
    assert(tott_build_lesson(&l, out, sizeof out) == TOTT_NOT_AUTHORIZED);
    l.authorized = 1;
    l.evidence_reference = NULL;
    assert(tott_build_lesson(&l, out, sizeof out) == TOTT_PROVENANCE_MISSING);
    l.evidence_reference = "evidence-9";
    l.reviewer = NULL;
    assert(tott_build_lesson(&l, out, sizeof out) == TOTT_UNREVIEWED);
    l.status = TOTT_PROPOSED;
    assert(tott_build_lesson(&l, out, 4U) == TOTT_OUTPUT_TOO_SMALL);
    return 0;
}
