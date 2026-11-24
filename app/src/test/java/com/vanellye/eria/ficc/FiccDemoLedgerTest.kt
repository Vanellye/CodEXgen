package com.vanellye.eria.ficc

import java.math.BigDecimal
import java.time.Instant
import org.junit.Assert.*
import org.junit.Test

class FiccDemoLedgerTest {
    private fun fixture() = DemoLedgerFactory.create()
    private fun identity(id: String) = DemoIdentityDirectory.find(id)!!

    @Test fun directoryExposesFourFixedDemoIdentities() {
        assertEquals(
            setOf(DemoRole.DEMO_OWNER, DemoRole.DEMO_ADMIN, DemoRole.DEMO_ACCOUNTANT, DemoRole.DEMO_AUDITOR),
            DemoIdentityDirectory.all().map { it.role }.toSet()
        )
    }

    @Test fun fixtureContainsTenEntitiesAndFortyAccounts() {
        val bundle = fixture()
        assertEquals(10, bundle.entities.size)
        assertEquals(40, bundle.accounts.size)
    }

    @Test fun fixtureSeedsTwentyBalancedJournalEntries() {
        val bundle = fixture()
        val owner = identity("demo-owner")
        val count = bundle.entities.sumOf { bundle.ledger.entries(owner, it.id).size }
        assertEquals(20, count)
    }

    @Test fun accountantCanPostBalancedSyntheticJournal() {
        val bundle = fixture()
        val accountant = identity("demo-accountant")
        val entity = bundle.entities.first()
        val result = bundle.ledger.post(
            accountant,
            JournalEntry(
                id = "test-balanced", entityId = entity.id, description = "Test balanced journal",
                occurredAt = Instant.parse("2026-02-01T00:00:00Z"),
                lines = listOf(
                    JournalLine("${entity.id}-cash", EntrySide.DEBIT, BigDecimal("50.00"), "USD"),
                    JournalLine("${entity.id}-capital", EntrySide.CREDIT, BigDecimal("50.00"), "USD")
                )
            )
        )
        assertEquals("test-balanced", result.id)
    }

    @Test fun unbalancedJournalIsRejected() {
        val bundle = fixture()
        val entity = bundle.entities.first()
        val error = runCatching {
            bundle.ledger.post(
                identity("demo-accountant"),
                JournalEntry(
                    id = "test-unbalanced", entityId = entity.id, description = "Must fail",
                    occurredAt = Instant.parse("2026-02-01T00:00:00Z"),
                    lines = listOf(
                        JournalLine("${entity.id}-cash", EntrySide.DEBIT, BigDecimal("50.00"), "USD"),
                        JournalLine("${entity.id}-capital", EntrySide.CREDIT, BigDecimal("49.99"), "USD")
                    )
                )
            )
        }.exceptionOrNull()
        assertNotNull(error)
        assertTrue(error!!.message!!.contains("Unbalanced"))
    }

    @Test fun auditorCannotPost() {
        val bundle = fixture()
        val entity = bundle.entities.first()
        val error = runCatching {
            bundle.ledger.post(
                identity("demo-auditor"),
                JournalEntry(
                    id = "auditor-write", entityId = entity.id, description = "Must fail",
                    occurredAt = Instant.parse("2026-02-01T00:00:00Z"),
                    lines = listOf(
                        JournalLine("${entity.id}-cash", EntrySide.DEBIT, BigDecimal("10.00"), "USD"),
                        JournalLine("${entity.id}-capital", EntrySide.CREDIT, BigDecimal("10.00"), "USD")
                    )
                )
            )
        }.exceptionOrNull()
        assertNotNull(error)
    }

    @Test fun verifiedOrProviderConnectedSyntheticRecordIsRejected() {
        val bundle = fixture()
        val entity = bundle.entities.first()
        val error = runCatching {
            bundle.ledger.post(
                identity("demo-owner"),
                JournalEntry(
                    id = "provider-marked", entityId = entity.id, description = "Must fail",
                    occurredAt = Instant.parse("2026-02-01T00:00:00Z"),
                    lines = listOf(
                        JournalLine("${entity.id}-cash", EntrySide.DEBIT, BigDecimal("10.00"), "USD"),
                        JournalLine("${entity.id}-capital", EntrySide.CREDIT, BigDecimal("10.00"), "USD")
                    ),
                    provenance = DataProvenance(
                        verified = true, providerConnected = true, sourceReference = "fixture:invalid"
                    )
                )
            )
        }.exceptionOrNull()
        assertNotNull(error)
    }

    @Test fun demoPrincipalCannotCrossWorkspaceBoundary() {
        val bundle = fixture()
        val auth = DemoAuthorizationService(bundle.auditLog)
        val decision = auth.authorize(
            identity("demo-owner").copy(workspaceId = "production"),
            DemoPermission.LEDGER_READ,
            workspaceId = "production"
        )
        assertFalse(decision.allowed)
    }

    @Test fun deleteRequiresExactConfirmationAndCreatesAuditEvent() {
        val bundle = fixture()
        val owner = identity("demo-owner")
        val entry = bundle.ledger.entries(owner, bundle.entities.first().id).first()
        val error = runCatching {
            bundle.ledger.delete(owner, entry.id, DestructiveConfirmation(false, entry.id, ""))
        }.exceptionOrNull()
        assertNotNull(error)
        assertTrue(bundle.ledger.delete(
            owner, entry.id, DestructiveConfirmation(true, entry.id, "Demo fixture cleanup")
        ))
        assertTrue(bundle.auditLog.all().any { it.action == "ledger:delete" && it.targetId == entry.id })
    }

    @Test fun auditorCannotDeleteLedgerEntries() {
        val bundle = fixture()
        val auditor = identity("demo-auditor")
        val entry = bundle.ledger.entries(auditor, bundle.entities.first().id).first()
        val error = runCatching {
            bundle.ledger.delete(
                auditor, entry.id, DestructiveConfirmation(true, entry.id, "Attempt")
            )
        }.exceptionOrNull()
        assertNotNull(error)
    }
}
