#ifndef PANTHEON_CONTROL_GATE_HPP
#define PANTHEON_CONTROL_GATE_HPP

#include <string>
#include <vector>

namespace pantheon {

struct StandardEvidence {
    unsigned int number;       // Canonical standard number: 1 through 38.
    bool passed;
    std::string evidenceReference; // Immutable audit/evidence identifier.
    StandardEvidence() : number(0), passed(false), evidenceReference() {}
    StandardEvidence(unsigned int n, bool p, const std::string& ref)
        : number(n), passed(p), evidenceReference(ref) {}
};

class OwnerApproval {
public:
    virtual ~OwnerApproval() {}
    // Implementations must return true only after authenticated owner approval.
    virtual bool approvedByAuthorizedOwner() const = 0;
};

struct ControlGateDecision {
    bool granted;
    unsigned int passedCount;
    std::string reason;
    ControlGateDecision() : granted(false), passedCount(0), reason("not_evaluated") {}
};

class ControlGate {
public:
    static const unsigned int REQUIRED_STANDARDS = 38;

    ControlGateDecision evaluate(const std::vector<StandardEvidence>& standards,
                                 const OwnerApproval& ownerApproval) const;
};

} // namespace pantheon

#endif
