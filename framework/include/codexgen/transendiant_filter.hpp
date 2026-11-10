#ifndef CODEXGEN_TRANSEDIANT_FILTER_HPP
#define CODEXGEN_TRANSEDIANT_FILTER_HPP

#include <algorithm>
#include <string>
#include <vector>

namespace codexgen { namespace framework {

enum class SpliceDecision { Unresolved, Yes, No, Cant };
enum class PulseDisposition { Blocked, Quarantined, Rejected, Preserved, Restored };

struct TransendiantRecord {
    std::string record_id;
    std::string origin_realm;
    std::string destination_realm;
    std::string expression;
    std::string canonical_expression;
    std::string provenance_ref;
    std::string evidence_ref;
    SpliceDecision decision;
    bool source_verified;
    bool destination_verified;
    bool authorization_verified;

    TransendiantRecord()
        : decision(SpliceDecision::Unresolved),
          source_verified(false),
          destination_verified(false),
          authorization_verified(false) {}
};

struct TransendiantPulse {
    unsigned long long sequence;
    std::string record_id;
    std::string origin_realm;
    std::string destination_realm;
    std::string original_expression;
    std::string emitted_expression;
    PulseDisposition disposition;
    bool splice_isolated;
    bool splice_released;
    std::string reason;

    TransendiantPulse()
        : sequence(0), disposition(PulseDisposition::Preserved),
          splice_isolated(false), splice_released(false) {}
};

/**
 * Deterministic cross-realm filter.
 *
 * It never infers semantic equivalence from spelling or sound. Restoration
 * requires an explicit YES, verified endpoints, explicit authorization,
 * provenance, evidence, and a caller-supplied canonical expression.
 * Uncertainty is preserved as a first-class outcome, never coerced to YES/NO.
 *
 * This class does not perform network transport, cryptography, or NLP.
 * Adapters must verify provenance/evidence and authorization before setting
 * the corresponding flags.
 */
class TransendiantPulseFilter {
public:
    std::vector<TransendiantPulse> process(
        const std::vector<TransendiantRecord>& records) const {
        std::vector<TransendiantPulse> pulses;
        pulses.reserve(records.size());

        for (std::size_t i = 0; i < records.size(); ++i) {
            pulses.push_back(classify(records[i]));
        }

        std::stable_sort(pulses.begin(), pulses.end(),
            [](const TransendiantPulse& a, const TransendiantPulse& b) {
                if (a.disposition != b.disposition)
                    return static_cast<int>(a.disposition) < static_cast<int>(b.disposition);
                if (a.origin_realm != b.origin_realm)
                    return a.origin_realm < b.origin_realm;
                if (a.destination_realm != b.destination_realm)
                    return a.destination_realm < b.destination_realm;
                return a.record_id < b.record_id;
            });

        for (std::size_t i = 0; i < pulses.size(); ++i)
            pulses[i].sequence = static_cast<unsigned long long>(i + 1);
        return pulses;
    }

private:
    static bool valid_identifier(const std::string& value) {
        if (value.empty()) return false;
        for (std::size_t i = 0; i < value.size(); ++i) {
            const char c = value[i];
            const bool valid = (c >= 'a' && c <= 'z') ||
                               (c >= 'A' && c <= 'Z') ||
                               (c >= '0' && c <= '9') ||
                               c == '.' || c == '_' || c == ':' ||
                               c == '/' || c == '-';
            if (!valid) return false;
        }
        return true;
    }

    static TransendiantPulse classify(const TransendiantRecord& record) {
        TransendiantPulse pulse;
        pulse.record_id = record.record_id;
        pulse.origin_realm = record.origin_realm;
        pulse.destination_realm = record.destination_realm;
        pulse.original_expression = record.expression;
        pulse.emitted_expression = record.expression;
        pulse.splice_isolated = record.expression.find(" / ") != std::string::npos;

        if (!valid_identifier(record.record_id) ||
            !valid_identifier(record.origin_realm) ||
            !valid_identifier(record.destination_realm) ||
            record.expression.empty()) {
            pulse.disposition = PulseDisposition::Quarantined;
            pulse.reason = "invalid identity, realm, or empty expression; original data retained";
            return pulse;
        }

        if (record.decision == SpliceDecision::Cant) {
            pulse.disposition = PulseDisposition::Blocked;
            pulse.reason = "CANT constraint blocks cross-realm adoption";
            return pulse;
        }

        if (record.decision == SpliceDecision::No) {
            pulse.disposition = PulseDisposition::Rejected;
            pulse.reason = "explicit NO rejects this splice only; both endpoints remain";
            return pulse;
        }

        if (record.decision != SpliceDecision::Yes) {
            pulse.disposition = PulseDisposition::Preserved;
            pulse.reason = "decision unresolved; preserve expression and isolated splice";
            return pulse;
        }

        if (!record.source_verified || !record.destination_verified ||
            !record.authorization_verified || record.provenance_ref.empty() ||
            record.evidence_ref.empty() || record.canonical_expression.empty()) {
            pulse.disposition = PulseDisposition::Preserved;
            pulse.reason = "YES recorded, but evidence, provenance, endpoint verification, or authorization is incomplete";
            return pulse;
        }

        pulse.disposition = PulseDisposition::Restored;
        pulse.emitted_expression = record.canonical_expression;
        pulse.splice_released = pulse.splice_isolated;
        pulse.reason = "explicitly authorized and evidenced mapping restored";
        return pulse;
    }
};

inline const char* pulse_disposition_name(PulseDisposition disposition) {
    switch (disposition) {
        case PulseDisposition::Blocked: return "BLOCKED";
        case PulseDisposition::Quarantined: return "QUARANTINED";
        case PulseDisposition::Rejected: return "REJECTED";
        case PulseDisposition::Preserved: return "PRESERVED";
        case PulseDisposition::Restored: return "RESTORED";
    }
    return "UNKNOWN";
}

} } // namespace codexgen::framework

#endif
