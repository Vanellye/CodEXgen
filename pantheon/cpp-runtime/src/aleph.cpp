#include "pantheon/aleph.hpp"

namespace pantheon {

Aleph::Aleph()
    : mutex_(), state_(AlephState::READY), reason_(), actions_() {}

bool Aleph::recordRecoveryAction(
        const std::string& label,
        const std::function<bool()>& reverseAction) {
    if (label.empty() || !reverseAction) return false;
    std::lock_guard<std::mutex> lock(mutex_);
    if (state_ != AlephState::READY) return false;
    actions_.push_back(RecoveryAction(label, reverseAction));
    return true;
}

void Aleph::engage(const std::string& reason) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (state_ == AlephState::READY) {
        state_ = AlephState::SAFE_HOLD;
        reason_ = reason.empty() ? "execution_failed" : reason;
    }
}

AlephState Aleph::state() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return state_;
}

std::string Aleph::reason() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return reason_;
}

AlephRecoveryReport Aleph::reverse(const AlephApproval& approval) {
    AlephRecoveryReport report;
    std::lock_guard<std::mutex> lock(mutex_);

    if (state_ != AlephState::SAFE_HOLD &&
        state_ != AlephState::RECOVERY_INCOMPLETE) {
        report.reason = "aleph_not_in_safe_hold";
        return report;
    }
    if (!approval.approvedByAuthorizedOwner()) {
        report.reason = "authorized_owner_approval_required";
        return report;
    }

    for (std::vector<RecoveryAction>::const_iterator it = actions_.begin();
         it != actions_.end(); ++it) {
        if (!it->completed) ++report.attempted;
    }

    for (std::vector<RecoveryAction>::reverse_iterator it = actions_.rbegin();
         it != actions_.rend(); ++it) {
        if (it->completed) continue;
        bool ok = false;
        try {
            ok = it->reverse();
        } catch (...) {
            ok = false;
        }
        if (!ok) {
            report.reason = "reverse_action_failed:" + it->label;
            state_ = AlephState::RECOVERY_INCOMPLETE;
            return report;
        }
        it->completed = true;
        ++report.succeeded;
    }

    state_ = AlephState::RECOVERED;
    report.completed = true;
    report.reason = "reversed_in_dependency_order";
    return report;
}

} // namespace pantheon
