#ifndef CODEXGEN_HOST_SIMULATOR_HPP
#define CODEXGEN_HOST_SIMULATOR_HPP
#include "codexgen/framework.hpp"
#include <map>
#include <string>
#include <vector>
namespace codexgen { namespace framework {
enum class EventKind { RunStarted, ModuleCompleted, ModuleRejected, RecoveryRequested, StateRestored, SafeHoldEntered };
enum class RecoveryAction { None, RestoreCheckpoint, EnterSafeHold };
struct TraceEvent {
    unsigned long sequence;
    EventKind kind;
    std::string module_id;
    Status status;
    RecoveryAction recovery;
    std::string detail;
};
class EventTrace {
public:
    void append(EventKind kind, const std::string& module_id, Status status,
                RecoveryAction recovery, const std::string& detail);
    const std::vector<TraceEvent>& events() const;
    void clear();
private:
    std::vector<TraceEvent> events_;
};
class HostSimulator {
public:
    explicit HostSimulator(Registry& registry);
    void set_state(const std::string& key, const std::string& value);
    bool get_state(const std::string& key, std::string* value) const;
    void checkpoint();
    bool has_checkpoint() const;
    ExecutionResult run(const std::string& module_id,
                        const ExecutionRequest& request,
                        RecoveryAction recovery);
    bool safe_hold() const;
    const EventTrace& trace() const;
    void clear_safe_hold();
private:
    Registry& registry_;
    std::map<std::string, std::string> state_;
    std::map<std::string, std::string> checkpoint_;
    bool checkpoint_valid_;
    bool safe_hold_;
    EventTrace trace_;
};
const char* event_kind_name(EventKind kind);
const char* recovery_action_name(RecoveryAction action);
} }
#endif
