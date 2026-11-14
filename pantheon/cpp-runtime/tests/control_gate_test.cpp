#include "pantheon/runtime.hpp"
#include <cassert>
#include <memory>
#include <string>
#include <vector>

class ControlledModule : public pantheon::Module {
public:
    std::string name() const { return "controlled"; }
    bool requiresControlAuthorization() const { return true; }
    pantheon::Result execute(const pantheon::Input&) const {
        pantheon::Result result;
        result.ok = true;
        result.module = name();
        result.message = "controlled_action_executed";
        return result;
    }
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
        standards.push_back(pantheon::StandardEvidence(i, true, "audit-evidence-" + std::to_string(i)));
    }
    return standards;
}

int main() {
    pantheon::Runtime runtime;
    std::shared_ptr<pantheon::Module> controlled(new ControlledModule());
    assert(runtime.registerModule(controlled));

    pantheon::Result ordinary = runtime.execute("controlled", pantheon::Input());
    assert(!ordinary.ok);
    assert(ordinary.message == "control_authorization_required");

    std::vector<pantheon::StandardEvidence> standards = allStandards();
    TestOwnerApproval approved(true);
    TestOwnerApproval notApproved(false);

    pantheon::Result noOwner = runtime.executeControlled(
        "controlled", pantheon::Input(), standards, notApproved);
    assert(!noOwner.ok);
    assert(noOwner.message == "control_gate_denied:authorized_owner_approval_required");

    standards[37].passed = false;
    pantheon::Result lastStandardFailed = runtime.executeControlled(
        "controlled", pantheon::Input(), standards, approved);
    assert(!lastStandardFailed.ok);
    assert(lastStandardFailed.message == "control_gate_denied:standard_not_passed");

    standards = allStandards();
    standards.pop_back();
    pantheon::Result incomplete = runtime.executeControlled(
        "controlled", pantheon::Input(), standards, approved);
    assert(!incomplete.ok);
    assert(incomplete.message == "control_gate_denied:exactly_38_standards_required");

    standards = allStandards();
    pantheon::Result granted = runtime.executeControlled(
        "controlled", pantheon::Input(), standards, approved);
    assert(granted.ok);
    assert(granted.message == "controlled_action_executed");
    return 0;
}
