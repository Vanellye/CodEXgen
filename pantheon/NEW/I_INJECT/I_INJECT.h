#ifndef ERIA_I_INJECT_H
#define ERIA_I_INJECT_H

/*
 * ERIA I-INJECT: protected, proposal-only injection contract (C99).
 *
 * This module validates whether a proposed value may be considered for a
 * declared integration point. It does not write, execute, publish, transfer,
 * or mutate data. The caller must independently verify all authorization
 * assertions and preserve the source record.
 *
 * No gate is bypassable: consent, security, safety, ownership, approval.
 */
#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    I_INJECT_HOLD = 0,
    I_INJECT_PROPOSED = 1,
    I_INJECT_INVALID = 2
} IInjectStatus;

typedef struct {
    const char *intent;
    const char *source_reference;
    const char *provenance_reference;
    const char *target;
    const char *requested_scope;
    const char *authorized_scope;
    const char *compatibility_reference;
    const char *approval_reference;
    int consent_verified;
    int security_verified;
    int safety_verified;
    int ownership_verified;
    int approval_verified;
    int compatibility_verified;
} IInjectRequest;

typedef struct {
    IInjectStatus status;
    const char *decision;
    const char *reason;
} IInjectResult;

/* Returns PROPOSED only when every required reference and gate is present. */
IInjectResult i_inject_validate(const IInjectRequest *request);

#ifdef __cplusplus
}
#endif
#endif
