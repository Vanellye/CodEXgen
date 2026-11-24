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

    @Test fun fixtureContainsTenEntitiesAndSixtyAccounts() {
        val bundle = fixture()
        assertEquals(10, bundle.entities.size)
        assertEquals(60, bundle.accounts.size)
    }

    @Test fun fixtureSeedsThirtyBalancedJournalEntries() {
        val bundle = fixture()
        val owner = identity("demo-owner")
        val count = bundle.entities.sumOf { bundle.ledger.entries(owner, it.id).size }
        assertEquals(30, count)
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
        val auth = DemoAuthorizationService(InMemoryAuditLog())
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
        assertTrue(bundle.auditReader.events(owner).any { it.action == "ledger:delete" && it.targetId == entry.id })
    }


    @Test fun realProviderRecordCannotEnterSyntheticLedger() {
        val bundle = fixture()
        val entity = bundle.entities.first()
        val error = runCatching {
            bundle.ledger.post(
                identity("demo-owner"),
                JournalEntry(
                    id = "real-record",
                    entityId = entity.id,
                    description = "Provider-origin data is outside this ledger",
                    occurredAt = Instant.parse("2026-02-01T00:00:00Z"),
                    lines = listOf(
                        JournalLine("${entity.id}-cash", EntrySide.DEBIT, BigDecimal("10.00"), "USD"),
                        JournalLine("${entity.id}-capital", EntrySide.CREDIT, BigDecimal("10.00"), "USD")
                    ),
                    provenance = DataProvenance(
                        classification = DataClassification.REAL,
                        sourceType = DataSourceType.PROVIDER,
                        verified = true,
                        providerConnected = true,
                        sourceReference = "provider:fixture"
                    )
                )
            )
        }.exceptionOrNull()
        assertNotNull(error)
    }

    @Test fun accountantCannotReadAuditHistory() {
        val bundle = fixture()
        val error = runCatching {
            bundle.auditReader.events(identity("demo-accountant"))
        }.exceptionOrNull()
        assertNotNull(error)
    }


    @Test fun accountantCanReconcileMatchingSyntheticStatement() {
        val bundle = fixture()
        val entity = bundle.entities.first()
        val record = AccountReconciliation(
            id = "cash-recon-1",
            entityId = entity.id,
            accountId = "${entity.id}-cash",
            statementBalance = BigDecimal("100000.00"),
            currency = "USD"
        )
        assertEquals(record, bundle.ledger.reconcile(identity("demo-accountant"), record))
    }

    @Test fun reconciliationRejectsStatementMismatch() {
        val bundle = fixture()
        val entity = bundle.entities.first()
        val error = runCatching {
            bundle.ledger.reconcile(
                identity("demo-accountant"),
                AccountReconciliation(
                    id = "cash-recon-mismatch",
                    entityId = entity.id,
                    accountId = "${entity.id}-cash",
                    statementBalance = BigDecimal("99999.99"),
                    currency = "USD"
                )
            )
        }.exceptionOrNull()
        assertNotNull(error)
        assertTrue(error!!.message!!.contains("does not match"))
    }

    @Test fun journalCannotMixEntities() {
        val bundle = fixture()
        val first = bundle.entities[0]
        val second = bundle.entities[1]
        val error = runCatching {
            bundle.ledger.post(
                identity("demo-accountant"),
                JournalEntry(
                    id = "cross-entity-journal",
                    entityId = first.id,
                    description = "Must fail entity isolation",
                    occurredAt = Instant.parse("2026-02-01T00:00:00Z"),
                    lines = listOf(
                        JournalLine("${first.id}-cash", EntrySide.DEBIT, BigDecimal("5.00"), "USD"),
                        JournalLine("${second.id}-capital", EntrySide.CREDIT, BigDecimal("5.00"), "USD")
                    )
                )
            )
        }.exceptionOrNull()
        assertNotNull(error)
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

    @Test fun everyEntityHasSixUniqueSyntheticAccounts() {
        val bundle = fixture()
        assertEquals(bundle.accounts.size, bundle.accounts.map { it.id }.toSet().size)
        bundle.entities.forEach { entity ->
            val accounts = bundle.accounts.filter { it.entityId == entity.id }
            assertEquals(6, accounts.size)
            assertEquals(setOf("1000", "1100", "2000", "3000", "4000", "5000"), accounts.map { it.code }.toSet())
            assertTrue(accounts.all {
                it.provenance.classification == DataClassification.DEMO &&
                    it.provenance.sourceType == DataSourceType.SYNTHETIC &&
                    !it.provenance.verified && !it.provenance.providerConnected
            })
        }
    }

    @Test fun eachEntityHasThreeBalancedSyntheticSeedJournals() {
        val bundle = fixture()
        val owner = identity("demo-owner")
        bundle.entities.forEach { entity ->
            val entries = bundle.ledger.entries(owner, entity.id)
            assertEquals(3, entries.size)
            assertEquals(
                setOf("seed-${entity.id}-capital", "seed-${entity.id}-revenue", "seed-${entity.id}-payable"),
                entries.map { it.id }.toSet()
            )
            entries.forEach { entry ->
                assertEquals(DataClassification.DEMO, entry.provenance.classification)
                assertEquals(DataSourceType.SYNTHETIC, entry.provenance.sourceType)
                assertFalse(entry.provenance.verified)
                assertFalse(entry.provenance.providerConnected)
                entry.lines.groupBy { it.currency }.forEach { (_, lines) ->
                    val debits = lines.filter { it.side == EntrySide.DEBIT }
                        .fold(BigDecimal.ZERO) { total, line -> total + line.amount }
                    val credits = lines.filter { it.side == EntrySide.CREDIT }
                        .fold(BigDecimal.ZERO) { total, line -> total + line.amount }
                    assertEquals(0, debits.compareTo(credits))
                }
            }
        }
    }

}
