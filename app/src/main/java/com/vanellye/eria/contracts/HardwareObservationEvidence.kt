package com.vanellye.eria.contracts

import java.security.MessageDigest

/**
 * A physical observation is a separate evidence type from SimulationEvidence.
 * This record proves only that raw bytes and acquisition metadata were recorded;
 * it does not authenticate the instrument, calibration, operator, or physical truth.
 */
class HardwareObservationEvidence internal constructor(
    val observationId: String,
    val deviceId: String,
    val instrumentId: String,
    val capturedAtEpochMillis: Long,
    val acquisitionMethod: String,
    val calibrationReference: String,
    val measurementUncertainty: String,
    val rawDataSha256: String,
    val relatedSimulationEvidenceId: String?,
    rawData: ByteArray
) {
    private val rawDataSnapshot = rawData.copyOf()

    val simulatedOnly: Boolean = false
    val hardwareObserved: Boolean = true

    fun rawData(): ByteArray = rawDataSnapshot.copyOf()
}

/** Creates observation records only from supplied physical-acquisition bytes and metadata. */
object HardwareObservationRecorder {
    fun capture(
        deviceId: String,
        instrumentId: String,
        capturedAtEpochMillis: Long,
        acquisitionMethod: String,
        calibrationReference: String,
        measurementUncertainty: String,
        rawData: ByteArray,
        relatedSimulationEvidenceId: String? = null
    ): HardwareObservationEvidence {
        require(deviceId.isNotBlank()) { "deviceId is required" }
        require(instrumentId.isNotBlank()) { "instrumentId is required" }
        require(capturedAtEpochMillis > 0L) { "a positive capture timestamp is required" }
        require(acquisitionMethod.isNotBlank()) { "acquisitionMethod is required" }
        require(calibrationReference.isNotBlank()) { "calibrationReference is required" }
        require(measurementUncertainty.isNotBlank()) { "measurementUncertainty must be stated" }
        require(rawData.isNotEmpty()) { "raw physical observation bytes are required" }
        require(relatedSimulationEvidenceId == null ||
            relatedSimulationEvidenceId.matches(Regex("^[0-9a-f]{64}$"))) {
            "related simulation reference must be a SHA-256 evidence ID"
        }

        val snapshot = rawData.copyOf()
        val digest = sha256(snapshot)
        val id = sha256(
            listOf(
                deviceId, instrumentId, capturedAtEpochMillis.toString(),
                acquisitionMethod, calibrationReference, measurementUncertainty,
                digest, relatedSimulationEvidenceId.orEmpty()
            ).joinToString("\u0000").toByteArray(Charsets.UTF_8)
        )
        return HardwareObservationEvidence(
            observationId = id,
            deviceId = deviceId,
            instrumentId = instrumentId,
            capturedAtEpochMillis = capturedAtEpochMillis,
            acquisitionMethod = acquisitionMethod,
            calibrationReference = calibrationReference,
            measurementUncertainty = measurementUncertainty,
            rawDataSha256 = digest,
            relatedSimulationEvidenceId = relatedSimulationEvidenceId,
            rawData = snapshot
        )
    }

    private fun sha256(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes)
            .joinToString("") { "%02x".format(it) }
}

/**
 * Validates the structure and integrity of a hardware-observation record.
 * It intentionally accepts no SimulationEvidence and never declares PONS READY.
 */
object HardwareObservationGate {
    fun requireObservation(evidence: HardwareObservationEvidence): HardwareObservationEvidence {
        require(evidence.hardwareObserved && !evidence.simulatedOnly) {
            "Simulation evidence cannot be promoted to hardware observation"
        }
        require(evidence.rawData().isNotEmpty()) { "raw observation data is missing" }
        val actualDigest = MessageDigest.getInstance("SHA-256").digest(evidence.rawData())
            .joinToString("") { "%02x".format(it) }
        require(actualDigest == evidence.rawDataSha256) { "raw observation digest mismatch" }
        require(evidence.deviceId.isNotBlank() && evidence.instrumentId.isNotBlank()) {
            "device and instrument identity are required"
        }
        require(evidence.calibrationReference.isNotBlank()) {
            "calibration reference is required"
        }
        require(evidence.measurementUncertainty.isNotBlank()) {
            "measurement uncertainty must remain explicit"
        }
        return evidence
    }
}
