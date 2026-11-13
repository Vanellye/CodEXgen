#ifndef ERIA_Z_TO_A_H
#define ERIA_Z_TO_A_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>

typedef enum {
    Z2A_DATA_UNSPECIFIED = 0,
    Z2A_DATA_PUBLIC,
    Z2A_DATA_CONSENTED_AGGREGATE
} Z2ADataClass;

typedef enum {
    Z2A_EVIDENCE_UNKNOWN = 0,
    Z2A_EVIDENCE_SOURCE_REPORTED,
    Z2A_EVIDENCE_CORROBORATED,
    Z2A_EVIDENCE_HYPOTHESIS,
    Z2A_EVIDENCE_INTERPRETATION
} Z2AEvidenceClass;

typedef enum {
    Z2A_OK = 0,
    Z2A_INVALID,
    Z2A_NOT_AUTHORIZED,
    Z2A_UNSUPPORTED_DATA,
    Z2A_PROVENANCE_MISSING,
    Z2A_EVIDENCE_MISSING,
    Z2A_OUTPUT_TOO_SMALL
} Z2AStatus;

/* Caller supplies minimized data and references; this struct does not
 * cryptographically establish permission, provenance, or evidence. */
typedef struct {
    const char *source_id;
    const char *record_id;
    const char *original_forum_ref;
    const char *provenance_ref;
    const char *evidence_ref;
    const char *claim_or_output;
    const char *purpose;
    const char *authorized_scope;
    const char *requested_scope;
    const char *known_uncertainty;
    Z2ADataClass data_class;
    Z2AEvidenceClass evidence_class;
    int authorization_confirmed;
} Z2AEnvelope;

/* Produces a reverse-trace audit note; never writes or changes source data. */
Z2AStatus z2a_audit(const Z2AEnvelope *envelope,
                    char *output,
                    size_t output_capacity);

#ifdef __cplusplus
}
#endif

#endif
