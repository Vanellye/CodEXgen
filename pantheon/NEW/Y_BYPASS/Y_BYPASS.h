#ifndef ERIA_Y_BYPASS_H
#define ERIA_Y_BYPASS_H

/*
 * ERIA Y-bypass contract — portable, header-only C99.
 *
 * Y is an explicit continuation state for a declared OPTIONAL field only.
 * It never converts or overwrites the original value. Zero, NULL, and empty
 * remain distinct inputs. This helper cannot authenticate the caller or
 * verify consent; the caller must supply verified gate results.
 *
 * Never use Y to bypass consent, security, safety, ownership, or approval.
 */
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    Y_INPUT_ZERO = 1,
    Y_INPUT_NULL = 2,
    Y_INPUT_EMPTY = 3
} YInputKind;

typedef enum {
    Y_STATUS_DENIED = 0,
    Y_STATUS_BYPASS_Y = 1,
    Y_STATUS_INVALID = 2
} YStatus;

typedef struct {
    YInputKind input_kind;
    const char *field_name;
    const char *scope;
    const char *allowed_scope;
    const char *reason;
    const char *authorization_ref;
    int field_is_optional;
    int consent_verified;
    int security_verified;
    int safety_verified;
    int ownership_verified;
    int approval_verified;
} YBypassRequest;

typedef struct {
    YStatus status;
    const char *token; /* "Y" only when every condition is satisfied. */
    const char *explanation;
} YBypassResult;

static int y_bypass_text_present(const char *value)
{
    return value != NULL && value[0] != '\0';
}

static int y_bypass_scope_matches(const char *scope, const char *allowed_scope)
{
    const char *a;
    const char *b;
    if (!y_bypass_text_present(scope) || !y_bypass_text_present(allowed_scope)) {
        return 0;
    }
    a = scope;
    b = allowed_scope;
    while (*a != '\0' && *b != '\0' && *a == *b) {
        ++a;
        ++b;
    }
    return *a == '\0' && *b == '\0';
}

static YBypassResult y_bypass_resolve(const YBypassRequest *request)
{
    YBypassResult result;
    result.status = Y_STATUS_DENIED;
    result.token = "HOLD";
    result.explanation = "Y bypass denied; preserve the original value.";

    if (request == NULL ||
        (request->input_kind != Y_INPUT_ZERO &&
         request->input_kind != Y_INPUT_NULL &&
         request->input_kind != Y_INPUT_EMPTY) ||
        !y_bypass_text_present(request->field_name) ||
        !y_bypass_text_present(request->reason) ||
        !y_bypass_text_present(request->authorization_ref)) {
        result.status = Y_STATUS_INVALID;
        result.explanation = "Invalid request or missing audit reference.";
        return result;
    }

    if (!request->field_is_optional ||
        !y_bypass_scope_matches(request->scope, request->allowed_scope) ||
        !request->consent_verified ||
        !request->security_verified ||
        !request->safety_verified ||
        !request->ownership_verified ||
        !request->approval_verified) {
        result.explanation =
            "Protected gate, optionality, or scope check failed; no bypass.";
        return result;
    }

    result.status = Y_STATUS_BYPASS_Y;
    result.token = "Y";
    result.explanation =
        "Explicit optional-field continuation; original zero/NULL/empty is unchanged.";
    return result;
}

#ifdef __cplusplus
}
#endif

#endif /* ERIA_Y_BYPASS_H */
