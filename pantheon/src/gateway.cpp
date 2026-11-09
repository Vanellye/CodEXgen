#include "pantheon/gateway.hpp"
#include <cmath>
#include <stdexcept>

namespace pantheon {

const char* gatewayOriginCommit() {
    return "747fdea5388113f6a8ebad720b9c6283dc7dce70";
}

GatewayDecision GatewayRouter::evaluate(
        const std::vector<GatewayCandidate>& candidates,
        double minimumConfidence) {
    if (!std::isfinite(minimumConfidence) ||
        minimumConfidence < 0.0 || minimumConfidence > 1.0) {
        throw std::invalid_argument("minimum_confidence must be within [0, 1]");
    }
    if (candidates.size() > 128) {
        throw std::invalid_argument("at most 128 gateway candidates are supported");
    }

    GatewayDecision decision;
    decision.originCommit = gatewayOriginCommit();

    double total = 0.0;
    std::vector<double> weights;
    weights.reserve(candidates.size());

    for (std::size_t i = 0; i < candidates.size(); ++i) {
        const GatewayCandidate& candidate = candidates[i];
        if (candidate.id.empty()) {
            throw std::invalid_argument("gateway candidate id must not be empty");
        }
        for (std::size_t j = 0; j < i; ++j) {
            if (candidates[j].id == candidate.id) {
                throw std::invalid_argument("gateway candidate ids must be unique");
            }
        }
        const double values[] = {
            candidate.compatibility, candidate.readiness, candidate.reliability
        };
        for (int k = 0; k < 3; ++k) {
            if (!std::isfinite(values[k]) || values[k] < 0.0 || values[k] > 1.0) {
                throw std::invalid_argument("gateway scores must be within [0, 1]");
            }
        }

        // Authorization and safety are hard gates, not weighted preferences.
        if (!candidate.authorized || !candidate.safe) continue;

        // Reliability receives the highest individual weighting.
        const double weight = 0.30 * candidate.compatibility +
                              0.30 * candidate.readiness +
                              0.40 * candidate.reliability;
        weights.push_back(weight);
        total += weight;
        GatewayRoute route;
        route.id = candidate.id;
        decision.routes.push_back(route);
    }

    if (decision.routes.empty() || total <= 0.0) {
        decision.reason = "no_authorized_safe_gateway_with_positive_score";
        return decision;
    }

    std::size_t best = 0;
    for (std::size_t i = 0; i < decision.routes.size(); ++i) {
        decision.routes[i].probability = weights[i] / total;
        if (decision.routes[i].probability > decision.confidence) {
            decision.confidence = decision.routes[i].probability;
            best = i;
        }
    }

    if (decision.confidence >= minimumConfidence) {
        decision.selectedGateway = decision.routes[best].id;
        decision.gatewayReached = true;
        decision.reason = "highest_scoring_eligible_gateway_selected";
    } else {
        decision.reason = "confidence_below_required_threshold";
    }
    return decision;
}

} // namespace pantheon
