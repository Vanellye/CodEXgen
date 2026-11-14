package com.vanellye.eria.pons

enum class PonsEffectiveState { READY, DEGRADED, HOLD, UNKNOWN }

data class PonsComponentStatus(
    val componentId: String,
    val operationalState: PonsOperationalState,
    val provenance: PonsProvenanceResult,
    val effectiveState: PonsEffectiveState,
    val anchor: PonsAnchorIdentity
)

/** Combines component-reported health with PONS-computed source provenance. */
class PonsStatusRegistry(private val provenanceGate: PonsProvenanceGate) {
    fun inspect(
        componentId: String,
        operationalState: PonsOperationalState,
        sourceBytes: ByteArray?
    ): PonsComponentStatus {
        val provenance = provenanceGate.verify(componentId, sourceBytes)
        val effective = when {
            provenance.state == PonsProvenanceState.HOLD -> PonsEffectiveState.HOLD
            provenance.state != PonsProvenanceState.VERIFIED -> PonsEffectiveState.UNKNOWN
            operationalState == PonsOperationalState.HOLD -> PonsEffectiveState.HOLD
            operationalState == PonsOperationalState.DEGRADED -> PonsEffectiveState.DEGRADED
            operationalState == PonsOperationalState.READY -> PonsEffectiveState.READY
            else -> PonsEffectiveState.UNKNOWN
        }
        return PonsComponentStatus(
            componentId = componentId,
            operationalState = operationalState,
            provenance = provenance,
            effectiveState = effective,
            anchor = provenanceGate.anchor
        )
    }
}
