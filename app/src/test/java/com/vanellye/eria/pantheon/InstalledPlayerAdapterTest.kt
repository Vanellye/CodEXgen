package com.vanellye.eria.pantheon
import org.junit.Assert.*
import org.junit.Test
class InstalledPlayerAdapterTest {
    @Test fun proposalIsBoundToObservedPlayerAndCannotExecute() {
        val thread = SuspensionThread.fromTransmission(
            "thread-player",
            TransmissionOrigin("tx-player", "local.capture", "2026-11-12T10:00:00Z", "b".repeat(64)),
            SuspensionEvent("event-create", SuspensionEventType.THREAD_CREATED, "2026-11-12T10:00:00Z", "operator", "created")
        )
        val observed = PlayerObservation("example.media.player", "session-9", PlayerPlaybackState.PLAYING, "2026-11-12T10:00:01Z")
        val proposal = PlayerControlProposalFactory.create("proposal-1", thread, observed, PlayerControlIntent.REQUEST_PAUSE, "2026-11-12T10:00:02Z")
        assertEquals("example.media.player", proposal.targetPackage)
        assertEquals("session-9", proposal.targetSessionRef)
        assertEquals("player.request_pause:example.media.player", proposal.approvalScope)
        assertFalse(proposal.executionEnabled)
    }
}
