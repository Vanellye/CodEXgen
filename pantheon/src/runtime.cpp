#include "pantheon/runtime.hpp"

namespace pantheon {

Runtime::Runtime() : modules_() {}

bool Runtime::registerModule(const std::shared_ptr<Module>& module) {
    if (!module) return false;
    const std::string key = module->name();
    if (key.empty() || modules_.find(key) != modules_.end()) return false;
    modules_[key] = module;
    return true;
}

bool Runtime::hasModule(const std::string& name) const {
    return modules_.find(name) != modules_.end();
}

Result Runtime::execute(const std::string& name, const Input& input) const {
    std::map<std::string, std::shared_ptr<Module> >::const_iterator it =
        modules_.find(name);
    if (it == modules_.end()) {
        Result missing;
        missing.module = name;
        missing.message = "module_not_registered";
        return missing;
    }
    if (it->second->requiresControlAuthorization()) {
        Result denied;
        denied.module = name;
        denied.message = "control_authorization_required";
        return denied;
    }
    return it->second->execute(input);
}

Result Runtime::executeControlled(
        const std::string& name, const Input& input,
        const std::vector<StandardEvidence>& standards,
        const OwnerApproval& ownerApproval) const {
    std::map<std::string, std::shared_ptr<Module> >::const_iterator it =
        modules_.find(name);
    if (it == modules_.end()) {
        Result missing;
        missing.module = name;
        missing.message = "module_not_registered";
        return missing;
    }
    if (!it->second->requiresControlAuthorization()) {
        Result denied;
        denied.module = name;
        denied.message = "module_does_not_require_control_authorization";
        return denied;
    }

    ControlGate gate;
    const ControlGateDecision decision = gate.evaluate(standards, ownerApproval);
    if (!decision.granted) {
        Result denied;
        denied.module = name;
        denied.message = "control_gate_denied:" + decision.reason;
        denied.metrics["standards_passed"] = decision.passedCount;
        denied.metrics["standards_required"] = ControlGate::REQUIRED_STANDARDS;
        return denied;
    }
    return it->second->execute(input);
}

std::vector<std::string> Runtime::moduleNames() const {
    std::vector<std::string> names;
    for (std::map<std::string, std::shared_ptr<Module> >::const_iterator it =
             modules_.begin(); it != modules_.end(); ++it) {
        names.push_back(it->first);
    }
    return names;
}

const char* Runtime::version() {
    return "Pantheon Native Runtime 0.1.0";
}

} // namespace pantheon
