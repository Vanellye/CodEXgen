#include "pantheon/gateway.hpp"
#include <cassert>
#include <cmath>
#include <stdexcept>
#include <string>
#include <vector>

int main() {
    assert(std::string(pantheon::gatewayOriginCommit()) ==
           "747fdea5388113f6a8ebad720b9c6283dc7dce70");

    pantheon::GatewayCandidate local;
    local.id = "local-native";
    local.compatibility = 1.0;
    local.readiness = 0.9;
    local.reliability = 0.95;
    local.authorized = true;
    local.safe = true;

    pantheon::GatewayCandidate remote;
    remote.id = "remote-adapter";
    remote.compatibility = 0.8;
    remote.readiness = 0.8;
    remote.reliability = 0.7;
    remote.authorized = true;
    remote.safe = true;

    pantheon::GatewayCandidate blocked;
    blocked.id = "unapproved-device";
    blocked.compatibility = 1.0;
    blocked.readiness = 1.0;
    blocked.reliability = 1.0;
    blocked.authorized = false;
    blocked.safe = true;

    std::vector<pantheon::GatewayCandidate> candidates;
    candidates.push_back(local);
    candidates.push_back(remote);
    candidates.push_back(blocked);

    pantheon::GatewayDecision decision =
        pantheon::GatewayRouter::evaluate(candidates, 0.5);
    assert(decision.gatewayReached);
    assert(decision.selectedGateway == "local-native");
    assert(decision.routes.size() == 2);
    assert(decision.confidence > 0.5);
    const double localWeight = 0.30 * 1.0 + 0.30 * 0.9 + 0.40 * 0.95;
    const double remoteWeight = 0.30 * 0.8 + 0.30 * 0.8 + 0.40 * 0.7;
    assert(std::fabs(decision.routes[0].probability -
                     localWeight / (localWeight + remoteWeight)) < 1e-12);
    assert(std::fabs(decision.routes[0].probability +
                     decision.routes[1].probability - 1.0) < 1e-12);

    pantheon::GatewayDecision gated =
        pantheon::GatewayRouter::evaluate(candidates, 1.0);
    assert(!gated.gatewayReached);
    assert(gated.selectedGateway.empty());

    blocked.authorized = true;
    blocked.safe = false;
    candidates.clear();
    candidates.push_back(blocked);
    pantheon::GatewayDecision none = pantheon::GatewayRouter::evaluate(candidates);
    assert(!none.gatewayReached);
    assert(none.routes.empty());

    bool rejected = false;
    try { pantheon::GatewayRouter::evaluate(candidates, 1.1); }
    catch (const std::invalid_argument&) { rejected = true; }
    assert(rejected);
    return 0;
}
