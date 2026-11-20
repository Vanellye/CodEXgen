#include "PONS.h"
#include <assert.h>
#include <string.h>

/* Test-only deterministic stub. This is NOT cryptography. */
static int test_digest(const unsigned char *bytes, size_t length,
                       char output[65], void *context) {
    size_t i;
    const char *expected = (const char *)context;
    if (bytes == NULL || length == 0U || expected == NULL) return 0;
    for (i = 0; i < 64U; ++i) output[i] = expected[i];
    output[64] = '\0';
    return 1;
}

int main(void) {
    static const unsigned char source[] = "fixture";
    static const char digest[] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    PonsCManifestPin pin = {
        "pantheon.new", "reviewed-ref", "pantheon/NEW/NEW.c", digest,
        PONS_CANONICAL_ANCHOR_ID, PONS_CANONICAL_ANCHOR_REF
    };
    PonsCProof *proof = NULL;

    assert(pons_c_verify(&pin, source, sizeof(source) - 1U,
                         test_digest, (void *)digest, &proof) == PONS_C_VERIFIED);
    assert(pons_c_proof_is_valid(proof, "pantheon.new"));
    pons_c_proof_destroy(proof);
    proof = NULL;

    assert(pons_c_verify(&pin, (const unsigned char *)"altered", 7U,
                         test_digest, (void *)"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                         &proof) == PONS_C_HOLD);
    assert(!pons_c_proof_is_valid(proof, "pantheon.new"));
    pons_c_proof_destroy(proof);
    proof = NULL;

    pin.anchor_id = "altered-anchor";
    assert(pons_c_verify(&pin, source, sizeof(source) - 1U,
                         test_digest, (void *)digest, &proof) == PONS_C_HOLD);
    pons_c_proof_destroy(proof);
    proof = NULL;

    pin.anchor_id = PONS_CANONICAL_ANCHOR_ID;
    assert(pons_c_verify(&pin, NULL, 0U, test_digest, (void *)digest, &proof) == PONS_C_UNKNOWN);
    assert(!pons_c_proof_is_valid(proof, "pantheon.new"));
    pons_c_proof_destroy(proof);
    return 0;
}
