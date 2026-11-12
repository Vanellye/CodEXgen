#ifndef ERIA_RHYTHMATIC_REMEDY_H
#define ERIA_RHYTHMATIC_REMEDY_H

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    RR_OBSERVE = 0,
    RR_ACCOUNT,
    RR_REFLECT,
    RR_REFINE,
    RR_RESTORE,
    RR_RECONCILE
} RrStage;

typedef enum {
    RR_OK = 0,
    RR_INVALID,
    RR_NOT_AUTHORIZED,
    RR_PROVENANCE_MISSING,
    RR_OUTPUT_TOO_SMALL,
    RR_BAD_TRANSITION
} RrStatus;

/*
 * A caller-supplied, owner-authorized description of a recurring pattern.
 * References and authorization are assertions from the caller; this module
 * does not authenticate identities, inspect private streams, or move value.
 */
typedef struct {
    const char *cycle_id;
    const char *owner_reference;
    const char *pattern_reference;
    const char *evidence_reference;
    const char *observed_at;
    const char *current_pattern;
    const char *desired_pattern;
    const char *owner_selected_remedy;
    const char *uncertainty;
    unsigned confidence_percent; /* 0..100; descriptive, not a truth score */
    int owner_authorized;
    int scope_authorized;
} RrCycle;

RrStatus rr_advance(
    const RrCycle *cycle,
    RrStage current_stage,
    RrStage requested_stage,
    char *output,
    unsigned output_capacity
);

const char *rr_stage_name(RrStage stage);

#ifdef __cplusplus
}
#endif

#endif
