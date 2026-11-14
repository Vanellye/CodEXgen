#ifndef ERIA_PONS_H
#define ERIA_PONS_H

#include <stddef.h>

#define PONS_CANONICAL_ANCHOR_ID "7f7a43a973a96a06dd432bf94843213d09133323"
#define PONS_CANONICAL_ANCHOR_REF "df5ead3b55cfabd0ba40e902b4080946cba794dc"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    PONS_C_VERIFIED = 0,
    PONS_C_HOLD = 1,
    PONS_C_UNKNOWN = 2,
    PONS_C_INVALID = 3
} PonsCState;

/* Production builds must inject a vetted SHA-256 implementation. */
typedef int (*PonsCSha256Fn)(const unsigned char *bytes, size_t length,
                             char output_hex[65], void *context);

typedef struct {
    const char *component_id;
    const char *source_ref;
    const char *source_path;
    const char *expected_sha256;
    const char *anchor_id;
    const char *anchor_ref;
} PonsCManifestPin;

typedef struct PonsCProof PonsCProof;

/* Pin must come from an independently reviewed manifest.
 * Hash callback must be a real SHA-256 implementation in production.
 * Missing pin/source/hash provider => UNKNOWN; mismatch => HOLD. */
PonsCState pons_c_verify(const PonsCManifestPin *pin,
                         const unsigned char *source_bytes,
                         size_t source_length,
                         PonsCSha256Fn sha256_fn,
                         void *sha256_context,
                         PonsCProof **proof_out);

int pons_c_proof_is_valid(const PonsCProof *proof, const char *component_id);
void pons_c_proof_destroy(PonsCProof *proof);

#ifdef __cplusplus
}
#endif
#endif
