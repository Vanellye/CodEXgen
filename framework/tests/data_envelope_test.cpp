#include "codexgen/data_envelope.hpp"
#include <cassert>
#include <string>

using namespace codexgen::framework;

static DataEnvelope valid_record() {
    DataEnvelope record;
    record.record_id = "sensor.sample-001";
    record.source = "device.sensor-a";
    record.observed_at = "2026-11-09T19:00:00-06:00";
    record.payload_json = "{\"reading\":0,\"enabled\":false,\"note\":null}";
    record.units["reading"] = "milli-unit";
    record.quality = DataQuality::Valid;
    record.has_monotonic_time = true;
    record.monotonic_time.value = 123456;
    record.monotonic_time.clock_domain = "device.boot-7";
    record.provenance.source_digest = std::string(64, 'a');
    record.provenance.signature_status = "unverified";
    return record;
}

int main() {
    DataEnvelope record = valid_record();
    assert(validate_data_envelope(record).empty());
    assert(record.payload_json == "{\"reading\":0,\"enabled\":false,\"note\":null}");

    DataEnvelope bad_time = record;
    bad_time.observed_at = "2026-11-09T19:00:00";
    assert(!validate_data_envelope(bad_time).empty());

    DataEnvelope bad_digest = record;
    bad_digest.provenance.source_digest = "not-a-digest";
    assert(!validate_data_envelope(bad_digest).empty());

    DataEnvelope bad_clock = record;
    bad_clock.monotonic_time.value = -1;
    assert(!validate_data_envelope(bad_clock).empty());

    DataEnvelope unauthorized = record;
    unauthorized.authorization.scope.push_back("export.bundle");
    assert(!validate_data_envelope(unauthorized).empty());

    DataEnvelope authorized = record;
    authorized.authorization.status = AuthorizationStatus::Authorized;
    authorized.authorization.scope.push_back("export.bundle");
    authorized.authorization.approval_ref = "approval-123";
    assert(validate_data_envelope(authorized).empty());

    DataEnvelope wrong_schema = record;
    wrong_schema.schema_version = 2;
    assert(!validate_data_envelope(wrong_schema).empty());
    return 0;
}
