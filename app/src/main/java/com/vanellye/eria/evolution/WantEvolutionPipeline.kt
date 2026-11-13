package com.vanellye.eria.evolution

/**
 * Local orchestration contracts for WANT-driven ERIA evolution.
 *
 * Engine ports are deliberately provider-neutral. Implementations must keep
 * proposal generation side-effect free; Stride execution is the only mutating
 * boundary and always requires an exact, unexpired HumanApproval.
 */

data class Want(
    val id: String,
    val statement: String,
    val rationale: String,
    val repository: String,
    val branch: String,
    val acceptanceCriteria: List<String>,
    val allowedPaths: Set<String>,
    val excludedPaths: Set<String> = emptySet()
) {
    init {
        require(id.isNotBlank())
        require(statement.isNotBlank())
        require(repository.isNotBlank())
        require(branch.isNotBlank())
        require(acceptanceCriteria.isNotEmpty())
        require(allowedPaths.isNotEmpty())
        require(allowedPaths.none { it.startsWith("/") || it.split("/").contains("..") })
        require(excludedPaths.none { it.startsWith("/") || it.split("/").contains("..") })
    }
}

data class MiniPrompt(
    val id: String,
    val wantId: String,
    val objective: String,
    val repository: String,
    val branch: String,
    val allowedPaths: Set<String>,
    val excludedPaths: Set<String>,
    val acceptanceCriterion: String
)

class MiniPromptDriver {
    fun decompose(want: Want): List<MiniPrompt> = want.acceptanceCriteria.mapIndexed { index, criterion ->
        MiniPrompt(
            id = "${want.id}:step:${index + 1}",
            wantId = want.id,
            objective = "Implement and verify: $criterion",
            repository = want.repository,
            branch = want.branch,
            allowedPaths = want.allowedPaths,
            excludedPaths = want.excludedPaths,
            acceptanceCriterion = criterion
        )
    }
}

data class PlatformScaffoldProposal(
    val proposalId: String,
    val promptId: String,
    val manifestId: String,
    val summary: String
)

data class ChangeCandidate(
    val candidateId: String,
    val promptId: String,
    val repository: String,
    val branch: String,
    val changedPaths: Set<String>,
    val digest: String,
    val summary: String
)

data class PolicyContext(
    val wantId: String,
    val promptId: String,
    val repository: String,
    val branch: String,
    val changedPaths: Set<String>
)

data class PolicyVerdict(
    val allowed: Boolean,
    val reasons: List<String> = emptyList()
)

data class HumanApproval(
    val approvalId: String,
    val approvedBy: String,
    val wantId: String,
    val promptId: String,
    val repository: String,
    val branch: String,
    val candidateDigest: String,
    val approvedPaths: Set<String>,
    val approvedOperation: String,
    val expiresAtEpochMillis: Long
)

data class ExecutionReceipt(
    val executionId: String,
    val candidateDigest: String,
    val changedPaths: Set<String>,
    val checksPassed: Boolean,
    val evidenceReferences: List<String>
)

data class RewardEvent(
    val eventId: String,
    val wantId: String,
    val promptId: String,
    val executionId: String,
    val points: Int,
    val evidenceReferences: List<String>
)

sealed interface EvolutionResult {
    data class Prepared(
        val prompt: MiniPrompt,
        val scaffold: PlatformScaffoldProposal,
        val candidate: ChangeCandidate
    ) : EvolutionResult

    data class Blocked(val reasons: List<String>) : EvolutionResult

    data class Executed(
        val receipt: ExecutionReceipt,
        val reward: RewardEvent?
    ) : EvolutionResult
}

interface GenesisEngine {
    /** Must only return a proposal; must not write files or dispatch externally. */
    fun propose(prompt: MiniPrompt): PlatformScaffoldProposal
}

interface ForgeEngine {
    /** Must produce a reviewable candidate; must not commit, push, or deploy. */
    fun prepare(
        prompt: MiniPrompt,
        scaffold: PlatformScaffoldProposal
    ): ChangeCandidate
}

interface PantheonEngine {
    /** Policy evaluation is read-only and returns explicit reasons on denial. */
    fun evaluate(candidate: ChangeCandidate, context: PolicyContext): PolicyVerdict
}

interface StrideEngine {
    /** The sole mutating boundary. Implementations must enforce approval again. */
    fun execute(candidate: ChangeCandidate, approval: HumanApproval): ExecutionReceipt
}

interface EvolutionVerifier {
    fun verify(
        prompt: MiniPrompt,
        candidate: ChangeCandidate,
        receipt: ExecutionReceipt
    ): List<String>
}

interface RewardLedger {
    /** Must be idempotent by eventId and append-only. */
    fun appendOnce(event: RewardEvent): Boolean
}

class InMemoryRewardLedger : RewardLedger {
    private val events = linkedMapOf<String, RewardEvent>()

    @Synchronized
    override fun appendOnce(event: RewardEvent): Boolean {
        require(event.points > 0)
        if (events.containsKey(event.eventId)) return false
        events[event.eventId] = event
        return true
    }

    @Synchronized
    fun snapshot(): List<RewardEvent> = events.values.toList()
}

