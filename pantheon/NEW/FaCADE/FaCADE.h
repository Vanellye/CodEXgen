#ifndef ERIA_PANTHEON_FACADE_H
#define ERIA_PANTHEON_FACADE_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    FACADE_RELATION_RESTORES = 1,
    FACADE_RELATION_CORRECTS = 2,
    FACADE_RELATION_SUPERSEDES = 3,
    FACADE_RELATION_CONTRADICTS = 4,
    FACADE_RELATION_DERIVED_FROM = 5
} FaCADE_Relation;

typedef enum {
    FACADE_STATUS_OK = 0,
    FACADE_STATUS_INVALID = 1,
    FACADE_STATUS_NOT_AUTHORIZED = 2,
    FACADE_STATUS_PROVENANCE_MISSING = 3,
    FACADE_STATUS_LINK_UNVERIFIED = 4,
    FACADE_STATUS_OUTPUT_TOO_SMALL = 5
} FaCADE_Status;

typedef struct {
    const char *notice_id;
    const char *source_record_id;
    const char *target_record_id;
    const char *evidence_reference;
    const char *reason;
    const char *recorded_at;
    const char *reviewer_id;
    FaCADE_Relation relation;
    int source_authorized;
    int link_verified;
} FaCADE_Correction;

/* Builds an additive correction/portal proposal. It never edits source records,
 * impersonates a person, publishes, or treats a missing record as recovered fact.
 * Authorization and link_verified are upstream assertions, not cryptographic proof. */
FaCADE_Status facade_build_correction(const FaCADE_Correction *correction,
                                      char *output,
                                      size_t output_capacity);

#ifdef __cplusplus
}
#endif

#endif
