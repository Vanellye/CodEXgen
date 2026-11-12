#ifndef PANTHEON_IDNFK_HPP
#define PANTHEON_IDNFK_HPP

#include <string>
#include <vector>

namespace pantheon {
namespace idnfk {

// IDnfk is an exact system identifier. No acronym expansion is implied.
static const char* const IDENTIFIER = "IDnfk";

enum class EvidenceState { VERIFIED, INFERRED, UNKNOWN };
enum class SubjectClass { RECOGNIZED, OTHER };
enum class RunStage {
    DISCOVERED,
    CLASSIFIED,
    INSPECTION_REQUIRED,
    REVIEW_REQUIRED,
    READY_FOR_EXTERNAL_AUTHORIZATION_CHECK,
    INVALID
};

struct Subject {
    std::string id;
    std::string source;
    std::string description;
    std::string category;
    std::vector<std::string> recognizedCategories;
    std::string requestedAction;
    EvidenceState evidence;
    std::string approvalReference;

    Subject() : evidence(EvidenceState::UNKNOWN) {}
};

struct RunPlan {
    std::string identifier;
    SubjectClass subjectClass;
    RunStage stage;
    bool readyForAuthorizationCheck;
    std::vector<std::string> sequence;
    std::vector<std::string> findings;

    RunPlan()
        : identifier(IDENTIFIER),
          subjectClass(SubjectClass::OTHER),
          stage(RunStage::DISCOVERED),
          readyForAuthorizationCheck(false) {}
};

// Builds a deterministic, side-effect-free plan. It never executes the
// requested action or treats a supplied approval reference as authentication.
class IDnfkSequence {
public:
    RunPlan build(const Subject& subject) const;
};

} // namespace idnfk
} // namespace pantheon

#endif
