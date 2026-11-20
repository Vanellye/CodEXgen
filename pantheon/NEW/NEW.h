#ifndef ERIA_PANTHEON_NEW_H
#define ERIA_PANTHEON_NEW_H

#include <stddef.h>
#include "../PONS/PONS.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NEW_DATA_UNSPECIFIED = 0,
    NEW_DATA_PUBLIC = 1,
    NEW_DATA_CONSENTED_AGGREGATE = 2
} NewDataClass;

typedef enum {
    NEW_EVIDENCE_UNSPECIFIED = 0,
    NEW_EVIDENCE_SOURCE_REPORTED = 1,
    NEW_EVIDENCE_INDEPENDENTLY_CORROBORATED = 2,
    NEW_EVIDENCE_HYPOTHESIS = 3
} NewEvidenceStatus;

typedef enum {
    NEW_STATUS_OK = 0,
    NEW_STATUS_INVALID = 1,
    NEW_STATUS_NOT_AUTHORIZED = 2,
    NEW_STATUS_UNSUPPORTED_DATA = 3,
    NEW_STATUS_PROVENANCE_MISSING = 4,
    NEW_STATUS_OUTPUT_TOO_SMALL = 5,
    NEW_STATUS_PROOF_REFERENCE_MISSING = 6,
    NEW_STATUS_PONS_HOLD = 7
} NewStatus;

/* Caller supplies already-minimized data from an authorized source.
 * This module does not connect to or collect from external data streams.
 * authorization_confirmed is an upstream assertion, not cryptographic proof. */
typedef struct {
    const char *source_id;
    const char *record_id;
    const char *permission_basis;
    const char *purpose;
    const char *captured_at;
    const char *provenance_digest;
    const char *content_summary;
    const char *proof_reference;
    const char *proof_method;
    const char *proof_checked_at;
    NewDataClass data_class;
    NewEvidenceStatus evidence_status;
    int authorization_confirmed;
    const PonsCProof *pons_proof;
} NewRecord;

/* Builds a classified evidence summary for human review, never a verdict.
 * Provenance (origin/history) and proof references (claim support) stay distinct. */
NewStatus new_build_narrative(const NewRecord *record,
                              char *output,
                              size_t output_capacity);

#ifdef __cplusplus
}
#endif

#endif
