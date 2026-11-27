#include "RHYTHMATIC_REMEDY.h"

#include <stdio.h>
#include <string.h>

const char *rr_stage_name(RrStage stage) {
    switch (stage) {
        case RR_OBSERVE: return "Observe";
        case RR_ACCOUNT: return "Account";
        case RR_REFLECT: return "Reflect";
        case RR_REFINE: return "Refine";
        case RR_RESTORE: return "Restore";
        case RR_RECONCILE: return "Reconcile";
        default: return "Unknown";
    }
}

static int present(const char *value) {
    return value != NULL && value[0] != '\0';
}

RrStatus rr_advance(
    const RrCycle *cycle,
    RrStage current_stage,
    RrStage requested_stage,
    char *output,
    unsigned output_capacity
) {
    int written;

    if (cycle == NULL || output == NULL || output_capacity == 0U ||
        current_stage < RR_OBSERVE || current_stage > RR_RECONCILE ||
        requested_stage < RR_OBSERVE || requested_stage > RR_RECONCILE) {
        return RR_INVALID;
    }

    if (!present(cycle->cycle_id) || !present(cycle->owner_reference) ||
        !present(cycle->pattern_reference) || !present(cycle->observed_at) ||
        !present(cycle->current_pattern) ||
        !present(cycle->desired_pattern) ||
        !present(cycle->owner_selected_remedy) ||
        !present(cycle->uncertainty) ||
        cycle->confidence_percent > 100U) {
        return RR_INVALID;
    }

    if (!present(cycle->evidence_reference)) {
        return RR_PROVENANCE_MISSING;
    }

    if (!cycle->owner_authorized || !cycle->scope_authorized) {
        return RR_NOT_AUTHORIZED;
    }

    /* One forward step only; a completed cycle returns to Observe. */
    if (!((current_stage < RR_RECONCILE &&
           requested_stage == (RrStage)(current_stage + 1)) ||
          (current_stage == RR_RECONCILE &&
           requested_stage == RR_OBSERVE))) {
        return RR_BAD_TRANSITION;
    }

    written = snprintf(
        output,
        (size_t)output_capacity,
        "TeSt RHYTHMATIC REMEDY\n"
        "Cycle: %s\nOwner reference: %s\nPattern reference: %s\n"
        "Evidence/provenance reference: %s\nObserved: %s\n"
        "Transition: %s -> %s\n"
        "Current pattern: %s\nDesired pattern: %s\n"
        "Owner-selected remedy: %s\n"
        "Confidence descriptor: %u/100 (not a truth or worth score)\n"
        "Uncertainty: %s\n"
        "Safeguard: proposal only; owner retains control; no transfer, "
        "coercion, diagnosis, or automatic action.\n",
        cycle->cycle_id,
        cycle->owner_reference,
        cycle->pattern_reference,
        cycle->evidence_reference,
        cycle->observed_at,
        rr_stage_name(current_stage),
        rr_stage_name(requested_stage),
        cycle->current_pattern,
        cycle->desired_pattern,
        cycle->owner_selected_remedy,
        cycle->confidence_percent,
        cycle->uncertainty
    );

    if (written < 0 || (unsigned)written >= output_capacity) {
        output[0] = '\0';
        return RR_OUTPUT_TOO_SMALL;
    }

    return RR_OK;
}
