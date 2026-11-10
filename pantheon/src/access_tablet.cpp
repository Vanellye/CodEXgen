#include "pantheon/access_tablet.hpp"

namespace pantheon {

const char* accessOperationName(AccessOperation operation) {
    return operation == AccessOperation::Read ? "read" : "write";
}

AccessDecision AccessTablet::evaluate(
        const AccessRequirement& requirement,
        const AccessContext& context,
        const std::vector<AccessGrant>& grants) const {
    AccessDecision decision;
    if (requirement.resource.empty()) {
        decision.reason = "resource_required";
        return decision;
    }
    if (context.subject.empty()) {
        decision.reason = "subject_required";
        return decision;
    }
    if (context.invitationId.empty()) {
        decision.reason = "invitation_source_required";
        return decision;
    }
    if (context.sourceRevision.empty()) {
        decision.reason = "invitation_revision_required";
        return decision;
    }
    if (context.nowUnixSeconds <= 0) {
        decision.reason = "trusted_current_time_required";
        return decision;
    }

    for (std::vector<AccessGrant>::const_iterator it = grants.begin();
         it != grants.end(); ++it) {
        if (!it->approved) continue;
        if (it->subject != context.subject) continue;
        if (it->resource != requirement.resource) continue;
        if (it->operation != requirement.operation) continue;
        if (it->invitationId != context.invitationId) continue;
        if (it->sourceRevision != context.sourceRevision) continue;
        if (it->expiresAtUnixSeconds <= context.nowUnixSeconds) continue;

        decision.granted = true;
        decision.reason = "exact_invitation_bound_grant";
        return decision;
    }

    decision.reason = "no_matching_read_or_write_grant";
    return decision;
}

AccessDecision AccessTablet::evaluateAll(
        const std::vector<AccessRequirement>& requirements,
        const AccessContext& context,
        const std::vector<AccessGrant>& grants) const {
    AccessDecision decision;
    if (requirements.empty()) {
        decision.granted = true;
        decision.reason = "no_additional_access_requirements";
        return decision;
    }
    for (std::vector<AccessRequirement>::const_iterator it = requirements.begin();
         it != requirements.end(); ++it) {
        const AccessDecision item = evaluate(*it, context, grants);
        if (!item.granted) {
            decision.reason = std::string(accessOperationName(it->operation)) +
                              "_denied:" + item.reason + ":" + it->resource;
            return decision;
        }
    }
    decision.granted = true;
    decision.reason = "all_exact_access_requirements_granted";
    return decision;
}

} // namespace pantheon
