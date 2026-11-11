#include "pantheon/aleph.hpp"
#include "pantheon/runtime.hpp"
#include <cassert>
#include <string>
#include <vector>

class Approval : public pantheon::AlephApproval {
public:
    explicit Approval(bool allowed) : allowed_(allowed) {}
    bool approvedByAuthorizedOwner() const { return allowed_; }
private:
    bool allowed_;
};

class FailingModule : public pantheon::Module {
public:
    std::string name() const { return "failure"; }
    pantheon::Result execute(const pantheon::Input&) const {
        pantheon::Result result;
        result.module = name();
        result.message = "simulated_failure";
        return result;
    }
};

class SuccessModule : public pantheon::Module {
public:
    std::string name() const { return "success"; }
    pantheon::Result execute(const pantheon::Input&) const {
        pantheon::Result result;
        result.ok = true;
        result.module = name();
        result.message = "ok";
        return result;
    }
};

int main() {
    pantheon::Runtime runtime;
    assert(runtime.registerModule(
        std::shared_ptr<pantheon::Module>(new FailingModule())));
    assert(runtime.registerModule(
        std::shared_ptr<pantheon::Module>(new SuccessModule())));

    std::vector<int> order;
    assert(runtime.aleph().recordRecoveryAction("first",
        [&order]() { order.push_back(1); return true; }));
    assert(runtime.aleph().recordRecoveryAction("second",
        [&order]() { order.push_back(2); return true; }));

    pantheon::Result failed = runtime.execute("failure", pantheon::Input());
    assert(!failed.ok);
    assert(runtime.aleph().state() == pantheon::AlephState::SAFE_HOLD);
    assert(runtime.aleph().reason() == "simulated_failure");

    pantheon::Result held = runtime.execute("success", pantheon::Input());
    assert(!held.ok);
    assert(held.message == "aleph_safe_hold");

    Approval denied(false);
    pantheon::AlephRecoveryReport blocked = runtime.aleph().reverse(denied);
    assert(!blocked.completed);
    assert(blocked.reason == "authorized_owner_approval_required");

    Approval allowed(true);
    pantheon::AlephRecoveryReport recovered = runtime.aleph().reverse(allowed);
    assert(recovered.completed);
    assert(recovered.attempted == 2);
    assert(recovered.succeeded == 2);
    assert(order.size() == 2);
    assert(order[0] == 2 && order[1] == 1);
    assert(runtime.aleph().state() == pantheon::AlephState::RECOVERED);

    pantheon::Result heldAfterRecovery =
        runtime.execute("success", pantheon::Input());
    assert(!heldAfterRecovery.ok);
    assert(heldAfterRecovery.message == "aleph_safe_hold");
    return 0;
}
