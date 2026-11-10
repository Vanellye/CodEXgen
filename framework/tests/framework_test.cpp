#include "codexgen/framework.hpp"
#include <cassert>
#include <stdexcept>
using namespace codexgen::framework;
class EchoModule : public Module {
public:
    ModuleDescriptor descriptor() const {
        ModuleDescriptor d; d.id="test.echo"; d.version="1.0.0";
        d.required_capabilities.push_back(Capability::ReadLocalState); return d;
    }
    ExecutionResult execute(const ExecutionRequest& r) { return ExecutionResult(Status::Ok,r.input); }
};
class InvalidModule : public Module {
public:
    ModuleDescriptor descriptor() const { ModuleDescriptor d; d.version="1.0.0"; return d; }
    ExecutionResult execute(const ExecutionRequest&) { return ExecutionResult(Status::Ok); }
};
class ThrowingModule : public Module {
public:
    ModuleDescriptor descriptor() const { ModuleDescriptor d; d.id="test.throw"; d.version="1.0.0"; return d; }
    ExecutionResult execute(const ExecutionRequest&) { throw std::runtime_error("failure"); }
};
int main() {
    Registry registry; EchoModule echo; InvalidModule invalid; ThrowingModule throwing;
    assert(registry.add(0)==Status::InvalidDescriptor);
    assert(registry.add(&invalid)==Status::InvalidDescriptor);
    assert(registry.add(&echo)==Status::Ok);
    assert(registry.add(&echo)==Status::DuplicateModule);
    assert(registry.add(&throwing)==Status::Ok);
    assert(registry.size()==2);
    ExecutionRequest request; request.input="deterministic";
    assert(registry.run("test.echo",request).status==Status::MissingCapability);
    request.granted_capabilities.insert(Capability::ReadLocalState);
    ExecutionResult result=registry.run("test.echo",request);
    assert(result.status==Status::Ok && result.output=="deterministic");
    assert(result.module_id=="test.echo");
    assert(registry.run("missing.module",request).status==Status::NotFound);
    assert(registry.run("test.throw",request).status==Status::ModuleFailure);
    const std::vector<std::string> ids=registry.module_ids();
    assert(ids.size()==2 && ids[0]=="test.echo" && ids[1]=="test.throw");
    return 0;
}
