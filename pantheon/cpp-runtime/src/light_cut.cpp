#include "pantheon/light_cut.hpp"
#include <cmath>
#include <set>
namespace pantheon { namespace light_cut {
RoutingResult LightCutRouter::route(const FlowPacket& packet, const std::vector<Route>& routes) const {
    RoutingResult result;
    result.inputAmount = packet.amount;
    if (packet.sourceId.empty()) {
        result.findings.push_back("Flow source identity is required.");
        return result;
    }
    if (!std::isfinite(packet.amount) || packet.amount < 0.0) {
        result.findings.push_back("Flow amount must be finite and nonnegative.");
        return result;
    }
    if (routes.empty()) {
        result.findings.push_back("At least one destination route is required.");
        return result;
    }
    const double tolerance = 1e-9;
    double totalWeight = 0.0;
    std::set<std::string> destinations;
    for (std::vector<Route>::const_iterator it = routes.begin(); it != routes.end(); ++it) {
        if (it->destination.empty() || !std::isfinite(it->weight) || it->weight < 0.0 ||
            !destinations.insert(it->destination).second) {
            result.findings.push_back("Routes require unique destinations and finite nonnegative weights.");
            return result;
        }
        totalWeight += it->weight;
    }
    if (!std::isfinite(totalWeight) || std::fabs(totalWeight - 1.0) > tolerance) {
        result.findings.push_back("Route weights must sum to 1; no flow is dropped or implicitly amplified.");
        return result;
    }
    for (std::vector<Route>::const_iterator it = routes.begin(); it != routes.end(); ++it) {
        FlowSegment segment;
        segment.sourceId = packet.sourceId;
        segment.destination = it->destination;
        segment.amount = packet.amount * it->weight;
        result.segments.push_back(segment);
        result.routedAmount += segment.amount;
    }
    result.valid = true;
    result.findings.push_back("Flow partitioned across declared destinations; source identity retained.");
    result.findings.push_back("Routing is a plan only; downstream execution requires separate authorization.");
    return result;
}
} }
