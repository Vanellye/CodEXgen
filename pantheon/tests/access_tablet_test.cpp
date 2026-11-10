#include "pantheon/runtime.hpp"
#include <cassert>
#include <memory>
#include <string>
#include <vector>

class AccessModule : public pantheon::Module {
public:
    std::string name() const { return "access-module"; }
    std::vector<pantheon::AccessRequirement> accessRequirements() const {
        std::vector<pantheon::AccessRequirement> requirements;
        requirements.push_back(pantheon::AccessRequirement("secretum:alias/profile", pantheon::AccessOperation::Read));
        requirements.push_back(pantheon::AccessRequirement("datorum:record/42", pantheon::AccessOperation::Write));
        return requirements;
    }
    pantheon::Result execute(const pantheon::Input&) const {
        pantheon::Result result;
        result.ok = true;
        result.module = name();
        result.message = "resource_action_executed";
        return result;
    }
};


class ControlledAccessModule : public AccessModule {
public:
    std::string name() const { return "controlled-access-module"; }
    bool requiresControlAuthorization() const { return true; }
};

class TestOwnerApproval : public pantheon::OwnerApproval {
public:
    explicit TestOwnerApproval(bool approved) : approved_(approved) {}
    bool approvedByAuthorizedOwner() const { return approved_; }
private:
    bool approved_;
};

static std::vector<pantheon::StandardEvidence> allStandards() {
    std::vector<pantheon::StandardEvidence> standards;
    for (unsigned int i = 1; i <= 38; ++i) {
        standards.push_back(pantheon::StandardEvidence(i, true, "evidence-" + std::to_string(i)));
    }
    return standards;
}

static pantheon::AccessContext context() {
    pantheon::AccessContext value;
    value.subject = "user:local-owner";
    value.invitationId = "invite:job-42";
    value.sourceRevision = "sha256:source-revision-42";
    value.nowUnixSeconds = 1000;
    return value;
}

static pantheon::AccessGrant grant(
        const std::string& resource, pantheon::AccessOperation operation) {
    pantheon::AccessGrant value;
    value.subject = "user:local-owner";
    value.resource = resource;
    value.operation = operation;
    value.invitationId = "invite:job-42";
    value.sourceRevision = "sha256:source-revision-42";
    value.expiresAtUnixSeconds = 2000;
    value.approved = true;
    return value;
}

int main() {
    pantheon::Runtime runtime;
    std::shared_ptr<pantheon::Module> module(new AccessModule());
    assert(runtime.registerModule(module));

    // A declared resource module cannot use the legacy unscoped path.
    pantheon::Result legacy = runtime.execute("access-module", pantheon::Input());
    assert(!legacy.ok);
    assert(legacy.message == "access_tablet_required");

    std::vector<pantheon::AccessGrant> grants;
    grants.push_back(grant("secretum:alias/profile", pantheon::AccessOperation::Read));
    // Read permission alone does not imply write permission.
    pantheon::Result readOnly = runtime.executeWithAccess(
        "access-module", pantheon::Input(), context(), grants);
    assert(!readOnly.ok);
    assert(readOnly.message.find("write_denied:") == 0);

    grants.push_back(grant("datorum:record/42", pantheon::AccessOperation::Write));
    pantheon::Result allowed = runtime.executeWithAccess(
        "access-module", pantheon::Input(), context(), grants);
    assert(allowed.ok);
    assert(allowed.message == "resource_action_executed");

    pantheon::AccessContext wrongSource = context();
    wrongSource.sourceRevision = "sha256:different-source";
    pantheon::Result mismatch = runtime.executeWithAccess(
        "access-module", pantheon::Input(), wrongSource, grants);
    assert(!mismatch.ok);

    std::vector<pantheon::AccessGrant> expired = grants;
    expired[0].expiresAtUnixSeconds = 1000;
    pantheon::Result expiredDenied = runtime.executeWithAccess(
        "access-module", pantheon::Input(), context(), expired);
    assert(!expiredDenied.ok);

    std::vector<pantheon::AccessGrant> unapproved = grants;
    unapproved[1].approved = false;
    pantheon::Result unapprovedDenied = runtime.executeWithAccess(
        "access-module", pantheon::Input(), context(), unapproved);
    assert(!unapprovedDenied.ok);

    std::vector<pantheon::AccessGrant> wrongOperation = grants;
    wrongOperation[1].operation = pantheon::AccessOperation::Read;
    pantheon::Result operationDenied = runtime.executeWithAccess(
        "access-module", pantheon::Input(), context(), wrongOperation);
    assert(!operationDenied.ok);

    // A controlled resource module must pass both independent gates.
    std::shared_ptr<pantheon::Module> controlled(new ControlledAccessModule());
    assert(runtime.registerModule(controlled));
    pantheon::Result bypassAttempt = runtime.executeControlled(
        "controlled-access-module", pantheon::Input(), allStandards(),
        TestOwnerApproval(true));
    assert(!bypassAttempt.ok);
    assert(bypassAttempt.message == "access_tablet_required");

    pantheon::Result accessButNoOwner = runtime.executeControlledWithAccess(
        "controlled-access-module", pantheon::Input(), context(), grants,
        allStandards(), TestOwnerApproval(false));
    assert(!accessButNoOwner.ok);
    assert(accessButNoOwner.message ==
           "control_gate_denied:authorized_owner_approval_required");

    pantheon::Result bothGates = runtime.executeControlledWithAccess(
        "controlled-access-module", pantheon::Input(), context(), grants,
        allStandards(), TestOwnerApproval(true));
    assert(bothGates.ok);
    assert(bothGates.message == "resource_action_executed");
    return 0;
}
