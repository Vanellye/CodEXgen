#ifndef PANTHEON_CODE_TRANSLATION_HPP
#define PANTHEON_CODE_TRANSLATION_HPP

#include <cstddef>
#include <string>
#include <vector>

namespace pantheon {

// A read-only translation request. The caller supplies the digest of the exact
// source bytes; this engine never opens, rewrites, or executes repository files.
struct CodeSource {
    std::string path;
    std::string language;
    std::string revision;
    std::string sourceDigest;
    std::string bytes;
};

struct TranslationFinding {
    std::size_t line;
    std::string sourceText;
    std::string explanation;
    std::string construct;
    std::string evidenceClass;
    double confidence;
};

struct CodeTranslationResult {
    bool accepted;
    bool sourcePreserved;
    std::string sourcePath;
    std::string sourceRevision;
    std::string sourceDigest;
    std::string translationVersion;
    std::vector<TranslationFinding> findings;
    std::vector<std::string> reviewFlags;
    std::string boundary;
};

class CodeTranslationEngine {
public:
    // Deterministic, lexical first-pass only. Results are candidate explanations,
    // not proof of runtime behavior or a complete semantic translation.
    static CodeTranslationResult translate(const CodeSource& source);
};

} // namespace pantheon

#endif
