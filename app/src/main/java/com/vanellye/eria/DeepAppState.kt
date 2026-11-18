package com.vanellye.eria

/**
 * Canonical, immutable application state for long-running ERIA workplay flows.
 * This is a reducer model: it records state transitions but performs no I/O.
 */
data class DeepAppState(
    val runId: String? = null,
    val phase: Phase = Phase.IDLE,
    val title: String = "",
    val completedSteps: Int = 0,
    val totalSteps: Int = 0,
    val message: String? = null,
    val revision: Long = 0L
) {
    enum class Phase { IDLE, READY, RUNNING, REVIEW, BLOCKED, FAILED, COMPLETE }

    init {
        require(completedSteps >= 0) { "completedSteps cannot be negative" }
        require(totalSteps >= 0) { "totalSteps cannot be negative" }
        require(completedSteps <= totalSteps || totalSteps == 0) {
            "completedSteps cannot exceed totalSteps"
        }
        require(revision >= 0L) { "revision cannot be negative" }
    }

    val progress: Float
        get() = if (totalSteps == 0) 0f else completedSteps.toFloat() / totalSteps

    fun reduce(event: Event): DeepAppState = when (event) {
        is Event.Begin -> copy(
            runId = event.runId,
            phase = Phase.READY,
            title = event.title.trim(),
            completedSteps = 0,
            totalSteps = event.totalSteps,
            message = null,
            revision = revision + 1
        )
        is Event.Start -> if (matches(event.runId) && phase == Phase.READY) {
            copy(phase = Phase.RUNNING, revision = revision + 1)
        } else this
        is Event.StepCompleted -> if (
            matches(event.runId) && phase == Phase.RUNNING &&
            completedSteps < totalSteps
        ) copy(completedSteps = completedSteps + 1, revision = revision + 1) else this
        is Event.RequestReview -> if (matches(event.runId) && phase == Phase.RUNNING) {
            copy(phase = Phase.REVIEW, message = event.message, revision = revision + 1)
        } else this
        is Event.Block -> if (matches(event.runId) && phase != Phase.COMPLETE) {
            copy(phase = Phase.BLOCKED, message = event.reason, revision = revision + 1)
        } else this
        is Event.Fail -> if (matches(event.runId) && phase != Phase.COMPLETE) {
            copy(phase = Phase.FAILED, message = event.reason, revision = revision + 1)
        } else this
        is Event.Complete -> if (
            matches(event.runId) && phase == Phase.REVIEW &&
            completedSteps == totalSteps
        ) copy(phase = Phase.COMPLETE, message = event.summary, revision = revision + 1)
        else this
        is Event.Reset -> DeepAppState(revision = revision + 1)
    }

    private fun matches(candidate: String): Boolean = runId != null && runId == candidate

    sealed interface Event {
        data class Begin(val runId: String, val title: String, val totalSteps: Int) : Event {
            init {
                require(runId.isNotBlank())
                require(title.isNotBlank())
                require(totalSteps >= 0)
            }
        }
        data class Start(val runId: String) : Event
        data class StepCompleted(val runId: String) : Event
        data class RequestReview(val runId: String, val message: String? = null) : Event
        data class Block(val runId: String, val reason: String) : Event
        data class Fail(val runId: String, val reason: String) : Event
        data class Complete(val runId: String, val summary: String? = null) : Event
        data object Reset : Event
    }
}
