#include "codexgen/host_simulator.hpp"
namespace codexgen { namespace framework {
void EventTrace::append(EventKind kind, const std::string& id, Status status,
                        RecoveryAction recovery, const std::string& detail) {
    TraceEvent event;
    event.sequence = static_cast<unsigned long>(events_.size()) + 1UL;
    event.kind = kind; event.module_id = id; event.status = status;
    event.recovery = recovery; event.detail = detail;
    events_.push_back(event);
}
const std::vector<TraceEvent>& EventTrace::events() const { return events_; }
void EventTrace::clear() { events_.clear(); }
HostSimulator::HostSimulator(Registry& registry)
    : registry_(registry), checkpoint_valid_(false), safe_hold_(false) {}
void HostSimulator::set_state(const std::string& key, const std::string& value) {
    state_[key] = value;
}
bool HostSimulator::get_state(const std::string& key, std::string* value) const {
    if (value == 0) return false;
    std::map<std::string,std::string>::const_iterator it=state_.find(key);
    if (it==state_.end()) return false;
    *value=it->second; return true;
}
void HostSimulator::checkpoint() { checkpoint_=state_; checkpoint_valid_=true; }
bool HostSimulator::has_checkpoint() const { return checkpoint_valid_; }
ExecutionResult HostSimulator::run(const std::string& id,
                                   const ExecutionRequest& request,
                                   RecoveryAction recovery) {
    if (safe_hold_) {
        trace_.append(EventKind::ModuleRejected,id,Status::ModuleFailure,
                      recovery,"simulator is in safe hold");
        return ExecutionResult(Status::ModuleFailure,std::string(),id);
    }
    trace_.append(EventKind::RunStarted,id,Status::Ok,recovery,"execution requested");
    ExecutionResult result=registry_.run(id,request);
    if (result.status==Status::Ok) {
        trace_.append(EventKind::ModuleCompleted,id,result.status,recovery,"execution completed");
        return result;
    }
    trace_.append(EventKind::RecoveryRequested,id,result.status,recovery,
                  "failure requires explicit recovery handling");
    if (recovery==RecoveryAction::RestoreCheckpoint && checkpoint_valid_) {
        state_=checkpoint_;
        trace_.append(EventKind::StateRestored,id,result.status,recovery,
                      "last explicit checkpoint restored");
    } else {
        safe_hold_=true;
        trace_.append(EventKind::SafeHoldEntered,id,result.status,recovery,
                      recovery==RecoveryAction::RestoreCheckpoint
                      ? "checkpoint unavailable; fail closed"
                      : "no approved recovery path; fail closed");
    }
    return result;
}
bool HostSimulator::safe_hold() const { return safe_hold_; }
const EventTrace& HostSimulator::trace() const { return trace_; }
void HostSimulator::clear_safe_hold() { safe_hold_=false; }
const char* event_kind_name(EventKind kind) {
    switch(kind) {
        case EventKind::RunStarted: return "run_started";
        case EventKind::ModuleCompleted: return "module_completed";
        case EventKind::ModuleRejected: return "module_rejected";
        case EventKind::RecoveryRequested: return "recovery_requested";
        case EventKind::StateRestored: return "state_restored";
        case EventKind::SafeHoldEntered: return "safe_hold_entered";
    }
    return "unknown";
}
const char* recovery_action_name(RecoveryAction action) {
    switch(action) {
        case RecoveryAction::None: return "none";
        case RecoveryAction::RestoreCheckpoint: return "restore_checkpoint";
        case RecoveryAction::EnterSafeHold: return "enter_safe_hold";
    }
    return "unknown";
}
} }
