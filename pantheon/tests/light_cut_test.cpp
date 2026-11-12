#include "pantheon/light_cut.hpp"
#include <cassert>
#include <cmath>
#include <limits>
int main() {
    using namespace pantheon::light_cut;
    LightCutRouter router;
    FlowPacket packet;
    packet.sourceId = "origin-stream-01";
    packet.amount = 100.0;
    std::vector<Route> routes;
    routes.push_back(Route("forward", 0.6));
    routes.push_back(Route("upward", 0.4));
    RoutingResult result = router.route(packet, routes);
    assert(result.valid);
    assert(result.segments.size() == 2);
    assert(result.segments[0].sourceId == packet.sourceId);
    assert(result.segments[0].destination == "forward");
    assert(result.segments[1].destination == "upward");
    assert(std::fabs(result.segments[0].amount - 60.0) < 1e-9);
    assert(std::fabs(result.segments[1].amount - 40.0) < 1e-9);
    assert(std::fabs(result.routedAmount - packet.amount) < 1e-9);
    std::vector<Route> incomplete;
    incomplete.push_back(Route("forward", 0.6));
    assert(!router.route(packet, incomplete).valid);
    std::vector<Route> duplicate;
    duplicate.push_back(Route("same", 0.5));
    duplicate.push_back(Route("same", 0.5));
    assert(!router.route(packet, duplicate).valid);
    std::vector<Route> negative;
    negative.push_back(Route("forward", 1.2));
    negative.push_back(Route("upward", -0.2));
    assert(!router.route(packet, negative).valid);
    FlowPacket invalid = packet;
    invalid.amount = std::numeric_limits<double>::infinity();
    assert(!router.route(invalid, routes).valid);
    invalid = packet;
    invalid.sourceId.clear();
    assert(!router.route(invalid, routes).valid);
    return 0;
}