class WantEngine(
    private val promptDriver: MiniPromptDriver,
    private val genesis: GenesisEngine,
    private val forge: ForgeEngine,
    private val pantheon: PantheonEngine,
    private val stride: StrideEngine,
    private val verifier: EvolutionVerifier,
    private val rewards: RewardLedger,
    private val nowEpochMillis: () -> Long = System::currentTimeMillis
) {
    /**
     * Generates proposals only. No source files are written and no engine is executed.
     */
    fun prepare(want: Want): List<EvolutionResult> =
        promptDriver.decompose(want).map { prompt ->
            runCatching {
                val scaffold = genesis.propose(prompt)
                require(scaffold.promptId == prompt.id) {
                    "GENESIS returned a proposal for a different prompt."
                }
                val candidate = forge.prepare(prompt, scaffold)
                validateCandidate(prompt, candidate)
                val context = PolicyContext(
                    want.id, prompt.id, want.repository, want.branch, candidate.changedPaths
                )
                val verdict = pantheon.evaluate(candidate, context)
                if (!verdict.allowed) {
                    EvolutionResult.Blocked(
                        verdict.reasons.ifEmpty { listOf("PANTHEON policy review denied this candidate.") }
                    )
                } else {
                    EvolutionResult.Prepared(prompt, scaffold, candidate)
                }
            }.getOrElse {
                EvolutionResult.Blocked(listOf(it.message ?: "Proposal preparation failed."))
            }
        }

    /**
     * Executes one prepared candidate only after exact human approval.
     * Any mismatch, expiry, policy denial, or failed verification blocks rewards.
     */
    fun execute(
        prepared: EvolutionResult.Prepared,
        approval: HumanApproval
    ): EvolutionResult {
        val prompt = prepared.prompt
        val candidate = prepared.candidate

        val approvalProblems = validateApproval(prepared, approval)
        if (approvalProblems.isNotEmpty()) return EvolutionResult.Blocked(approvalProblems)

        val context = PolicyContext(
            prompt.wantId, prompt.id, candidate.repository, candidate.branch, candidate.changedPaths
        )
        val verdict = pantheon.evaluate(candidate, context)
        if (!verdict.allowed) {
            return EvolutionResult.Blocked(
                verdict.reasons.ifEmpty { listOf("PANTHEON denied execution.") }
            )
        }

        val receipt = runCatching { stride.execute(candidate, approval) }
            .getOrElse {
                return EvolutionResult.Blocked(
                    listOf(it.message ?: "STRIDE execution failed; no reward was issued.")
                )
            }

        if (receipt.candidateDigest != candidate.digest ||
            receipt.changedPaths != candidate.changedPaths
        ) {
            return EvolutionResult.Blocked(
                listOf("Execution receipt does not match the approved candidate; reward withheld.")
            )
        }

        val verificationProblems = verifier.verify(prompt, candidate, receipt)
        if (!receipt.checksPassed || verificationProblems.isNotEmpty() ||
            receipt.evidenceReferences.isEmpty()
        ) {
            return EvolutionResult.Blocked(
                verificationProblems.ifEmpty {
                    listOf("Required checks or evidence are missing; reward withheld.")
                }
            )
        }

        val reward = RewardEvent(
            eventId = "verified:${receipt.executionId}",
            wantId = prompt.wantId,
            promptId = prompt.id,
            executionId = receipt.executionId,
            points = 3,
            evidenceReferences = receipt.evidenceReferences
        )
        val recorded = rewards.appendOnce(reward)
        return EvolutionResult.Executed(receipt, reward.takeIf { recorded })
    }

    private fun validateCandidate(prompt: MiniPrompt, candidate: ChangeCandidate) {
        require(candidate.promptId == prompt.id) {
            "FORGE returned a candidate for a different prompt."
        }
        require(candidate.repository == prompt.repository && candidate.branch == prompt.branch) {
            "FORGE changed the repository or branch outside the WANT scope."
        }
        require(candidate.digest.isNotBlank()) { "Candidate digest is required." }
        require(candidate.changedPaths.isNotEmpty()) { "Candidate must identify changed paths." }
        require(candidate.changedPaths.all { path ->
            !path.startsWith("/") && !path.split("/").contains("..") &&
                path in prompt.allowedPaths && path !in prompt.excludedPaths
        }) { "Candidate contains paths outside the approved WANT scope." }
    }

    private fun validateApproval(
        prepared: EvolutionResult.Prepared,
        approval: HumanApproval
    ): List<String> {
        val prompt = prepared.prompt
        val candidate = prepared.candidate
        val problems = mutableListOf<String>()
        if (approval.approvalId.isBlank() || approval.approvedBy.isBlank()) {
            problems += "A recorded human approval identity is required."
        }
        if (approval.wantId != prompt.wantId || approval.promptId != prompt.id) {
            problems += "Approval does not identify this WANT and mini-prompt."
        }
        if (approval.repository != candidate.repository || approval.branch != candidate.branch) {
            problems += "Approval repository or branch does not match the candidate."
        }
        if (approval.candidateDigest != candidate.digest) {
            problems += "Approval digest does not match the exact candidate."
        }
        if (approval.approvedPaths != candidate.changedPaths) {
            problems += "Approval paths must exactly match the candidate paths."
        }
        if (approval.approvedOperation != "apply-candidate") {
            problems += "Approval does not authorize the apply-candidate operation."
        }
        if (approval.expiresAtEpochMillis <= nowEpochMillis()) {
            problems += "Human approval is expired."
        }
        return problems
    }
}
