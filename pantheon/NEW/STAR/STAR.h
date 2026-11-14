#ifndef ERIA_STAR_H
#define ERIA_STAR_H
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
    const char *token_id;
    const char *script;
    const char *unicode_name;
    unsigned int codepoint;
    const char *utf8_glyph;
} star_glyph_token;
/* Immutable registry; returns NULL for an out-of-range index. */
size_t star_glyph_token_count(void);
const star_glyph_token *star_glyph_token_at(size_t index);
#ifdef __cplusplus
}
#endif
#endif
