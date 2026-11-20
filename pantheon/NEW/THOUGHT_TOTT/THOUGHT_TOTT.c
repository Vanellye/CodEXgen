#include "THOUGHT_TOTT.h"
#include <stdio.h>

static int present(const char *s) { return s != NULL && s[0] != '\0'; }

TottResult tott_build_lesson(const TottLesson *l, char *out, size_t cap) {
    int n;
    const char *status;
    if (l == NULL || out == NULL || cap == 0U) return TOTT_INVALID;
    out[0] = '\0';
    if (!l->authorized) return TOTT_NOT_AUTHORIZED;
    if (!present(l->lesson_id) || !present(l->correction_id) ||
        !present(l->source_reference) || !present(l->corrected_reference) ||
        !present(l->evidence_reference) || !present(l->observed_mistake) ||
        !present(l->correction) || !present(l->reusable_lesson) ||
        !present(l->scope)) return TOTT_PROVENANCE_MISSING;
    switch (l->status) {
        case TOTT_PROPOSED: status = "PROPOSED"; break;
        case TOTT_ACCEPTED:
            if (!present(l->reviewer) || !present(l->reviewed_at))
                return TOTT_UNREVIEWED;
            status = "ACCEPTED WITHIN STATED SCOPE"; break;
        case TOTT_CHALLENGED: status = "CHALLENGED; retain dissent"; break;
        case TOTT_SUPERSEDED: status = "SUPERSEDED; retain prior lesson"; break;
        default: return TOTT_INVALID;
    }
    n = snprintf(out, cap,
        "THOUGHT TOTT LEARNING NOTE\nLesson: %s\nCorrection: %s\n"
        "Source: %s\nCorrected record: %s\nEvidence: %s\n"
        "Observed mistake: %s\nCorrection made: %s\n"
        "Reusable lesson: %s\nScope: %s\nStatus: %s\n"
        "Reviewer: %s\nReviewed at: %s\n"
        "Limit: this lesson is contextual, revisable, and not a universal fact.\n",
        l->lesson_id, l->correction_id, l->source_reference,
        l->corrected_reference, l->evidence_reference, l->observed_mistake,
        l->correction, l->reusable_lesson, l->scope, status,
        present(l->reviewer) ? l->reviewer : "NOT RECORDED",
        present(l->reviewed_at) ? l->reviewed_at : "NOT RECORDED");
    if (n < 0 || (size_t)n >= cap) {
        out[0] = '\0';
        return TOTT_OUTPUT_TOO_SMALL;
    }
    return TOTT_OK;
}
