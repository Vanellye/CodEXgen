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
static void register_fixtures(Registry& registry, Echo& echo, Failure& failure) {
    assert(registry.add(&echo)==Status::Ok);
    assert(registry.add(&failure)==Status::Ok);
}
static void run_fixture(HostSimulator& sim, ExecutionRequest& request) {
    sim.set_state("mode","baseline"); sim.checkpoint();
    ExecutionResult ok=sim.run("fixture.echo",request,RecoveryAction::None);
    assert(ok.status==Status::Ok && ok.output=="fixture-input");
    sim.set_state("mode","mutated");
    ExecutionResult bad=sim.run("fixture.failure",request,RecoveryAction::RestoreCheckpoint);
    assert(bad.status==Status::ModuleFailure);
    std::string mode;
    assert(sim.get_state("mode",&mode) && mode=="baseline");
    assert(!sim.safe_hold());
}
int main() {
    Echo echo; Failure failure; Registry registry;
    register_fixtures(registry,echo,failure);
    ExecutionRequest request; request.input="fixture-input";
    request.granted_capabilities.insert(Capability::ReadLocalState);
    HostSimulator first(registry), replay(registry);
    run_fixture(first,request); run_fixture(replay,request);
    const std::vector<TraceEvent>& a=first.trace().events();
    const std::vector<TraceEvent>& b=replay.trace().events();
    assert(a.size()==5 && b.size()==a.size());
    for (std::size_t i=0;i<a.size();++i) {
        assert(a[i].sequence==i+1 && b[i].sequence==a[i].sequence);
        assert(a[i].kind==b[i].kind && a[i].module_id==b[i].module_id);
        assert(a[i].status==b[i].status && a[i].recovery==b[i].recovery);
    }
    assert(a[0].kind==EventKind::RunStarted);
    assert(a[1].kind==EventKind::ModuleCompleted);
    assert(a[2].kind==EventKind::RunStarted);
    assert(a[3].kind==EventKind::RecoveryRequested);
    assert(a[4].kind==EventKind::StateRestored);
    HostSimulator no_checkpoint(registry);
    no_checkpoint.run("fixture.failure",request,RecoveryAction::RestoreCheckpoint);
    assert(no_checkpoint.safe_hold());
    assert(no_checkpoint.run("fixture.echo",request,RecoveryAction::None).status==Status::ModuleFailure);
    no_checkpoint.clear_safe_hold();
    HostSimulator no_policy(registry);
    no_policy.run("fixture.failure",request,RecoveryAction::None);
    assert(no_policy.safe_hold());
    ExecutionRequest denied;
    HostSimulator permission_test(registry);
    permission_test.run("fixture.echo",denied,RecoveryAction::None);
    assert(permission_test.safe_hold());
    return 0;
}
