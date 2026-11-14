#include "pantheon/code_translation.hpp"
#include <cassert>
#include <stdexcept>

int main() {
    pantheon::CodeSource source;
    source.path = "src/example.cpp";
    source.language = "cpp";
    source.revision = "test-revision";
    source.sourceDigest = "sha256:test-fixture";
    source.bytes = "#include <string>\nclass Engine {\npublic:\n  void run() {\n    return;\n  }\n};\n";

    const pantheon::CodeTranslationResult result =
        pantheon::CodeTranslationEngine::translate(source);
    assert(result.accepted);
    assert(result.sourcePreserved);
    assert(result.sourceDigest == source.sourceDigest);
    assert(result.sourcePath == source.path);
    assert(result.findings.size() >= 3);
    assert(result.findings[0].line == 1);
    assert(!result.reviewFlags.empty());

    pantheon::CodeSource invalid = source;
    invalid.sourceDigest.clear();
    bool rejected = false;
    try { pantheon::CodeTranslationEngine::translate(invalid); }
    catch (const std::invalid_argument&) { rejected = true; }
    assert(rejected);
    return 0;
}
