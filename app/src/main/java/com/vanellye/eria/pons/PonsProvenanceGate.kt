package com.vanellye.eria.pons

import java.security.MessageDigest

/** Immutable canonical identity pinned by the PONS integration. */
data class PonsAnchorIdentity(
    val anchorId: String,
    val branch: String,
    val refSha: String
) {
    companion object {
        val CANONICAL = PonsAnchorIdentity(
            anchorId = "7f7a43a973a96a06dd432bf94843213d09133323",
            branch = "zero-dissipation-anchor",
            refSha = "df5ead3b55cfabd0ba40e902b4080946cba794dc"
        )
    }
}

enum class PonsProvenanceState { VERIFIED, HOLD, UNKNOWN }
enum class PonsOperationalState { READY, DEGRADED, HOLD, UNKNOWN }

data class PonsComponentPin(
    val componentId: String,
    val sourceRef: String,
    val sourcePath: String,
    val sha256: String
)

data class PonsProvenanceResult(
    val componentId: String,
    val state: PonsProvenanceState,
    val expectedSha256: String?,
    val actualSha256: String?,
    val reason: String,
    val anchor: PonsAnchorIdentity
)

/**
 * Android-side PONS verifier.
 *
 * Pins must be loaded from a separately reviewed trust manifest. This class
 * computes source digests itself and never accepts a component's accuracy claim.
 */
class PonsProvenanceGate(
    pins: Map<String, PonsComponentPin>,
    val anchor: PonsAnchorIdentity = PonsAnchorIdentity.CANONICAL
) {
    // Defensive snapshot: callers cannot mutate trust pins after gate construction.
    private val pins: Map<String, PonsComponentPin> = pins.toMap()

    init {
        require(anchor == PonsAnchorIdentity.CANONICAL) {
            "PONS canonical anchor mismatch; refusing initialization"
        }
        pins.forEach { (key, pin) ->
            require(key == pin.componentId) { "PONS manifest key/component mismatch" }
            require(pin.sha256.matches(Regex("^[0-9a-f]{64}$"))) {
                "PONS pin must be lowercase SHA-256"
            }
            require(pin.sourceRef.isNotBlank() && pin.sourcePath.isNotBlank()) {
                "PONS source identity is incomplete"
            }
        }
    }

    fun verify(componentId: String, sourceBytes: ByteArray?): PonsProvenanceResult {
        val pin = pins[componentId]
            ?: return PonsProvenanceResult(
                componentId, PonsProvenanceState.UNKNOWN, null, null,
                "component has no independently pinned manifest entry", anchor
            )
        if (sourceBytes == null) {
            return PonsProvenanceResult(
                componentId, PonsProvenanceState.UNKNOWN, pin.sha256, null,
                "source bytes unavailable", anchor
            )
        }
        val actual = sha256(sourceBytes)
        val matches = actual == pin.sha256
        return PonsProvenanceResult(
            componentId,
            if (matches) PonsProvenanceState.VERIFIED else PonsProvenanceState.HOLD,
            pin.sha256,
            actual,
            if (matches) "source digest matches pinned manifest" else "source digest mismatch",
            anchor
        )
    }

    companion object {
        fun sha256(bytes: ByteArray): String =
            MessageDigest.getInstance("SHA-256").digest(bytes)
                .joinToString("") { "%02x".format(it) }
    }
}
