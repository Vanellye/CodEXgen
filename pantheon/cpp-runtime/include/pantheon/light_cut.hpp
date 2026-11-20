#ifndef PANTHEON_LIGHT_CUT_HPP
#define PANTHEON_LIGHT_CUT_HPP
#include <string>
#include <vector>
namespace pantheon { namespace light_cut {
struct FlowPacket {
    std::string sourceId;
    double amount;
    FlowPacket() : amount(0.0) {}
};
struct Route {
    std::string destination;
    double weight;
    Route() : weight(0.0) {}
    Route(const std::string& target, double share) : destination(target), weight(share) {}
};
struct FlowSegment {
    std::string sourceId;
    std::string destination;
    double amount;
};
struct RoutingResult {
    bool valid;
    double inputAmount;
    double routedAmount;
    std::vector<FlowSegment> segments;
    std::vector<std::string> findings;
    RoutingResult() : valid(false), inputAmount(0.0), routedAmount(0.0) {}
};
class LightCutRouter {
public:
    // Declarative, side-effect-free partition. Weights must sum to 1.
    RoutingResult route(const FlowPacket& packet, const std::vector<Route>& routes) const;
};
} }
#endif
