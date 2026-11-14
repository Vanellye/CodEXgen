package com.vanellye.eria.contracts

import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import com.vanellye.eria.pons.PonsComponentStatus
import com.vanellye.eria.pons.PonsAnchorIdentity
import com.vanellye.eria.pons.requireReady
import com.vanellye.eria.pons.PonsEffectiveState
import com.vanellye.eria.pons.PonsAnchorIdentity

/**
 * SKRIBED writing contract.
 *
 * The original text is retained byte-for-byte as UTF-8. No Unicode normalization,
 * spelling correction, transliteration, or formatting rewrite is performed here.
 * Any edited form is a separately labelled derivative.
 */
enum class WritingVariantKind {
    ORIGINAL,
    CORRECTED,
    INTERPRETED,
    TRANSLATED
}

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
    val outputSha256: String
)

class SkribedDocument(
    originalText: String,
    val provenance: WritingProvenance = WritingProvenance()
) {
    private val originalUtf8: ByteArray = originalText.toByteArray(StandardCharsets.UTF_8)

    /** Returns the exact original string; derived variants never replace it. */
    val originalText: String = originalText

    val originalSha256: String = sha256(originalUtf8)

    /** Returns a defensive copy of the original UTF-8 bytes. */
    fun originalBytes(): ByteArray = originalUtf8.copyOf()

    fun derive(
        kind: WritingVariantKind,
        text: String,
        operation: String,
        operationVersion: String
    ): WritingVariant {
        require(kind != WritingVariantKind.ORIGINAL) {
            "ORIGINAL is immutable; use the originalText property"
        }
        require(operation.isNotBlank()) { "operation must not be blank" }
        require(operationVersion.isNotBlank()) { "operationVersion must not be blank" }
        return WritingVariant(
            kind = kind,
            text = text,
            operation = operation,
            operationVersion = operationVersion,
            outputSha256 = sha256(text.toByteArray(StandardCharsets.UTF_8))
        )
    }

    companion object {
        internal fun sha256(bytes: ByteArray): String =
            MessageDigest.getInstance("SHA-256")
                .digest(bytes)
                .joinToString("") { "%02x".format(it) }
    }
}

/**
 * An immutable internal transmission frame. Payload access always returns a copy.
 * The digest covers the exact bytes and is checked before endpoint delivery.
 */
class TransmissionFrame private constructor(
    val transmissionId: String,
    val correlationId: String,
    val sourceRef: String,
    private val payloadBytes: ByteArray,
    val payloadSha256: String,
    val anchor: PonsAnchorIdentity
) {
    fun payload(): ByteArray = payloadBytes.copyOf()

    fun hasValidIntegrity(): Boolean =
        SkribedDocument.sha256(payloadBytes) == payloadSha256

    companion object {
        fun create(
            transmissionId: String,
            correlationId: String,
            sourceRef: String,
            payload: ByteArray,
            anchor: PonsAnchorIdentity = PonsAnchorIdentity.CANONICAL
        ): TransmissionFrame {
            require(transmissionId.isNotBlank()) { "transmissionId must not be blank" }
            require(correlationId.isNotBlank()) { "correlationId must not be blank" }
            require(sourceRef.isNotBlank()) { "sourceRef must not be blank" }
            require(anchor == PonsAnchorIdentity.CANONICAL) { "Transmission anchor mismatch" }
            val stablePayload = payload.copyOf()
            return TransmissionFrame(
                transmissionId = transmissionId,
                correlationId = correlationId,
                sourceRef = sourceRef,
                payloadBytes = stablePayload,
                payloadSha256 = SkribedDocument.sha256(stablePayload),
                anchor = anchor
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
    val responsePayload: ByteArray,
    val anchor: PonsAnchorIdentity,
    val evidenceId: String,
    val supersedesEvidenceId: String?
)

/** Immutable evidence event. New observations supersede, but never erase, earlier events. */
data class TransmissionEvidence(
    val evidenceId: String,
    val transmissionId: String,
    val anchor: PonsAnchorIdentity,
    val requestSha256: String,
    val responseSha256: String,
    val supersedesEvidenceId: String?
)

/** In-memory append-only evidence history; production must persist and authenticate checkpoints. */
class TransmissionEvidenceLedger {
    private val events = mutableListOf<TransmissionEvidence>()

    @Synchronized
    fun append(
        transmissionId: String,
        anchor: PonsAnchorIdentity,
        requestSha256: String,
        responseSha256: String
    ): TransmissionEvidence {
        require(transmissionId.isNotBlank())
        require(anchor == PonsAnchorIdentity.CANONICAL) { "Evidence anchor mismatch" }
        val previous = events.lastOrNull { it.transmissionId == transmissionId }
        val canonical = listOf(
            transmissionId, anchor.anchorId, anchor.branch, anchor.refSha,
            requestSha256, responseSha256, previous?.evidenceId.orEmpty()
        ).joinToString("|")
        val event = TransmissionEvidence(
            evidenceId = SkribedDocument.sha256(canonical.toByteArray(StandardCharsets.UTF_8)),
            transmissionId = transmissionId,
            anchor = anchor,
            requestSha256 = requestSha256,
            responseSha256 = responseSha256,
            supersedesEvidenceId = previous?.evidenceId
        )
        events.add(event)
        return event
    }

    @Synchronized
    fun history(transmissionId: String): List<TransmissionEvidence> =
        events.filter { it.transmissionId == transmissionId }.toList()
}

/** A local endpoint. Implementations must not silently dispatch to a network or device. */
fun interface InternalTransmissionEndpoint {
    fun receive(frame: TransmissionFrame): ByteArray
}

interface TransmissionTransceiver {
    fun transceive(
        frame: TransmissionFrame,
        endpoint: InternalTransmissionEndpoint
    ): TransmissionReceipt
}

/**
 * In-process, closed-loop transceiver. No sockets, webhooks, media players, hardware
 * actuators, or external destinations are available through this implementation.
 */
class InMemoryTransmissionTransceiver(
    private val ponsStatus: PonsComponentStatus,
    private val evidenceLedger: TransmissionEvidenceLedger = TransmissionEvidenceLedger()
) : TransmissionTransceiver {
    init {
        ponsStatus.requireReady("audio.internal-transceiver")
    }

    override fun transceive(
        frame: TransmissionFrame,
        endpoint: InternalTransmissionEndpoint
    ): TransmissionReceipt {
        require(frame.hasValidIntegrity()) { "Transmission integrity check failed" }

        // Reconstruct the frame so the endpoint receives a defensive payload copy.
        val delivered = TransmissionFrame.create(
            transmissionId = frame.transmissionId,
            correlationId = frame.correlationId,
            sourceRef = frame.sourceRef,
            payload = frame.payload(),
            anchor = frame.anchor
        )
        val response = endpoint.receive(delivered).copyOf()

        val evidence = evidenceLedger.append(
            transmissionId = frame.transmissionId,
            anchor = frame.anchor,
            requestSha256 = frame.payloadSha256,
            responseSha256 = SkribedDocument.sha256(response)
        )
        return TransmissionReceipt(
            transmissionId = frame.transmissionId,
            correlationId = frame.correlationId,
            sourceRef = frame.sourceRef,
            requestSha256 = frame.payloadSha256,
            responseSha256 = SkribedDocument.sha256(response),
            responsePayload = response,
            anchor = evidence.anchor,
            evidenceId = evidence.evidenceId,
            supersedesEvidenceId = evidence.supersedesEvidenceId
        )
    }
}
