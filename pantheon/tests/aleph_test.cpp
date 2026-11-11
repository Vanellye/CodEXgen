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

int main() {
    pantheon::Runtime runtime;
    assert(runtime.registerModule(
        std::shared_ptr<pantheon::Module>(new FailingModule())));

    std::vector<int> order;
    assert(runtime.aleph().recordRecoveryAction("first",
        [&order]() { order.push_back(1); return true; }));
    assert(runtime.aleph().recordRecoveryAction("second",
        [&order]() { order.push_back(2); return true; }));

    pantheon::Result failed = runtime.execute("failure", pantheon::Input());
    assert(!failed.ok);
    assert(runtime.aleph().state() == pantheon::AlephState::SAFE_HOLD);
    assert(runtime.aleph().reason() == "simulated_failure");

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
    return 0;
}
