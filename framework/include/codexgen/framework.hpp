#ifndef CODEXGEN_FRAMEWORK_HPP
#define CODEXGEN_FRAMEWORK_HPP
#include <map>
#include <set>
#include <string>
#include <vector>
namespace codexgen { namespace framework {
enum class Capability { ReadLocalState, WriteLocalState, EmitAuditEvent, UseNetwork, RequestActuation };
enum class Status { Ok, InvalidDescriptor, DuplicateModule, MissingCapability, ModuleFailure, NotFound };
struct ModuleDescriptor {
    std::string id;
    std::string version;
    std::vector<Capability> required_capabilities;
};
struct ExecutionRequest {
    std::string input;
    std::set<Capability> granted_capabilities;
};
struct ExecutionResult {
    Status status;
    std::string output;
    std::string module_id;
    ExecutionResult(Status value = Status::Ok, const std::string& text = std::string(),
                    const std::string& id = std::string())
        : status(value), output(text), module_id(id) {}
};
class Module {
public:
    virtual ~Module() {}
    virtual ModuleDescriptor descriptor() const = 0;
    virtual ExecutionResult execute(const ExecutionRequest& request) = 0;
};
class Registry {
public:
    Status add(Module* module);
    ExecutionResult run(const std::string& module_id, const ExecutionRequest& request) const;
    std::vector<std::string> module_ids() const;
    std::size_t size() const;
private:
    std::map<std::string, Module*> modules_;
};
const char* status_name(Status status);
} }
#endif
