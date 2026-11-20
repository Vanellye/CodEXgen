#include "pantheon/ectict.hpp"
#include <cassert>
int main() {
    using namespace pantheon::ectict;
    EctictThinking review;
    Viewpoint one = {"v1", "source-A", "Preserve the existing design.", EvidenceState::VERIFIED};
    Viewpoint two = {"v2", "source-B", "Replace the existing design.", EvidenceState::INFERRED};
    assert(review.addViewpoint(one));
    assert(review.addViewpoint(two));
    Tension tension = {"t1", "v1", "v2", "What evidence distinguishes these approaches?"};
    assert(review.addTension(tension));
    GrowthProposal proposal;
    proposal.id = "g1";
    proposal.tensionId = "t1";
    proposal.learning = "Compare both approaches against the same acceptance criteria.";
    proposal.nextStep = "Run a bounded, reviewable experiment.";
    assert(review.addProposal(proposal));
    assert(review.validate().valid);
    assert(review.viewpoints().size() == 2);
    assert(review.viewpoints()[0].statement != review.viewpoints()[1].statement);
    assert(review.proposals().size() == 1);
    Tension collapsed = {"t2", "v1", "v1", "Force both views into one."};
    assert(!review.addTension(collapsed));
    GrowthProposal unreviewed = proposal;
    unreviewed.id = "g2";
    unreviewed.requiresHumanReview = false;
    assert(!review.addProposal(unreviewed));
    Viewpoint duplicate = one;
    duplicate.statement = "Overwrite the original.";
    assert(!review.addViewpoint(duplicate));
    return 0;
}
