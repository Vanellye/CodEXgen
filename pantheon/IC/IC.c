#include "IC.h"

int ic_can_start(const ICGate *gate, int dependencies_passed) {
    if (gate == 0 || gate->state != IC_STAGE_PENDING) {
        return 0;
    }
    if (!dependencies_passed) {
        return 0;
    }
    if (gate->requires_approval && gate->approval != IC_APPROVAL_GRANTED) {
        return 0;
    }
    if (gate->approval == IC_APPROVAL_DENIED) {
        return 0;
    }
    return 1;
}

int ic_start(ICGate *gate, int dependencies_passed) {
    if (gate == 0 || gate->state != IC_STAGE_PENDING) {
        return 0;
    }
    if (!dependencies_passed ||
        gate->approval == IC_APPROVAL_DENIED ||
        (gate->requires_approval && gate->approval != IC_APPROVAL_GRANTED)) {
        gate->state = IC_STAGE_BLOCKED;
        return 0;
    }
    gate->state = IC_STAGE_RUNNING;
    return 1;
}

int ic_finish(ICGate *gate, int checks_passed) {
    if (gate == 0 || gate->state != IC_STAGE_RUNNING) {
        return 0;
    }
    gate->state = checks_passed ? IC_STAGE_PASSED : IC_STAGE_FAILED;
    return 1;
}

int ic_can_publish(const ICGate *gate, int all_quality_checks_passed) {
    if (gate == 0 || gate->state != IC_STAGE_PASSED ||
        !all_quality_checks_passed) {
        return 0;
    }
    if (gate->approval != IC_APPROVAL_GRANTED) {
        return 0;
    }
    return 1;
}
