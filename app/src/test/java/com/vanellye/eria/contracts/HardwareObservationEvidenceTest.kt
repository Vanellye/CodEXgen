package com.vanellye.eria.contracts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class HardwareObservationEvidenceTest {
    @Test
    fun recordsRawMeasurementAsObservationWithoutClaimingItIsAuthenticated() {
        val raw = byteArrayOf(10, 20, 30, 40)
        val evidence = HardwareObservationRecorder.capture(
            deviceId = "device-under-test",
            instrumentId = "sensor-01",
            capturedAtEpochMillis = 1_800_000_000_000L,
            acquisitionMethod = "direct sensor export",
            calibrationReference = "calibration-record-2026-11",
            measurementUncertainty = "manufacturer tolerance; independent calibration pending",
            rawData = raw
        )

        raw[0] = 99
        assertTrue(evidence.hardwareObserved)
        assertFalse(evidence.simulatedOnly)
        assertTrue(evidence.rawData().contentEquals(byteArrayOf(10, 20, 30, 40)))
        assertEquals(evidence, HardwareObservationGate.requireObservation(evidence))
        assertTrue(evidence.observationId.matches(Regex("^[0-9a-f]{64}$")))
        assertTrue(evidence.rawDataSha256.matches(Regex("^[0-9a-f]{64}$")))
    }

    @Test
    fun observationMayReferenceSimulationButDoesNotInheritItsEvidenceClass() {
        val simulationId = "a".repeat(64)
        val evidence = HardwareObservationRecorder.capture(
            deviceId = "fold-device",
            instrumentId = "microphone-input",
            capturedAtEpochMillis = 1_800_000_000_001L,
            acquisitionMethod = "PCM capture",
            calibrationReference = "not-yet-independently-calibrated",
            measurementUncertainty = "unknown; calibration required",
            rawData = byteArrayOf(1, 2, 3),
            relatedSimulationEvidenceId = simulationId
        )

        assertEquals(simulationId, evidence.relatedSimulationEvidenceId)
        assertTrue(evidence.hardwareObserved)
        assertFalse(evidence.simulatedOnly)
        HardwareObservationGate.requireObservation(evidence)
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsMissingPhysicalBytes() {
        HardwareObservationRecorder.capture(
            deviceId = "device",
            instrumentId = "sensor",
            capturedAtEpochMillis = 1L,
            acquisitionMethod = "direct",
            calibrationReference = "calibration",
            measurementUncertainty = "unknown",
            rawData = byteArrayOf()
        )
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsMissingUncertaintyStatement() {
        HardwareObservationRecorder.capture(
            deviceId = "device",
            instrumentId = "sensor",
            capturedAtEpochMillis = 1L,
            acquisitionMethod = "direct",
            calibrationReference = "calibration",
            measurementUncertainty = " ",
            rawData = byteArrayOf(1)
        )
    }
}
