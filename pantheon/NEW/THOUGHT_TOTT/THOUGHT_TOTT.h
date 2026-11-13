#ifndef ERIA_THOUGHT_TOTT_H
#define ERIA_THOUGHT_TOTT_H
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    TOTT_PROPOSED = 1,
    TOTT_ACCEPTED = 2,
    TOTT_CHALLENGED = 3,
    TOTT_SUPERSEDED = 4
} TottStatus;

typedef enum {
    TOTT_OK = 0,
    TOTT_INVALID = 1,
    TOTT_NOT_AUTHORIZED = 2,
    TOTT_PROVENANCE_MISSING = 3,
    TOTT_UNREVIEWED = 4,
    TOTT_OUTPUT_TOO_SMALL = 5
} TottResult;

typedef struct {
    const char *lesson_id;
    const char *correction_id;
    const char *source_reference;
    const char *corrected_reference;
    const char *evidence_reference;
    const char *observed_mistake;
    const char *correction;
    const char *reusable_lesson;
    const char *scope;
    const char *reviewer;
    const char *reviewed_at;
    TottStatus status;
    int authorized;
} TottLesson;

/* Formats a traceable learning note. It does not train a model or mutate records.
 * ACCEPTED means reviewed within the stated scope, not universally true. */
TottResult tott_build_lesson(const TottLesson *lesson, char *output,
                             size_t output_capacity);
#ifdef __cplusplus
}
#endif
#endif
