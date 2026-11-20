#include "../STAR.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void) {
    const star_glyph_token *token;
    assert(star_glyph_token_count() == 6U);
    token = star_glyph_token_at(0U);
    assert(token != NULL && strcmp(token->token_id, "EG_D010") == 0);
    assert(token->codepoint == 0x13080U && strcmp(token->utf8_glyph, "𓂀") == 0);
    token = star_glyph_token_at(1U);
    assert(token != NULL && token->codepoint == 0x131F3U);
    token = star_glyph_token_at(2U);
    assert(token != NULL && token->codepoint == 0x133E4U);
    token = star_glyph_token_at(3U);
    assert(token != NULL && strcmp(token->token_id, "CU_AN") == 0);
    assert(token->codepoint == 0x1202DU && strcmp(token->utf8_glyph, "𒀭") == 0);
    token = star_glyph_token_at(4U);
    assert(token != NULL && token->codepoint == 0x12097U);
    token = star_glyph_token_at(5U);
    assert(token != NULL && token->codepoint == 0x121A0U);
    assert(star_glyph_token_at(6U) == NULL);
    puts("PASS: STAR glyph registry contract tests");
    return 0;
}
