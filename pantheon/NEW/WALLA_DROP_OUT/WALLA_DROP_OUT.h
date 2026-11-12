#ifndef ERIA_WALLA_DROP_OUT_H
#define ERIA_WALLA_DROP_OUT_H

/* ERIA Walla 《¡》 wallet disconnect contract.
 * Proposal-only: does not call a provider, move funds, delete records,
 * revoke credentials, or modify an external wallet.
 * All five protection gates are mandatory and cannot be bypassed.
 */
#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    WALLA_HOLD = 0,
    WALLA_DISCONNECT_PROPOSED = 1,
    WALLA_INVALID = 2
} WallaStatus;

typedef struct {
    const char *wallet_reference;
    const char *owner_reference;
    const char *provider_reference;
    const char *scope;
    const char *authorized_scope;
    const char *approval_reference;
    int consent_verified;
    int security_verified;
    int safety_verified;
    int ownership_verified;
    int approval_verified;
    int preserve_transaction_history;
    int preserve_audit_provenance;
} WallaRequest;

typedef struct {
    WallaStatus status;
    const char *replacement_label;
    const char *decision;
    const char *reason;
} WallaResult;

WallaResult walla_prepare_disconnect(const WallaRequest *request);

#ifdef __cplusplus
}
#endif
#endif
