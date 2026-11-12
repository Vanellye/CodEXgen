#ifndef ERIA_WALLA_REGURGITATION_H
#define ERIA_WALLA_REGURGITATION_H

/* Walla 《¡》 regurgitation: pinned proposal + owner/system TRU Meet Point.
 * Reconciles references only. It does not reconnect wallets, restore secrets,
 * move funds, alter provider state, or accept a proposal automatically.
 * Consent, security, safety, ownership, and approval are mandatory.
 */
#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    WALLA_TRU_HOLD = 0,
    WALLA_TRU_READY_FOR_REVIEW = 1,
    WALLA_TRU_INVALID = 2
} WallaTruStatus;

typedef enum {
    WALLA_EVIDENCE_UNSPECIFIED = 0,
    WALLA_EVIDENCE_VERIFIED_REFERENCE = 1,
    WALLA_EVIDENCE_UNVERIFIED_CLAIM = 2,
    WALLA_EVIDENCE_INTERPRETATION = 3
} WallaEvidenceClass;

typedef struct {
    const char *proposal_id;
    const char *wallet_reference;
    const char *owner_reference;
    const char *origin_record_reference;
    const char *provenance_reference;
    const char *owner_record_reference;
    const char *system_record_reference;
    const char *authorized_scope;
    const char *requested_scope;
    const char *review_reference;
    WallaEvidenceClass evidence_class;
    int owner_confirms_match;
    int system_record_available;
    int consent_verified;
    int security_verified;
    int safety_verified;
    int ownership_verified;
    int approval_verified;
    int transaction_history_preserved;
} WallaTruRequest;

typedef struct {
    WallaTruStatus status;
    const char *pinned_proposal_id;
    const char *meet_point;
    const char *decision;
    const char *reason;
} WallaTruResult;

WallaTruResult walla_tru_meet(const WallaTruRequest *request);

#ifdef __cplusplus
}
#endif
#endif
