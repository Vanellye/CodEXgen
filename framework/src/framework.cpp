#include "codexgen/framework.hpp"
#include <utility>
namespace codexgen { namespace framework {
namespace {
bool valid_descriptor(const ModuleDescriptor& d) { return !d.id.empty() && !d.version.empty(); }
bool has_capabilities(const ModuleDescriptor& d, const std::set<Capability>& grants) {
    for (std::vector<Capability>::const_iterator it=d.required_capabilities.begin();
         it!=d.required_capabilities.end(); ++it) {
        if (grants.find(*it)==grants.end()) return false;
    }
    return true;
}
}
Status Registry::add(Module* module) {
    if (module==0) return Status::InvalidDescriptor;
    const ModuleDescriptor d=module->descriptor();
    if (!valid_descriptor(d)) return Status::InvalidDescriptor;
    if (modules_.find(d.id)!=modules_.end()) return Status::DuplicateModule;
    modules_.insert(std::make_pair(d.id,module));
    return Status::Ok;
}
ExecutionResult Registry::run(const std::string& id, const ExecutionRequest& request) const {
    std::map<std::string,Module*>::const_iterator found=modules_.find(id);
    if (found==modules_.end()) return ExecutionResult(Status::NotFound,std::string(),id);
    if (!has_capabilities(found->second->descriptor(),request.granted_capabilities))
        return ExecutionResult(Status::MissingCapability,std::string(),id);
    try {
        ExecutionResult result=found->second->execute(request);
        result.module_id=id;
        return result;
    } catch (...) {
        return ExecutionResult(Status::ModuleFailure,std::string(),id);
    }
}
std::vector<std::string> Registry::module_ids() const {
    std::vector<std::string> ids;
    for (std::map<std::string,Module*>::const_iterator it=modules_.begin();it!=modules_.end();++it)
        ids.push_back(it->first);
    return ids;
}
std::size_t Registry::size() const { return modules_.size(); }
const char* status_name(Status s) {
    switch(s) {
        case Status::Ok: return "ok";
        case Status::InvalidDescriptor: return "invalid_descriptor";
        case Status::DuplicateModule: return "duplicate_module";
        case Status::MissingCapability: return "missing_capability";
        case Status::ModuleFailure: return "module_failure";
        case Status::NotFound: return "not_found";
    }
    return "unknown";
}
} }
