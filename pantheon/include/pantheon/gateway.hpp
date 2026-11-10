#ifndef PANTHEON_GATEWAY_HPP
#define PANTHEON_GATEWAY_HPP

#include <string>
#include <vector>

namespace pantheon {

// Immutable provenance anchor: the Faculty Engine integration commit.
const char* gatewayOriginCommit();

struct GatewayCandidate {
    std::string id;
    double compatibility;
    double readiness;
    double reliability;
    bool authorized;
    bool safe;

    GatewayCandidate()
        : id(), compatibility(0.0), readiness(0.0), reliability(0.0),
          authorized(false), safe(false) {}
};

struct GatewayRoute {
    std::string id;
    double probability;
};

struct GatewayDecision {
    std::string originCommit;
    std::string selectedGateway;
    double confidence;
    bool gatewayReached;
    std::vector<GatewayRoute> routes;
    std::string reason;

    GatewayDecision()
        : originCommit(), selectedGateway(), confidence(0.0),
          gatewayReached(false), routes(), reason() {}
};

class GatewayRouter {
public:
    // Scores are normalized across eligible routes. They are relative routing
    // weights, not calibrated probabilities of real-world success.
    static GatewayDecision evaluate(const std::vector<GatewayCandidate>& candidates,
                                    double minimumConfidence = 0.0);
};

} // namespace pantheon

#endif
