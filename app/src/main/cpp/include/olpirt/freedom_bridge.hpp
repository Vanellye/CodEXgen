#pragma once
#include "olpirt/light_bridge.hpp"
#include <sstream>
#include <string>

namespace codexgen::olpirt {
/** Portable, plain-text dependency audit; provider implementations remain replaceable. */
class FreedomBridge final {
public:
    std::string exportSummary(const LightReport& report) const {
        std::ostringstream out;
        out << "Olpirt / Pons dependency report\n"
            << "modules=" << report.modules << "\n"
            << "dependency_edges=" << report.dependencyEdges << "\n"
            << "resolved_edges=" << report.resolvedEdges << "\n"
            << "light_index=" << report.lightIndex << "%\n"
            << "ready=" << (report.ready() ? "true" : "false") << "\n";
        for (const auto& item : report.missingProviders) out << "missing=" << item << "\n";
        for (const auto& item : report.dependencyCycles) out << "cycle=" << item << "\n";
        return out.str();
    }
};
} // namespace codexgen::olpirt
