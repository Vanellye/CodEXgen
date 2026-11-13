package com.vanellye.eria.contracts

import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.util.UUID

/** Original writing is immutable; every derivative is a separately tiered correction. */
enum class WritingVariantKind { ORIGINAL, CORRECTED, INTERPRETED, TRANSLATED }

data class WritingProvenance(
    val authorRef: String? = null,
    val sourceRef: String? = null,
    val createdAt: String? = null
)

data class WritingVariant(
    val kind: WritingVariantKind,
    val text: String,
    val operation: String,
    val operationVersion: String,
    val outputSha256: String,
    val correctionTier: CorrectionTierLine
)

class SkribedDocument(
    originalText: String,
    private val correctionJournal: CorrectionLineageJournal,
    val provenance: WritingProvenance = WritingProvenance()
) {
    private val originalUtf8 = originalText.toByteArray(StandardCharsets.UTF_8)
    private val correctionLock = Any()

    val originalText: String = originalText
    val originalSha256: String = sha256(originalUtf8)

    fun originalBytes(): ByteArray = originalUtf8.copyOf()

    /** Read-only snapshot of the append-only correction journal. */
    fun correctionTiers(): List<CorrectionTierLine> =
        synchronized(correctionLock) { correctionJournal.readAll().toList() }

    /**
     * Every derivative operation is journaled before the variant is returned.
     * The caller must explicitly inject durable app-private storage or a test journal;
     * there is intentionally no silent in-memory default.
     */
    fun derive(
        kind: WritingVariantKind,
        text: String,
        operation: String,
        operationVersion: String,
        changeKind: CorrectionChangeKind = CorrectionChangeKind.REPLACE,
        correctionPoint: String = operation,
        basedOn: WritingVariant? = null
    ): WritingVariant {
        require(kind != WritingVariantKind.ORIGINAL) {
            "ORIGINAL is immutable; use the originalText property"
        }
        require(operation.isNotBlank()) { "operation must not be blank" }
        require(operationVersion.isNotBlank()) { "operationVersion must not be blank" }
        require(correctionPoint.isNotBlank()) { "correctionPoint must not be blank" }

        synchronized(correctionLock) {
            val knownTiers = correctionJournal.readAll()
            val parentTier = basedOn?.correctionTier
            if (parentTier != null) {
                require(knownTiers.any { it.correctionId == parentTier.correctionId }) {
                    "A correction cannot derive from a detached or foreign tier"
                }
            }

            val fromHash = basedOn?.outputSha256 ?: originalSha256
            val toHash = sha256(text.toByteArray(StandardCharsets.UTF_8))
            val tier = CorrectionTierLine(
                correctionId = UUID.randomUUID().toString(),
                originalSourceTierRef = CorrectionTierLine.ORIGINAL_SOURCE_TIER_REF,
                originalSourceTierCommit = CorrectionTierLine.ORIGINAL_SOURCE_TIER_COMMIT,
                sourceContentSha256 = fromHash,
                sourceCorrectionId = parentTier?.correctionId,
                correctionPoint = correctionPoint,
                changeKind = changeKind,
                fromSha256 = fromHash,
                toSha256 = toHash,
                operation = operation,
                operationVersion = operationVersion,
                lineageCorrectionIds = if (parentTier == null) {
                    emptyList()
                } else {
                    parentTier.lineageCorrectionIds + parentTier.correctionId
                }
            )

            // A failed append aborts the operation: no untracked derivative escapes.
            correctionJournal.append(tier)

            return WritingVariant(
                kind = kind,
                text = text,
                operation = operation,
                operationVersion = operationVersion,
                outputSha256 = toHash,
                correctionTier = tier
            )
        }
    }

    companion object {
        internal fun sha256(bytes: ByteArray): String =
            MessageDigest.getInstance("SHA-256")
                .digest(bytes)
                .joinToString("") { "%02x".format(it) }
    }
}

/** Immutable internal transmission frame; payload access always returns a copy. */
class TransmissionFrame private constructor(
    val transmissionId: String,
    val correlationId: String,
    val sourceRef: String,
    private val payloadBytes: ByteArray,
    val payloadSha256: String
) {
    fun payload(): ByteArray = payloadBytes.copyOf()

    fun hasValidIntegrity(): Boolean =
        SkribedDocument.sha256(payloadBytes) == payloadSha256

    companion object {
        fun create(
            transmissionId: String,
            correlationId: String,
            sourceRef: String,
            payload: ByteArray
        ): TransmissionFrame {
            require(transmissionId.isNotBlank()) { "transmissionId must not be blank" }
            require(correlationId.isNotBlank()) { "correlationId must not be blank" }
            require(sourceRef.isNotBlank()) { "sourceRef must not be blank" }
            val stablePayload = payload.copyOf()
            return TransmissionFrame(
                transmissionId = transmissionId,
                correlationId = correlationId,
                sourceRef = sourceRef,
                payloadBytes = stablePayload,
                payloadSha256 = SkribedDocument.sha256(stablePayload)
            )
        }
    }
}

data class TransmissionReceipt(
    val transmissionId: String,
    val correlationId: String,
    val sourceRef: String,
    val requestSha256: String,
    val responseSha256: String,
    val responsePayload: ByteArray
)

/** A local endpoint; implementations must not silently dispatch to a network or device. */
fun interface InternalTransmissionEndpoint {
    fun receive(frame: TransmissionFrame): ByteArray
}

interface TransmissionTransceiver {
    fun transceive(
        frame: TransmissionFrame,
        endpoint: InternalTransmissionEndpoint
    ): TransmissionReceipt
}

/** In-process closed-loop transceiver; no network, hardware, or automatic playback. */
class InMemoryTransmissionTransceiver : TransmissionTransceiver {
    override fun transceive(
        frame: TransmissionFrame,
        endpoint: InternalTransmissionEndpoint
    ): TransmissionReceipt {
        require(frame.hasValidIntegrity()) { "Transmission integrity check failed" }
        val delivered = TransmissionFrame.create(
            transmissionId = frame.transmissionId,
            correlationId = frame.correlationId,
            sourceRef = frame.sourceRef,
            payload = frame.payload()
        )
        val response = endpoint.receive(delivered).copyOf()
        return TransmissionReceipt(
            transmissionId = frame.transmissionId,
            correlationId = frame.correlationId,
            sourceRef = frame.sourceRef,
            requestSha256 = frame.payloadSha256,
            responseSha256 = SkribedDocument.sha256(response),
            responsePayload = response
        )
    }
}
