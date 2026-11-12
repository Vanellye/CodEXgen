package com.vanellye.eria.pantheon
enum class PlayerPlaybackState { PLAYING, PAUSED, STOPPED, BUFFERING, UNKNOWN }
enum class PlayerControlIntent { REQUEST_PAUSE, REQUEST_RESUME }
data class PlayerObservation(
    val packageName: String, val sessionRef: String?, val playbackState: PlayerPlaybackState,
    val observedAt: String, val metadataRef: String? = null
)
/** Observation-only adapter for players exposing an authorized media session. */
interface InstalledPlayerAdapter { fun observe(): PlayerObservation? }
data class PlayerControlProposal(
    val proposalId: String, val threadId: String, val targetPackage: String,
    val targetSessionRef: String?, val intent: PlayerControlIntent, val requestedAt: String,
    val approvalScope: String, val executionEnabled: Boolean = false
)
/** Creates a reviewable proposal only; it never sends a command to the installed player. */
object PlayerControlProposalFactory {
    fun create(
        proposalId: String, thread: SuspensionThread, observation: PlayerObservation,
        intent: PlayerControlIntent, requestedAt: String
    ): PlayerControlProposal {
        require(thread.status != SuspensionStatus.CLOSED) { "closed thread cannot create proposals" }
        require(proposalId.isNotBlank() && observation.packageName.isNotBlank()) { "proposal and player identity are required" }
        require(requestedAt.isNotBlank()) { "requestedAt is required" }
        return PlayerControlProposal(
            proposalId, thread.threadId, observation.packageName, observation.sessionRef,
            intent, requestedAt, "player." + intent.name.lowercase() + ":" + observation.packageName, false
        )
    }
}
