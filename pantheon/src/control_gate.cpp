#include "pantheon/control_gate.hpp"

#include <set>

namespace pantheon {

ControlGateDecision ControlGate::evaluate(
        const std::vector<StandardEvidence>& standards,
        const OwnerApproval& ownerApproval) const {
    ControlGateDecision decision;
    if (standards.size() != REQUIRED_STANDARDS) {
        decision.reason = "exactly_38_standards_required";
        return decision;
    }

    std::set<unsigned int> seen;
    for (std::vector<StandardEvidence>::const_iterator it = standards.begin();
         it != standards.end(); ++it) {
        if (it->number < 1 || it->number > REQUIRED_STANDARDS) {
            decision.reason = "standard_number_out_of_range";
            return decision;
        }
        if (!seen.insert(it->number).second) {
            decision.reason = "duplicate_standard_number";
            return decision;
        }
        if (!it->passed) {
            decision.reason = "standard_not_passed";
            return decision;
        }
        if (it->evidenceReference.empty()) {
            decision.reason = "standard_evidence_missing";
            return decision;
        }
        ++decision.passedCount;
    }

    if (seen.size() != REQUIRED_STANDARDS) {
        decision.reason = "one_or_more_standards_missing";
        return decision;
    }
    if (!ownerApproval.approvedByAuthorizedOwner()) {
        decision.reason = "authorized_owner_approval_required";
        return decision;
    }

    decision.granted = true;
    decision.reason = "all_38_standards_passed_and_owner_approved";
    return decision;
}

} // namespace pantheon
