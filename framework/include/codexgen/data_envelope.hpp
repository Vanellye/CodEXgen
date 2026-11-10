#ifndef CODEXGEN_DATA_ENVELOPE_HPP
#define CODEXGEN_DATA_ENVELOPE_HPP

#include <map>
#include <regex>
#include <string>
#include <vector>

namespace codexgen { namespace framework {

enum class DataQuality {
    Valid, Stale, OutOfRange, Uncalibrated, SensorFault, Unknown
};

enum class AuthorizationStatus {
    NotAuthorized, Authorized, Declined
};

struct MonotonicTime {
    long long value;
    std::string clock_domain;
    MonotonicTime() : value(0) {}
};

struct DataProvenance {
    std::string source_ref;
    std::string source_commit;
    std::string source_digest;
    std::string signer;
    std::string signature_status;
    DataProvenance() : signature_status("not_present") {}
};

struct DataTransformation {
    std::string operation;
    std::string version;
    std::string parameters_digest;
    std::string output_digest;
};

struct DataAuthorization {
    AuthorizationStatus status;
    std::vector<std::string> scope;
    std::string approval_ref;
    DataAuthorization() : status(AuthorizationStatus::NotAuthorized) {}
};

/**
 * Portable C++11 representation of the TRUE NORTH data envelope.
 *
 * payload_json is preserved verbatim. Parsing and canonical JSON encoding
 * belong to the host adapter. Validation does not authorize execution.
 */
struct DataEnvelope {
    int schema_version;
    std::string record_id;
    std::string source;
    std::string observed_at;
    bool has_monotonic_time;
    MonotonicTime monotonic_time;
    std::string payload_json;
    std::map<std::string, std::string> units;
    DataQuality quality;
    DataProvenance provenance;
    std::vector<DataTransformation> transformations;
    DataAuthorization authorization;
    std::map<std::string, std::string> validation;
    std::map<std::string, std::string> retention;

    DataEnvelope()
        : schema_version(1), has_monotonic_time(false), quality(DataQuality::Unknown) {}
};

inline bool is_stable_identifier(const std::string& value) {
    static const std::regex pattern("^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$");
    return std::regex_match(value, pattern);
}

inline bool is_sha256_digest(const std::string& value) {
    static const std::regex pattern("^[0-9a-f]{64}$");
    return std::regex_match(value, pattern);
}

inline bool is_offset_timestamp(const std::string& value) {
    static const std::regex pattern(
        "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(Z|[+-][0-9]{2}:[0-9]{2})$");
    return std::regex_match(value, pattern);
}

inline std::vector<std::string> validate_data_envelope(const DataEnvelope& record) {
    std::vector<std::string> errors;
    if (record.schema_version != 1) errors.push_back("schema_version must equal 1");
    if (!is_stable_identifier(record.record_id)) errors.push_back("record_id is invalid");
    if (!is_stable_identifier(record.source)) errors.push_back("source is invalid");
    if (!is_offset_timestamp(record.observed_at)) errors.push_back("observed_at requires an ISO-8601 timezone");
    if (record.payload_json.empty()) errors.push_back("payload_json must not be empty");

    if (record.has_monotonic_time) {
        if (record.monotonic_time.value < 0) errors.push_back("monotonic_time must be non-negative");
        if (!is_stable_identifier(record.monotonic_time.clock_domain))
            errors.push_back("monotonic_time clock_domain is invalid");
    }

    for (std::map<std::string, std::string>::const_iterator it = record.units.begin();
         it != record.units.end(); ++it) {
        if (it->first.empty() || it->second.empty()) errors.push_back("unit keys and values must be non-empty");
    }

    if (!record.provenance.source_digest.empty() &&
        !is_sha256_digest(record.provenance.source_digest))
        errors.push_back("provenance source_digest must be lowercase SHA-256");
    if (record.provenance.signature_status != "not_present" &&
        record.provenance.signature_status != "valid" &&
        record.provenance.signature_status != "invalid" &&
        record.provenance.signature_status != "unverified")
        errors.push_back("provenance signature_status is invalid");

    for (std::size_t i = 0; i < record.transformations.size(); ++i) {
        const DataTransformation& item = record.transformations[i];
        if (!is_stable_identifier(item.operation)) errors.push_back("transformation operation is invalid");
        if (!is_stable_identifier(item.version)) errors.push_back("transformation version is invalid");
        if (!item.parameters_digest.empty() && !is_sha256_digest(item.parameters_digest))
            errors.push_back("transformation parameters_digest is invalid");
        if (!item.output_digest.empty() && !is_sha256_digest(item.output_digest))
            errors.push_back("transformation output_digest is invalid");
    }

    if (record.authorization.status == AuthorizationStatus::Authorized) {
        if (record.authorization.scope.empty()) errors.push_back("authorized record requires a non-empty scope");
        for (std::size_t i = 0; i < record.authorization.scope.size(); ++i) {
            if (!is_stable_identifier(record.authorization.scope[i]))
                errors.push_back("authorization scope contains an invalid identifier");
        }
        if (!is_stable_identifier(record.authorization.approval_ref))
            errors.push_back("authorized record requires an approval_ref");
    } else {
        if (!record.authorization.scope.empty()) errors.push_back("non-authorized record cannot declare approved scope");
        if (!record.authorization.approval_ref.empty()) errors.push_back("non-authorized record cannot contain approval_ref");
    }
    return errors;
}

} } // namespace codexgen::framework

#endif
