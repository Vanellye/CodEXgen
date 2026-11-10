#ifndef CODEXGEN_FIRMWARE_CONTRACT_HPP
#define CODEXGEN_FIRMWARE_CONTRACT_HPP

#include <stdint.h>

namespace codexgen {
namespace firmware {

// Stable quality flags. A value is not trustworthy merely because it exists.
enum ObservationQuality {
    QUALITY_UNKNOWN = 0,
    QUALITY_VALID = 1,
    QUALITY_STALE = 2,
    QUALITY_OUT_OF_RANGE = 3,
    QUALITY_UNCALIBRATED = 4,
    QUALITY_SENSOR_FAULT = 5
};

struct Observation {
    uint32_t source_id;
    uint32_t channel_id;
    int64_t monotonic_time_ms;
    int32_t value_milli;
    uint16_t unit_code;
    ObservationQuality quality;

    Observation()
        : source_id(0), channel_id(0), monotonic_time_ms(0),
          value_milli(0), unit_code(0), quality(QUALITY_UNKNOWN) {}
};

enum DeviceHealthState {
    DEVICE_HEALTH_UNKNOWN = 0,
    DEVICE_HEALTH_READY = 1,
    DEVICE_HEALTH_DEGRADED = 2,
    DEVICE_HEALTH_FAULT = 3,
    DEVICE_HEALTH_SAFE_HOLD = 4
};

struct DeviceHealth {
    DeviceHealthState state;
    uint32_t fault_code;
    uint32_t uptime_seconds;

    DeviceHealth()
        : state(DEVICE_HEALTH_UNKNOWN), fault_code(0), uptime_seconds(0) {}
};

// Hardware-specific implementations are supplied by a selected board package.
class MonotonicClock {
public:
    virtual ~MonotonicClock() {}
    virtual int64_t nowMilliseconds() const = 0;
};

class ObservationSource {
public:
    virtual ~ObservationSource() {}
    virtual bool read(Observation& observation) = 0;
};

class HealthMonitor {
public:
    virtual ~HealthMonitor() {}
    virtual DeviceHealth currentHealth() const = 0;
};

// The generic contract intentionally exposes no actuator or remote-command API.
class LocalEventStore {
public:
    virtual ~LocalEventStore() {}
    virtual bool append(const Observation& observation) = 0;
    virtual bool appendHealth(const DeviceHealth& health,
                              int64_t monotonic_time_ms) = 0;
};

} // namespace firmware
} // namespace codexgen

#endif
