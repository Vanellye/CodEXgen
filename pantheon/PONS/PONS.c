#include "PONS.h"

#include <stdio.h>
#include <string.h>

static int present(const char *s) { return s != NULL && s[0] != '\0'; }

static int copy_text(char *out, size_t cap, const char *in) {
    int n;
    if (!present(in) || out == NULL || cap == 0U) return 0;
    n = snprintf(out, cap, "%s", in);
    return n >= 0 && (size_t)n < cap;
}

static int is_hex_sha256(const char *s) {
    size_t i;
    if (s == NULL || strlen(s) != 64U) return 0;
    for (i = 0; i < 64U; ++i) {
        const char c = s[i];
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return 0;
    }
    return 1;
}

PonsCState pons_c_verify(const PonsCManifestPin *pin,
                         const unsigned char *source_bytes,
                         size_t source_length,
                         PonsCSha256Fn sha256_fn,
                         void *sha256_context,
                         PonsCProof *proof) {
    char actual[65] = {0};
    if (proof == NULL) return PONS_C_INVALID;
    memset(proof, 0, sizeof(*proof));
    proof->state = PONS_C_UNKNOWN;

    if (pin == NULL || !present(pin->component_id) ||
        !present(pin->source_ref) || !present(pin->source_path) ||
        !is_hex_sha256(pin->expected_sha256) ||
        !present(pin->anchor_id) || !present(pin->anchor_ref)) {
        (void)snprintf(proof->reason, sizeof(proof->reason), "manifest pin incomplete");
        return proof->state;
    }
    if (strcmp(pin->anchor_id, PONS_CANONICAL_ANCHOR_ID) != 0 ||
        strcmp(pin->anchor_ref, PONS_CANONICAL_ANCHOR_REF) != 0) {
        proof->state = PONS_C_HOLD;
        (void)snprintf(proof->reason, sizeof(proof->reason), "canonical anchor mismatch");
        return proof->state;
    }
    if (source_bytes == NULL || source_length == 0U || sha256_fn == NULL) {
        (void)snprintf(proof->reason, sizeof(proof->reason), "source or SHA-256 provider unavailable");
        return proof->state;
    }
    if (!copy_text(proof->component_id, sizeof(proof->component_id), pin->component_id) ||
        !copy_text(proof->expected_sha256, sizeof(proof->expected_sha256), pin->expected_sha256)) {
        proof->state = PONS_C_INVALID;
        return proof->state;
    }
    if (!sha256_fn(source_bytes, source_length, actual, sha256_context) ||
        !is_hex_sha256(actual)) {
        (void)snprintf(proof->reason, sizeof(proof->reason), "SHA-256 provider failed");
        return proof->state;
    }
    (void)copy_text(proof->actual_sha256, sizeof(proof->actual_sha256), actual);
    if (strcmp(actual, pin->expected_sha256) != 0) {
        proof->state = PONS_C_HOLD;
        (void)snprintf(proof->reason, sizeof(proof->reason), "source digest mismatch");
        return proof->state;
    }
    proof->state = PONS_C_VERIFIED;
    (void)snprintf(proof->reason, sizeof(proof->reason), "source digest matched reviewed pin");
    return proof->state;
}

int pons_c_proof_is_valid(const PonsCProof *proof, const char *component_id) {
    return proof != NULL && component_id != NULL &&
           proof->state == PONS_C_VERIFIED &&
           strcmp(proof->component_id, component_id) == 0 &&
           is_hex_sha256(proof->expected_sha256) &&
           is_hex_sha256(proof->actual_sha256) &&
           strcmp(proof->expected_sha256, proof->actual_sha256) == 0;
}
