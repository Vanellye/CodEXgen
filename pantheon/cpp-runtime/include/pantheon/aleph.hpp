#ifndef PANTHEON_ALEPH_HPP
#define PANTHEON_ALEPH_HPP

#include <functional>
#include <mutex>
#include <string>
#include <vector>

namespace pantheon {

class AlephApproval {
public:
    virtual ~AlephApproval() {}
    virtual bool approvedByAuthorizedOwner() const = 0;
};

enum class AlephState {
    READY,
    SAFE_HOLD,
    RECOVERED,
    RECOVERY_INCOMPLETE
};

struct AlephRecoveryReport {
    bool completed;
    unsigned int attempted;
    unsigned int succeeded;
    std::string reason;

    AlephRecoveryReport()
        : completed(false), attempted(0), succeeded(0), reason("not_started") {}
};

// ALEPH automatically enters SAFE_HOLD when Runtime observes a failed result.
// Reversal is limited to explicitly registered compensating actions and requires
// owner approval. It never rewrites Git history or assumes arbitrary side effects
// can be undone.
class Aleph {
public:
    Aleph();

    bool recordRecoveryAction(const std::string& label,
                              const std::function<bool()>& reverseAction);
    void engage(const std::string& reason);
    AlephState state() const;
    std::string reason() const;
    AlephRecoveryReport reverse(const AlephApproval& approval);

private:
    struct RecoveryAction {
        std::string label;
        std::function<bool()> reverse;
        bool completed;
        RecoveryAction(const std::string& value,
                       const std::function<bool()>& action)
            : label(value), reverse(action), completed(false) {}
    };

    mutable std::mutex mutex_;
    AlephState state_;
    std::string reason_;
    std::vector<RecoveryAction> actions_;
};

} // namespace pantheon

#endif
