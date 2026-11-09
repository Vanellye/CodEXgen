#pragma once
#include "olpirt/light_bridge.hpp"
#include <sstream>
#include <string>

namespace codexgen {
namespace olpirt {
class FreedomBridge {
public:
    std::string exportSummary(const LightReport& report) const {
        std::ostringstream out;
        out << "Olpirt / Pons dependency report\n"
            << "modules=" << report.modules << "\n"
            << "dependency_edges=" << report.dependencyEdges << "\n"
            << "resolved_edges=" << report.resolvedEdges << "\n"
            << "light_index=" << report.lightIndex << "%\n"
            << "ready=" << (report.ready() ? "true" : "false") << "\n";
        for (std::vector<std::string>::const_iterator it = report.missingProviders.begin(); it != report.missingProviders.end(); ++it) out << "missing=" << *it << "\n";
        for (std::vector<std::string>::const_iterator it = report.dependencyCycles.begin(); it != report.dependencyCycles.end(); ++it) out << "cycle=" << *it << "\n";
        return out.str();
    }
};
} // namespace olpirt
} // namespace codexgen
