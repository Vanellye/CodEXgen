package com.vanellye.eria.contracts

/** Maps minimized ERIA painting/audio descriptors into the existing TRUE NORTH envelope. */
data class ResonantPaintingExport(
    val recordId: String,
    val observedAt: String,
    val artworkSourceRef: String,
    val artworkSha256: String,
    val artworkBytes: Long,
    val audioFeatures: Map<String, Any?>,
    val paintingFeatures: Map<String, Any?>,
    val style: String,
    val operation: String? = null,
    val operationVersion: String = "3.0.0",
    val parametersSha256: String? = null
)

object ResonantPaintingDataAdapter {
    private const val SOURCE = "eria.resonant-pattern-painting"

    fun toEnvelope(export: ResonantPaintingExport): DataEnvelope {
        val payload = linkedMapOf<String, Any?>(
            "paintingRecordId" to export.recordId,
            "artworkSha256" to export.artworkSha256,
            "artworkBytes" to export.artworkBytes,
            "audioFeatures" to export.audioFeatures,
            "paintingFeatures" to export.paintingFeatures,
            "style" to export.style,
            "microphoneAudioStored" to false,
            "interpretationStatus" to "descriptive-measurements-only"
        )
        val units = mapOf(
            "rms" to "normalized-amplitude", "peak" to "normalized-amplitude",
            "centroid_hz" to "Hz", "dominant_hz" to "Hz",
            "spectral_flux" to "normalized-relative-energy",
            "zero_crossing_rate" to "crossings-per-sample",
            "low_band" to "normalized-energy-ratio", "mid_band" to "normalized-energy-ratio",
            "high_band" to "normalized-energy-ratio", "brightness" to "normalized-luminance",
            "stroke_count" to "count", "point_count" to "count",
            "canvas_width" to "px", "canvas_height" to "px", "artworkBytes" to "byte"
        )
        val transformations = export.operation?.let {
            listOf(DataTransformation(it, export.operationVersion,
                export.parametersSha256, export.artworkSha256))
        } ?: emptyList()

        return DataEnvelope(
            recordId = export.recordId, schemaVersion = 1, source = SOURCE,
            observedAt = export.observedAt, payload = payload, units = units,
            quality = DataQuality.UNCALIBRATED,
            provenance = DataProvenance(
                sourceRef = export.artworkSourceRef,
                sourceDigest = export.artworkSha256,
                signatureStatus = "not_present"
            ),
            transformations = transformations,
            authorization = DataAuthorization(
                status = AuthorizationStatus.NOT_AUTHORIZED,
                scope = emptyList(), approvalRef = null
            ),
            validation = mapOf(
                "measurementBasis" to "browser-Web-Audio-AnalyserNode-FFT",
                "humanReviewRequired" to "true",
                "rawMicrophoneAudioPersisted" to "false"
            ),
            retention = mapOf(
                "policy" to "local-user-controlled",
                "rawAudio" to "not-collected-or-stored"
            )
        )
    }

    /** Structural validation only. NOT_AUTHORIZED intentionally remains a hold. */
    fun validateStructure(export: ResonantPaintingExport): List<String> =
        DataEnvelopeValidator.validate(toEnvelope(export))
}
