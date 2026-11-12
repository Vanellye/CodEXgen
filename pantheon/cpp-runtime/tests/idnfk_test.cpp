#include "pantheon/idnfk.hpp"
#include <cassert>

int main() {
    using namespace pantheon::idnfk;
    IDnfkSequence sequence;
    Subject subject;
    subject.id = "subject-1";
    subject.source = "source-origin";
    subject.description = "A proposed SACREL evolution step";
    subject.category = "geometry";
    subject.recognizedCategories.push_back("geometry");
    subject.requestedAction = "prepare a reviewable geometry proposal";
    subject.evidence = EvidenceState::VERIFIED;

    RunPlan plan = sequence.build(subject);
    assert(plan.identifier == "IDnfk");
    assert(plan.subjectClass == SubjectClass::RECOGNIZED);
    assert(plan.stage == RunStage::REVIEW_REQUIRED);
    assert(!plan.readyForAuthorizationCheck);

    subject.approvalReference = "review-record-001";
    plan = sequence.build(subject);
    assert(plan.stage == RunStage::READY_FOR_EXTERNAL_AUTHORIZATION_CHECK);
    assert(plan.readyForAuthorizationCheck);

    subject.category = "unmapped-subject";
    plan = sequence.build(subject);
    assert(plan.subjectClass == SubjectClass::OTHER);
    assert(plan.stage == RunStage::INSPECTION_REQUIRED);
    assert(!plan.readyForAuthorizationCheck);
    assert(plan.sequence.size() == 4);
    assert(plan.sequence[2] == "OTHER");
    assert(plan.sequence[3] == "INSPECT");

    subject.category = "geometry";
    subject.evidence = EvidenceState::INFERRED;
    plan = sequence.build(subject);
    assert(plan.stage == RunStage::INSPECTION_REQUIRED);
    assert(!plan.readyForAuthorizationCheck);

    subject.evidence = EvidenceState::VERIFIED;
    subject.source.clear();
    plan = sequence.build(subject);
    assert(plan.stage == RunStage::INVALID);
    assert(!plan.readyForAuthorizationCheck);
    return 0;
}
