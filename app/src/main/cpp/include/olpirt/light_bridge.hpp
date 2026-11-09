#pragma once
#include <algorithm>
#include <functional>
#include <set>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace codexgen {
namespace olpirt {
struct ModuleContract {
    std::string name;
    std::vector<std::string> requires;
};
struct LightReport {
    std::size_t modules;
    std::size_t dependencyEdges;
    std::size_t resolvedEdges;
    std::vector<std::string> missingProviders;
    std::vector<std::string> dependencyCycles;
    double lightIndex;
    LightReport() : modules(0), dependencyEdges(0), resolvedEdges(0), lightIndex(100.0) {}
    bool ready() const {
        return missingProviders.empty() && dependencyCycles.empty();
    }
};

class OlpirtLightBridge {
public:
    LightReport illuminate(const std::vector<ModuleContract>& modules,
                           const std::set<std::string>& externalProviders = std::set<std::string>()) const {
        LightReport report;
        report.modules = modules.size();
        std::unordered_map<std::string, std::vector<std::string> > graph;
        std::unordered_set<std::string> names;
        for (std::vector<ModuleContract>::const_iterator it = modules.begin(); it != modules.end(); ++it) {
            names.insert(it->name);
            graph[it->name] = it->requires;
            report.dependencyEdges += it->requires.size();
        }
        for (std::vector<ModuleContract>::const_iterator it = modules.begin(); it != modules.end(); ++it) {
            for (std::vector<std::string>::const_iterator dep = it->requires.begin(); dep != it->requires.end(); ++dep) {
                if (names.count(*dep) || externalProviders.count(*dep)) {
                    ++report.resolvedEdges;
                } else {
                    report.missingProviders.push_back(it->name + " -> " + *dep);
                }
            }
        }

        enum Mark { VISITING, COMPLETE };
        std::unordered_map<std::string, Mark> marks;
        std::vector<std::string> path;
        std::set<std::string> cycles;
        std::function<void(const std::string&)> visit = [&](const std::string& node) {
            std::unordered_map<std::string, Mark>::iterator mark = marks.find(node);
            if (mark != marks.end() && mark->second == COMPLETE) return;
            if (mark != marks.end() && mark->second == VISITING) {
                std::vector<std::string>::iterator start = std::find(path.begin(), path.end(), node);
                std::string cycle;
                for (std::vector<std::string>::iterator p = start; p != path.end(); ++p) {
                    if (!cycle.empty()) cycle += " -> ";
                    cycle += *p;
                }
                cycles.insert(cycle + " -> " + node);
                return;
            }
            marks[node] = VISITING;
            path.push_back(node);
            const std::vector<std::string>& deps = graph[node];
            for (std::vector<std::string>::const_iterator dep = deps.begin(); dep != deps.end(); ++dep) {
                if (names.count(*dep)) visit(*dep);
            }
            path.pop_back();
            marks[node] = COMPLETE;
        };
        for (std::vector<ModuleContract>::const_iterator it = modules.begin(); it != modules.end(); ++it) visit(it->name);
        report.dependencyCycles.assign(cycles.begin(), cycles.end());
        if (report.dependencyEdges != 0) {
            report.lightIndex = 100.0 * static_cast<double>(report.resolvedEdges) /
                                static_cast<double>(report.dependencyEdges);
        }
        return report;
    }
};
} // namespace olpirt
} // namespace codexgen
