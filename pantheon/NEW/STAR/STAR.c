#include "STAR.h"
static const star_glyph_token STAR_GLYPHS[] = {
    {"EG_D010", "Egyptian hieroglyphs", "EGYPTIAN HIEROGLYPH D010", 0x13080U, "𓂀"},
    {"EG_N005", "Egyptian hieroglyphs", "EGYPTIAN HIEROGLYPH N005", 0x131F3U, "𓇳"},
    {"EG_Z001", "Egyptian hieroglyphs", "EGYPTIAN HIEROGLYPH Z001", 0x133E4U, "𓏤"},
    {"CU_AN", "Cuneiform", "CUNEIFORM SIGN AN", 0x1202DU, "𒀭"},
    {"CU_EN", "Cuneiform", "CUNEIFORM SIGN EN", 0x12097U, "𒂗"},
    {"CU_KI", "Cuneiform", "CUNEIFORM SIGN KI", 0x121A0U, "𒆠"}
};
size_t star_glyph_token_count(void) {
    return sizeof(STAR_GLYPHS) / sizeof(STAR_GLYPHS[0]);
}
const star_glyph_token *star_glyph_token_at(size_t index) {
    if (index >= star_glyph_token_count()) return NULL;
    return &STAR_GLYPHS[index];
}
