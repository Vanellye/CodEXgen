#pragma once
#include <algorithm>
#include <functional>
#include <set>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace codexgen::olpirt {
struct ModuleContract {
    std::string name;
    std::vector<std::string> requires;
};
struct LightReport {
    std::size_t modules = 0;
    std::size_t dependencyEdges = 0;
    std::size_t resolvedEdges = 0;
    std::vector<std::string> missingProviders;
    std::vector<std::string> dependencyCycles;
    double lightIndex = 100.0;
    bool ready() const noexcept {
        return missingProviders.empty() && dependencyCycles.empty();
    }
};

/** Olpirt makes declared software dependency paths visible and auditable. */
class OlpirtLightBridge final {
public:
    LightReport illuminate(const std::vector<ModuleContract>& modules,
                           const std::set<std::string>& externalProviders = {}) const {
        LightReport report;
        report.modules = modules.size();
        std::unordered_map<std::string, std::vector<std::string>> graph;
        std::unordered_set<std::string> names;
        for (const auto& module : modules) {
            names.insert(module.name);
            graph[module.name] = module.requires;
            report.dependencyEdges += module.requires.size();
        }
        for (const auto& module : modules) {
            for (const auto& dependency : module.requires) {
                if (names.count(dependency) || externalProviders.count(dependency)) {
                    ++report.resolvedEdges;
                } else {
                    report.missingProviders.push_back(module.name + " -> " + dependency);
                }
            }
        }

        enum class Mark { Visiting, Complete };
        std::unordered_map<std::string, Mark> marks;
        std::vector<std::string> path;
        std::set<std::string> cycles;
        std::function<void(const std::string&)> visit = [&](const std::string& node) {
            auto mark = marks.find(node);
            if (mark != marks.end() && mark->second == Mark::Complete) return;
            if (mark != marks.end() && mark->second == Mark::Visiting) {
                auto start = std::find(path.begin(), path.end(), node);
                std::string cycle;
                for (auto it = start; it != path.end(); ++it) {
                    if (!cycle.empty()) cycle += " -> ";
                    cycle += *it;
                }
                cycles.insert(cycle + " -> " + node);
                return;
            }
            marks[node] = Mark::Visiting;
            path.push_back(node);
            for (const auto& dependency : graph[node]) {
                if (names.count(dependency)) visit(dependency);
            }
            path.pop_back();
            marks[node] = Mark::Complete;
        };
        for (const auto& module : modules) visit(module.name);
        report.dependencyCycles.assign(cycles.begin(), cycles.end());
        if (report.dependencyEdges != 0) {
            report.lightIndex = 100.0 * static_cast<double>(report.resolvedEdges) /
                                static_cast<double>(report.dependencyEdges);
        }
        return report;
    }
};
} // namespace codexgen::olpirt
