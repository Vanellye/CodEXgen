#include "pantheon/idnfk.hpp"

namespace pantheon {
namespace idnfk {
namespace {
bool nonEmpty(const std::string& value) {
    return !value.empty();
}

bool contains(const std::vector<std::string>& values, const std::string& value) {
    for (std::vector<std::string>::const_iterator it = values.begin();
         it != values.end(); ++it) {
        if (*it == value) return true;
    }
    return false;
}
}

RunPlan IDnfkSequence::build(const Subject& subject) const {
    RunPlan plan;
    plan.sequence.push_back("DISCOVER");
    plan.stage = RunStage::DISCOVERED;

    if (!nonEmpty(subject.id) || !nonEmpty(subject.source) ||
        !nonEmpty(subject.description) || !nonEmpty(subject.requestedAction)) {
        plan.stage = RunStage::INVALID;
        plan.findings.push_back("Subject identity, source, description, and requested action are required.");
        return plan;
    }

    plan.sequence.push_back("CLASSIFY");
    const bool recognized = nonEmpty(subject.category) &&
        contains(subject.recognizedCategories, subject.category);
    plan.subjectClass = recognized ? SubjectClass::RECOGNIZED : SubjectClass::OTHER;
    plan.stage = RunStage::CLASSIFIED;

    if (!recognized) {
        plan.sequence.push_back("OTHER");
        plan.sequence.push_back("INSPECT");
        plan.stage = RunStage::INSPECTION_REQUIRED;
        plan.findings.push_back("Unrecognized or uncategorized subject routed to OTHER for inspection.");
        plan.findings.push_back("OTHER is a holding classification, not permission to execute or discard.");
        return plan;
    }

    if (subject.evidence != EvidenceState::VERIFIED) {
        plan.sequence.push_back("INSPECT");
        plan.stage = RunStage::INSPECTION_REQUIRED;
        plan.findings.push_back("Evidence must be VERIFIED before the request can advance.");
        return plan;
    }

    plan.sequence.push_back("REVIEW");
    plan.stage = RunStage::REVIEW_REQUIRED;
    if (!nonEmpty(subject.approvalReference)) {
        plan.findings.push_back("A traceable human approval reference is required before execution eligibility.");
        return plan;
    }

    plan.sequence.push_back("AUTHORIZE");
    plan.stage = RunStage::READY_FOR_AUTHORIZED_EXECUTION;
    plan.executionEligible = true;
    plan.findings.push_back("Approval reference recorded; an external authorization boundary must authenticate it.");
    plan.findings.push_back("This plan does not execute the requested action.");
    return plan;
}

} // namespace idnfk
} // namespace pantheon
