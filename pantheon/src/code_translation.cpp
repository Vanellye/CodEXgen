#include "pantheon/code_translation.hpp"

#include <sstream>
#include <stdexcept>

namespace pantheon {
namespace {

bool startsWith(const std::string& value, const std::string& prefix) {
    return value.compare(0, prefix.size(), prefix) == 0;
}

std::string trim(const std::string& value) {
    const std::string::size_type first = value.find_first_not_of(" \t\r");
    if (first == std::string::npos) return std::string();
    const std::string::size_type last = value.find_last_not_of(" \t\r");
    return value.substr(first, last - first + 1);
}

void add(std::vector<TranslationFinding>& out, std::size_t line,
         const std::string& source, const std::string& construct,
         const std::string& explanation) {
    TranslationFinding finding;
    finding.line = line;
    finding.sourceText = source;
    finding.construct = construct;
    finding.explanation = explanation;
    // Syntax recognition is observed; the English meaning is an interpretation.
    finding.evidenceClass = "INTERPRETATION";
    finding.confidence = 0.55;
    out.push_back(finding);
}

void inspectLine(const std::string& line, std::size_t number,
                 std::vector<TranslationFinding>& out) {
    const std::string s = trim(line);
    if (s.empty() || startsWith(s, "//") || startsWith(s, "# ") ||
        startsWith(s, "/*") || startsWith(s, "*")) return;

    if (startsWith(s, "#include") || startsWith(s, "import ") ||
        startsWith(s, "from ")) {
        add(out, number, line, "dependency declaration",
            "This line names a header or module that the source file depends on.");
    } else if (startsWith(s, "class ") || s.find(" class ") != std::string::npos) {
        add(out, number, line, "class declaration",
            "This line appears to declare a class, a named type that can group data and behavior.");
    } else if (startsWith(s, "struct ") || s.find(" struct ") != std::string::npos) {
        add(out, number, line, "struct declaration",
            "This line appears to declare a structure, a named aggregate data type.");
    } else if (startsWith(s, "interface ") || s.find(" interface ") != std::string::npos) {
        add(out, number, line, "interface declaration",
            "This line appears to declare an interface contract for implementing types.");
    } else if (startsWith(s, "def ") || startsWith(s, "fun ") ||
               s.find(") {") != std::string::npos) {
        add(out, number, line, "function or method declaration",
            "This line may begin a callable function or method; inspect its signature and body to establish its behavior.");
    } else if (startsWith(s, "return ") || s == "return;" || s == "return") {
        add(out, number, line, "return statement",
            "This line returns a value or ends the current function without a value.");
    } else if (startsWith(s, "if ") || startsWith(s, "if(") ||
               startsWith(s, "if (") || startsWith(s, "else if")) {
        add(out, number, line, "conditional",
            "This line begins or continues a conditional path; the condition determines when that path runs.");
    } else if (startsWith(s, "for ") || startsWith(s, "for(") ||
               startsWith(s, "for (") || startsWith(s, "while ") ||
               startsWith(s, "while(") || startsWith(s, "while (")) {
        add(out, number, line, "loop",
            "This line appears to begin a loop; its condition and body determine repetition.");
    } else if (s.find("SELECT ") != std::string::npos ||
               s.find("select ") != std::string::npos ||
               s.find("INSERT ") != std::string::npos ||
               s.find("UPDATE ") != std::string::npos ||
               s.find("DELETE ") != std::string::npos) {
        add(out, number, line, "SQL statement",
            "This line contains a recognizable SQL operation; its target and effects require query-context review.");
    }
}

} // namespace

CodeTranslationResult CodeTranslationEngine::translate(const CodeSource& source) {
    if (source.path.empty() || source.language.empty() ||
        source.revision.empty() || source.sourceDigest.empty())
        throw std::invalid_argument("path, language, revision, and sourceDigest are required");
    if (source.bytes.empty())
        throw std::invalid_argument("source bytes must not be empty");
    if (source.bytes.size() > 1024 * 1024)
        throw std::invalid_argument("source exceeds the 1 MiB first-pass limit");

    CodeTranslationResult result;
    result.accepted = true;
    result.sourcePreserved = true;
    result.sourcePath = source.path;
    result.sourceRevision = source.revision;
    result.sourceDigest = source.sourceDigest;
    result.translationVersion = "higher-faculty-lexical-0.1";
    result.boundary = "Candidate English explanations only; no compilation, execution, file writes, Git changes, or authorization.";
    result.reviewFlags.push_back("Lexical matching can miss constructs or misclassify syntax.");
    result.reviewFlags.push_back("Function behavior, control-flow effects, and runtime claims require full-context verification.");

    std::istringstream input(source.bytes);
    std::string line;
    std::size_t number = 0;
    while (std::getline(input, line)) {
        ++number;
        inspectLine(line, number, result.findings);
    }
    if (result.findings.empty())
        result.reviewFlags.push_back("No supported constructs were recognized; no semantic translation was inferred.");
    return result;
}

} // namespace pantheon
