#include "codexgen/transendiant_filter.hpp"
#include <cassert>
#include <string>
#include <vector>

using namespace codexgen::framework;

static TransendiantRecord base_record(const std::string& id) {
    TransendiantRecord record;
    record.record_id = id;
    record.origin_realm = "realm.origin";
    record.destination_realm = "realm.target";
    record.expression = "Don / dapper";
    return record;
}

int main() {
    TransendiantPulseFilter filter;
    std::vector<TransendiantRecord> records;

    TransendiantRecord unresolved = base_record("record-unresolved");
    records.push_back(unresolved);

    TransendiantRecord restored = base_record("record-restored");
    restored.decision = SpliceDecision::Yes;
    restored.source_verified = true;
    restored.destination_verified = true;
    restored.authorization_verified = true;
    restored.provenance_ref = "origin:commit-123";
    restored.evidence_ref = "evidence:test-456";
    restored.canonical_expression = "Don / dapper";
    records.push_back(restored);

    TransendiantRecord incomplete = base_record("record-incomplete");
    incomplete.decision = SpliceDecision::Yes;
    incomplete.canonical_expression = "Don / dapper";
    records.push_back(incomplete);

    TransendiantRecord rejected = base_record("record-rejected");
    rejected.decision = SpliceDecision::No;
    records.push_back(rejected);

    TransendiantRecord blocked = base_record("record-blocked");
    blocked.decision = SpliceDecision::Cant;
    records.push_back(blocked);

    TransendiantRecord malformed = base_record("bad id");
    records.push_back(malformed);

    const std::vector<TransendiantPulse> pulses = filter.process(records);
    assert(pulses.size() == records.size());

    // Deterministic disposition order: BLOCKED, QUARANTINED, REJECTED,
    // PRESERVED, RESTORED. Sequence numbers are assigned after sorting.
    assert(pulses[0].disposition == PulseDisposition::Blocked);
    assert(pulses[1].disposition == PulseDisposition::Quarantined);
    assert(pulses[2].disposition == PulseDisposition::Rejected);
    assert(pulses[3].disposition == PulseDisposition::Preserved);
    assert(pulses[4].disposition == PulseDisposition::Preserved);
    assert(pulses[5].disposition == PulseDisposition::Restored);

    for (std::size_t i = 0; i < pulses.size(); ++i)
        assert(pulses[i].sequence == i + 1);

    // Incomplete evidence never becomes certainty or changes the expression.
    assert(pulses[3].original_expression == "Don / dapper");
    assert(pulses[3].emitted_expression == "Don / dapper");
    assert(!pulses[3].splice_released);

    // An authorized, evidenced YES may release the isolated splice.
    assert(pulses[5].splice_isolated);
    assert(pulses[5].splice_released);
    assert(pulses[5].emitted_expression == "Don / dapper");

    // A slash embedded in a path-like token is not the isolated splice token.
    TransendiantRecord path = base_record("record-path");
    path.expression = "realm.origin/Don";
    const std::vector<TransendiantPulse> path_pulses =
        filter.process(std::vector<TransendiantRecord>(1, path));
    assert(!path_pulses[0].splice_isolated);

    // Reordering input does not change the sorted pulse identity order.
    std::vector<TransendiantRecord> reversed(records.rbegin(), records.rend());
    const std::vector<TransendiantPulse> reordered = filter.process(reversed);
    assert(reordered.size() == pulses.size());
    for (std::size_t i = 0; i < pulses.size(); ++i)
        assert(reordered[i].record_id == pulses[i].record_id);

    assert(std::string(pulse_disposition_name(PulseDisposition::Preserved)) == "PRESERVED");
    return 0;
}
