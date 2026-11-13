package com.vanellye.eria.evolution

import org.junit.Assert.*
import org.junit.Test

class WantEngineTest {
    private val want = Want(
        id = "want-1",
        statement = "Create a platform scaffold",
        rationale = "Enable reusable platform creation",
        repository = "Vanellye/CodEXgen",
        branch = "integration/wantever-propagation",
        acceptanceCriteria = listOf("manifest is validated"),
        allowedPaths = setOf("platform/manifest.json")
    )

    private class FakeGenesis : GenesisEngine {
        override fun propose(prompt: MiniPrompt) =
            PlatformScaffoldProposal("scaffold-1", prompt.id, "platform-1", "Proposed scaffold")
    }

    private class FakeForge(
        private val paths: Set<String> = setOf("platform/manifest.json")
    ) : ForgeEngine {
        override fun prepare(prompt: MiniPrompt, scaffold: PlatformScaffoldProposal) =
            ChangeCandidate(
                "candidate-1", prompt.id, prompt.repository, prompt.branch,
                paths, "sha256:abc123", "Candidate change"
            )
    }

    private class FakePantheon(private val allowed: Boolean = true) : PantheonEngine {
        var evaluations = 0
        override fun evaluate(candidate: ChangeCandidate, context: PolicyContext): PolicyVerdict {
            evaluations++
            return PolicyVerdict(allowed, if (allowed) emptyList() else listOf("Policy denied"))
        }
    }

    private class FakeStride : StrideEngine {
        var executions = 0
        override fun execute(candidate: ChangeCandidate, approval: HumanApproval): ExecutionReceipt {
            executions++
            return ExecutionReceipt(
                "exec-1", candidate.digest, candidate.changedPaths, true,
                listOf("test://unit/manifest-validation")
            )
        }
    }

    private class FakeApprovalGate : HumanApprovalGate {
        private val consumed = mutableSetOf<String>()
        override fun validateAndConsume(approval: HumanApproval): List<String> {
            if (!consumed.add(approval.approvalId)) return listOf("Approval has already been used.")
            return emptyList()
        }
    }

    private class FakeVerifier : EvolutionVerifier {
        override fun verify(
            prompt: MiniPrompt,
            candidate: ChangeCandidate,
            receipt: ExecutionReceipt
        ) = emptyList<String>()
    }

    private fun approval(prepared: EvolutionResult.Prepared, expiry: Long = 20_000L) =
        HumanApproval(
            approvalId = "approval-1",
            approvedBy = "reviewer-1",
            wantId = prepared.prompt.wantId,
            promptId = prepared.prompt.id,
            repository = prepared.candidate.repository,
            branch = prepared.candidate.branch,
            candidateDigest = prepared.candidate.digest,
            approvedPaths = prepared.candidate.changedPaths,
            approvedOperation = "apply-candidate",
            expiresAtEpochMillis = expiry
        )

    @Test fun prepareIsProposalOnlyAndDecomposesOnePromptPerCriterion() {
        val stride = FakeStride()
        val engine = engine(stride = stride)
        val results = engine.prepare(want.copy(acceptanceCriteria = listOf("a", "b")))
        assertEquals(2, results.size)
        assertTrue(results.all { it is EvolutionResult.Prepared })
        assertEquals(0, stride.executions)
    }

    @Test fun executionWithoutApprovalIsImpossibleThroughPublicApi() {
        val stride = FakeStride()
        val engine = engine(stride = stride)
        val prepared = engine.prepare(want).single() as EvolutionResult.Prepared
        val invalid = approval(prepared).copy(candidateDigest = "sha256:wrong")
        assertTrue(engine.execute(prepared, invalid) is EvolutionResult.Blocked)
        assertEquals(0, stride.executions)
    }

    @Test fun pantheonDenialBlocksExecution() {
        val stride = FakeStride()
        val engine = engine(stride = stride, pantheon = FakePantheon(false))
        val result = engine.prepare(want).single()
        assertTrue(result is EvolutionResult.Blocked)
        assertEquals(0, stride.executions)
    }

    @Test fun outOfScopeForgePathsAreRejected() {
        val engine = engine(forge = FakeForge(setOf("../outside.txt")))
        val result = engine.prepare(want).single()
        assertTrue(result is EvolutionResult.Blocked)
    }

    @Test fun verifiedExecutionAwardsRewardOnce() {
        val ledger = InMemoryRewardLedger()
        val engine = engine(rewards = ledger)
        val prepared = engine.prepare(want).single() as EvolutionResult.Prepared
        val result = engine.execute(prepared, approval(prepared))
        assertTrue(result is EvolutionResult.Executed)
        assertEquals(1, ledger.snapshot().size)
        val repeated = engine.execute(prepared, approval(prepared))
        assertTrue(repeated is EvolutionResult.Blocked)
        assertEquals(1, ledger.snapshot().size)
    }

    @Test fun expiredApprovalBlocksExecution() {
        val stride = FakeStride()
        val engine = engine(stride = stride, now = { 30_000L })
        val prepared = engine.prepare(want).single() as EvolutionResult.Prepared
        assertTrue(engine.execute(prepared, approval(prepared, 20_000L)) is EvolutionResult.Blocked)
        assertEquals(0, stride.executions)
    }

    private fun engine(
        stride: FakeStride = FakeStride(),
        pantheon: FakePantheon = FakePantheon(),
        forge: FakeForge = FakeForge(),
        rewards: InMemoryRewardLedger = InMemoryRewardLedger(),
        now: () -> Long = { 10_000L }
    ) = WantEngine(
        MiniPromptDriver(), FakeGenesis(), forge, pantheon, stride,
        FakeVerifier(), rewards, FakeApprovalGate(), now
    )
}
