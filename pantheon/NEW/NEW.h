#ifndef ERIA_PANTHEON_NEW_H
#define ERIA_PANTHEON_NEW_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NEW_DATA_UNSPECIFIED = 0,
    NEW_DATA_PUBLIC = 1,
    NEW_DATA_CONSENTED_AGGREGATE = 2
} NewDataClass;

typedef enum {
    NEW_STATUS_OK = 0,
    NEW_STATUS_INVALID = 1,
    NEW_STATUS_NOT_AUTHORIZED = 2,
    NEW_STATUS_UNSUPPORTED_DATA = 3,
    NEW_STATUS_PROVENANCE_MISSING = 4,
    NEW_STATUS_OUTPUT_TOO_SMALL = 5
} NewStatus;

/* Caller supplies already-minimized data from an authorized source.
 * This module does not connect to or collect from external data streams. */
typedef struct {
    const char *source_id;
    const char *record_id;
    const char *permission_basis;
    const char *purpose;
    const char *captured_at;
    const char *provenance_digest;
    const char *content_summary;
    NewDataClass data_class;
    int authorization_confirmed;
} NewRecord;

/* Creates an unverified narrative proposal for human review only. */
NewStatus new_build_narrative(const NewRecord *record,
                              char *output,
                              size_t output_capacity);

#ifdef __cplusplus
}
#endif

#endif
