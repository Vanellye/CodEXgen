package com.vanellye.eria.contracts

import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.util.UUID

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

    fun correctionTiers(): List<CorrectionTierLine> =
        synchronized(correctionLock) { correctionJournal.readAll().toList() }

    /**
     * Records a forward or reverse correction as a new append-only tier.
     * REVERSE requires output bytes that exactly match the source hash of basedOn;
     * no inverse is guessed, synthesized, or silently applied.
     */
    fun derive(
        kind: WritingVariantKind,
        text: String,
        operation: String,
        operationVersion: String,
        changeKind: CorrectionChangeKind = CorrectionChangeKind.REPLACE,
        correctionPoint: String = operation,
        basedOn: WritingVariant? = null,
        direction: CorrectionDirection = CorrectionDirection.FORWARD
    ): WritingVariant {
        require(kind != WritingVariantKind.ORIGINAL) {
            "ORIGINAL is immutable; use the originalText property"
        }
        require(operation.isNotBlank()) { "operation must not be blank" }
        require(operationVersion.isNotBlank()) { "operationVersion must not be blank" }
        require(correctionPoint.isNotBlank()) { "correctionPoint must not be blank" }
        require(direction != CorrectionDirection.REVERSE || basedOn != null) {
            "A reverse correction requires the exact prior variant"
        }

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
            if (direction == CorrectionDirection.REVERSE) {
                require(toHash == parentTier!!.fromSha256) {
                    "Reverse correction output must exactly match the prior tier's from hash"
                }
            }

            val tier = CorrectionTierLine(
                correctionId = UUID.randomUUID().toString(),
                originalSourceTierRef = CorrectionTierLine.ORIGINAL_SOURCE_TIER_REF,
                originalSourceTierCommit = CorrectionTierLine.ORIGINAL_SOURCE_TIER_COMMIT,
                futureMarkerAnchorCommit = CorrectionTierLine.FUTURE_MARKER_ANCHOR_COMMIT,
                sourceContentSha256 = fromHash,
                sourceCorrectionId = parentTier?.correctionId,
                correctionPoint = correctionPoint,
                changeKind = changeKind,
                direction = direction,
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

    /** Explicit to → from operation; the caller supplies the exact target text. */
    fun reverseTo(
        prior: WritingVariant,
        targetText: String,
        operationVersion: String,
        correctionPoint: String = "correction.reverse"
    ): WritingVariant = derive(
        kind = WritingVariantKind.CORRECTED,
        text = targetText,
        operation = "reverse:" + prior.operation,
        operationVersion = operationVersion,
        changeKind = prior.correctionTier.changeKind,
        correctionPoint = correctionPoint,
        basedOn = prior,
        direction = CorrectionDirection.REVERSE
    )

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

fun interface InternalTransmissionEndpoint {
    fun receive(frame: TransmissionFrame): ByteArray
}

interface TransmissionTransceiver {
    fun transceive(
        frame: TransmissionFrame,
        endpoint: InternalTransmissionEndpoint
    ): TransmissionReceipt
}

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
