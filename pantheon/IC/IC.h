#ifndef PANTHEON_IC_H
#define PANTHEON_IC_H

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Pantheon IC — Integration Core.
 *
 * This module models reviewable pipeline gates. It does not start processes,
 * invoke CI providers, synthesize hardware, write artifacts, or dispatch
 * external actions.
 */

typedef enum {
    IC_STAGE_PENDING = 0,
    IC_STAGE_RUNNING = 1,
    IC_STAGE_PASSED = 2,
    IC_STAGE_FAILED = 3,
    IC_STAGE_BLOCKED = 4
} ICStageState;

typedef enum {
    IC_APPROVAL_UNSET = 0,
    IC_APPROVAL_DENIED = 1,
    IC_APPROVAL_GRANTED = 2
} ICApproval;

typedef struct {
    ICStageState state;
    ICApproval approval;
    int requires_approval;
} ICGate;

/*
 * Aðð qualification: all seven independent checks must be present.
 * These are caller-supplied evidence flags, not cryptographic attestations.
 */
typedef struct {
    int intent;
    int consent;
    int evidence;
    int forward;
    int reverse;
    int review;
    int bridge_integrity;
} ICAeddChecks;

/* Read-only, fail-closed qualification of the seven Aðð checks. */
int ic_aedd_qualifies(const ICAeddChecks *checks);

/* True only when a pending gate has satisfied its dependencies and approval. */
int ic_can_start(const ICGate *gate, int dependencies_passed);

/* Transition pending -> running, or pending -> blocked when prerequisites fail. */
int ic_start(ICGate *gate, int dependencies_passed);

/* Transition running -> passed/failed. Returns 1 only for a valid transition. */
int ic_finish(ICGate *gate, int checks_passed);

/* Publication is a separate decision; this function never publishes anything. */
int ic_can_publish(const ICGate *gate, int all_quality_checks_passed);

#ifdef __cplusplus
}
#endif

#endif
