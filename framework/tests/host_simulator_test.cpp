#include "codexgen/host_simulator.hpp"
#include <cassert>
using namespace codexgen::framework;
class Echo : public Module {
public:
    ModuleDescriptor descriptor() const {
        ModuleDescriptor d; d.id="fixture.echo"; d.version="1.0.0";
        d.required_capabilities.push_back(Capability::ReadLocalState); return d;
    }
    ExecutionResult execute(const ExecutionRequest& r) {
        return ExecutionResult(Status::Ok,r.input);
    }
};
class Failure : public Module {
public:
    ModuleDescriptor descriptor() const {
        ModuleDescriptor d; d.id="fixture.failure"; d.version="1.0.0"; return d;
    }
    ExecutionResult execute(const ExecutionRequest&) {
        return ExecutionResult(Status::ModuleFailure);
    }
};
int main() {
    Registry registry; Echo echo; Failure failure;
    assert(registry.add(&echo)==Status::Ok);
    assert(registry.add(&failure)==Status::Ok);
    HostSimulator sim(registry);
    sim.set_state("mode","baseline"); sim.checkpoint();
    ExecutionRequest request; request.input="fixture-input";
    request.granted_capabilities.insert(Capability::ReadLocalState);
    ExecutionResult ok=sim.run("fixture.echo",request,RecoveryAction::None);
    assert(ok.status==Status::Ok && ok.output=="fixture-input");
    sim.set_state("mode","mutated");
    ExecutionResult bad=sim.run("fixture.failure",request,RecoveryAction::RestoreCheckpoint);
    assert(bad.status==Status::ModuleFailure);
    std::string mode;
    assert(sim.get_state("mode",&mode) && mode=="baseline");
    assert(!sim.safe_hold());
    const std::vector<TraceEvent>& events=sim.trace().events();
    assert(events.size()==5);
    for (std::size_t i=0;i<events.size();++i)
        assert(events[i].sequence==i+1);
    assert(events[0].kind==EventKind::RunStarted);
    assert(events[1].kind==EventKind::ModuleCompleted);
    assert(events[2].kind==EventKind::RunStarted);
    assert(events[3].kind==EventKind::RecoveryRequested);
    assert(events[4].kind==EventKind::StateRestored);
    HostSimulator no_checkpoint(registry);
    no_checkpoint.run("fixture.failure",request,RecoveryAction::RestoreCheckpoint);
    assert(no_checkpoint.safe_hold());
    ExecutionResult blocked=no_checkpoint.run("fixture.echo",request,RecoveryAction::None);
    assert(blocked.status==Status::ModuleFailure);
    no_checkpoint.clear_safe_hold();
    assert(!no_checkpoint.safe_hold());
    return 0;
}
