package com.vanellye.eria.ficc

import java.math.BigDecimal
import java.time.Instant

/** Local-only FICC demonstration domain. No provider/network/payment capability. */
enum class DemoRole { DEMO_OWNER, DEMO_ADMIN, DEMO_ACCOUNTANT, DEMO_AUDITOR }
enum class DemoPermission {
    WORKSPACE_READ, WORKSPACE_MANAGE, ENTITY_READ, ENTITY_MANAGE,
    LEDGER_READ, LEDGER_POST, LEDGER_RECONCILE, LEDGER_DELETE, AUDIT_READ
}
enum class DataClassification { DEMO, REAL }
enum class DataSourceType { SYNTHETIC, PROVIDER }
enum class AuditOutcome { ALLOWED, DENIED, POSTED, RECONCILED, DELETED }

data class DemoIdentity(
    val id: String,
    val displayName: String,
    val role: DemoRole,
    val workspaceId: String = DEMO_WORKSPACE_ID,
    val isDemoIdentity: Boolean = true
)

data class DataProvenance(
    val classification: DataClassification = DataClassification.DEMO,
    val sourceType: DataSourceType = DataSourceType.SYNTHETIC,
    val verified: Boolean = false,
    val providerConnected: Boolean = false,
    val sourceReference: String
)

data class AuditEvent(
    val id: String,
    val actorId: String,
    val actorRole: DemoRole,
    val action: String,
    val targetId: String,
    val outcome: AuditOutcome,
    val reason: String,
    val occurredAt: Instant,
    val provenance: DataProvenance
)

interface AuditLog {
    fun append(event: AuditEvent)
}

/** Append-only in-memory audit log for local demonstration use. */
class InMemoryAuditLog : AuditLog {
    private val events = mutableListOf<AuditEvent>()

    @Synchronized
    override fun append(event: AuditEvent) {
        require(events.none { it.id == event.id }) { "Duplicate audit event id" }
        events += event
    }

    @Synchronized
    internal fun snapshot(): List<AuditEvent> = events.toList()
}

object DemoIdentityDirectory {
    private val identities = listOf(
        DemoIdentity("demo-owner", "Demo Owner", DemoRole.DEMO_OWNER),
        DemoIdentity("demo-admin", "Demo Administrator", DemoRole.DEMO_ADMIN),
        DemoIdentity("demo-accountant", "Demo Accountant", DemoRole.DEMO_ACCOUNTANT),
        DemoIdentity("demo-auditor", "Demo Auditor", DemoRole.DEMO_AUDITOR)
    ).associateBy { it.id }

    fun all(): List<DemoIdentity> = identities.values.sortedBy { it.id }
    fun find(identityId: String): DemoIdentity? = identities[identityId]
}

class DemoAuditReader(
    private val authorization: DemoAuthorizationService,
    private val auditLog: InMemoryAuditLog
) {
    fun events(actor: DemoIdentity): List<AuditEvent> {
        authorization.require(actor, DemoPermission.AUDIT_READ, "audit-history")
        return auditLog.snapshot()
    }
}

data class AuthorizationDecision(
    val allowed: Boolean,
    val actorId: String,
    val permission: DemoPermission,
    val workspaceId: String,
    val reason: String
)

/** Service-layer RBAC, scoped to the isolated demo workspace and DEMO records. */
class DemoAuthorizationService(private val auditLog: AuditLog) {
    private val grants = mapOf(
        DemoRole.DEMO_OWNER to DemoPermission.values().toSet(),
        DemoRole.DEMO_ADMIN to setOf(
            DemoPermission.WORKSPACE_READ, DemoPermission.WORKSPACE_MANAGE,
            DemoPermission.ENTITY_READ, DemoPermission.ENTITY_MANAGE,
            DemoPermission.LEDGER_READ, DemoPermission.LEDGER_POST,
            DemoPermission.LEDGER_RECONCILE, DemoPermission.AUDIT_READ
        ),
        DemoRole.DEMO_ACCOUNTANT to setOf(
            DemoPermission.WORKSPACE_READ, DemoPermission.ENTITY_READ,
            DemoPermission.LEDGER_READ, DemoPermission.LEDGER_POST,
            DemoPermission.LEDGER_RECONCILE
        ),
        DemoRole.DEMO_AUDITOR to setOf(
            DemoPermission.WORKSPACE_READ, DemoPermission.ENTITY_READ,
            DemoPermission.LEDGER_READ, DemoPermission.AUDIT_READ
        )
    )

    fun authorize(
        actor: DemoIdentity,
        permission: DemoPermission,
        workspaceId: String = DEMO_WORKSPACE_ID,
        classification: DataClassification = DataClassification.DEMO,
        targetId: String = workspaceId
    ): AuthorizationDecision {
        val reason = when {
            !actor.isDemoIdentity || DemoIdentityDirectory.find(actor.id) != actor ->
                "Unknown or non-demo identity"
            actor.workspaceId != DEMO_WORKSPACE_ID || workspaceId != DEMO_WORKSPACE_ID ->
                "Demo identity is outside its authorized workspace"
            classification != DataClassification.DEMO ->
                "Demo identities cannot access non-demo records"
            permission !in grants.getValue(actor.role) ->
                "Role does not grant $permission"
            else -> "Authorized within the local demo workspace"
        }
        val allowed = reason.startsWith("Authorized")
        auditLog.append(
            AuditEvent(
                id = nextId("auth"),
                actorId = actor.id,
                actorRole = actor.role,
                action = "authorize:$permission",
                targetId = targetId,
                outcome = if (allowed) AuditOutcome.ALLOWED else AuditOutcome.DENIED,
                reason = reason,
                occurredAt = Instant.now(),
                provenance = demoProvenance("authorization:${actor.id}")
            )
        )
        return AuthorizationDecision(allowed, actor.id, permission, workspaceId, reason)
    }

    fun require(
        actor: DemoIdentity,
        permission: DemoPermission,
        targetId: String,
        classification: DataClassification = DataClassification.DEMO
    ) {
        val decision = authorize(actor, permission, targetId = targetId, classification = classification)
        check(decision.allowed) { decision.reason }
    }
}

enum class AccountType { ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE }
enum class EntrySide { DEBIT, CREDIT }

data class DemoEntity(
    val id: String,
    val legalName: String,
    val jurisdiction: String,
    val functionalCurrency: String,
    val provenance: DataProvenance = demoProvenance("entity:$id")
)

data class LedgerAccount(
    val id: String,
    val entityId: String,
    val code: String,
    val name: String,
    val type: AccountType,
    val currency: String = "USD",
    val provenance: DataProvenance = demoProvenance("account:$id")
)

data class JournalLine(
    val accountId: String,
    val side: EntrySide,
    val amount: BigDecimal,
    val currency: String
)

data class JournalEntry(
    val id: String,
    val entityId: String,
    val description: String,
    val occurredAt: Instant,
    val lines: List<JournalLine>,
    val provenance: DataProvenance = demoProvenance("journal:$id")
)

data class AccountReconciliation(
    val id: String,
    val entityId: String,
    val accountId: String,
    val statementBalance: BigDecimal,
    val currency: String,
    val reconciledAt: Instant = Instant.now(),
    val provenance: DataProvenance = demoProvenance("reconciliation:$id")
)

data class DestructiveConfirmation(
    val confirmed: Boolean,
    val targetId: String,
    val reason: String
)

class InMemoryDemoLedger(
    private val authorization: DemoAuthorizationService,
    private val auditLog: AuditLog,
    entities: List<DemoEntity>,
    accounts: List<LedgerAccount>
) {
    private val entitiesById = entities.associateBy { it.id }
    private val accountsById = accounts.associateBy { it.id }
    private val journalEntries = mutableListOf<JournalEntry>()
    private val reconciliationRecords = mutableListOf<AccountReconciliation>()

    fun entities(actor: DemoIdentity): List<DemoEntity> {
        authorization.require(actor, DemoPermission.ENTITY_READ, "entities")
        return entitiesById.values.toList()
    }

    fun accounts(actor: DemoIdentity, entityId: String): List<LedgerAccount> {
        requireEntity(entityId)
        authorization.require(actor, DemoPermission.LEDGER_READ, entityId)
        return accountsById.values.filter { it.entityId == entityId }
    }

    @Synchronized
    fun post(actor: DemoIdentity, entry: JournalEntry): JournalEntry {
        authorization.require(actor, DemoPermission.LEDGER_POST, entry.entityId, entry.provenance.classification)
        validate(entry)
        require(journalEntries.none { it.id == entry.id }) { "Journal entry already exists" }
        journalEntries += entry
        auditLog.append(audit(actor, "ledger:post", entry.id, AuditOutcome.POSTED, "Balanced synthetic journal posted"))
        return entry
    }

    @Synchronized
    fun reconcile(actor: DemoIdentity, record: AccountReconciliation): AccountReconciliation {
        authorization.require(actor, DemoPermission.LEDGER_RECONCILE, record.entityId, record.provenance.classification)
        val account = accountsById[record.accountId] ?: error("Unknown ledger account: ${record.accountId}")
        require(account.entityId == record.entityId) { "Reconciliation cannot cross entity boundaries" }
        require(record.currency == account.currency) { "Statement currency must match account currency" }
        require(record.statementBalance >= BigDecimal.ZERO) { "Statement balance cannot be negative" }
        require(record.provenance.classification == DataClassification.DEMO &&
            record.provenance.sourceType == DataSourceType.SYNTHETIC &&
            !record.provenance.verified && !record.provenance.providerConnected
        ) { "Only unverified synthetic statement fixtures can be reconciled in demo mode" }
        val debitNormal = account.type == AccountType.ASSET || account.type == AccountType.EXPENSE
        val net = journalEntries.asSequence()
            .filter { it.entityId == record.entityId }
            .flatMap { it.lines.asSequence() }
            .filter { it.accountId == record.accountId && it.currency == record.currency }
            .fold(BigDecimal.ZERO) { total, line ->
                val debit = if (line.side == EntrySide.DEBIT) line.amount else BigDecimal.ZERO
                val credit = if (line.side == EntrySide.CREDIT) line.amount else BigDecimal.ZERO
                total + if (debitNormal) debit - credit else credit - debit
            }
        require(net.compareTo(record.statementBalance) == 0) {
            "Statement balance ${record.statementBalance} does not match ledger balance $net"
        }
        require(reconciliationRecords.none { it.id == record.id }) { "Reconciliation id already exists" }
        reconciliationRecords += record
        auditLog.append(audit(actor, "ledger:reconcile", record.id, AuditOutcome.RECONCILED, "Statement and ledger balances match"))
        return record
    }

    @Synchronized
    fun reconciliations(actor: DemoIdentity, entityId: String): List<AccountReconciliation> {
        requireEntity(entityId)
        authorization.require(actor, DemoPermission.LEDGER_READ, entityId)
        return reconciliationRecords.filter { it.entityId == entityId }.toList()
    }

    @Synchronized
    fun delete(actor: DemoIdentity, entryId: String, confirmation: DestructiveConfirmation): Boolean {
        authorization.require(actor, DemoPermission.LEDGER_DELETE, entryId)
        require(confirmation.confirmed && confirmation.targetId == entryId) {
            "Explicit confirmation for the exact journal entry is required"
        }
        require(confirmation.reason.isNotBlank()) { "A deletion reason is required" }
        val existing = journalEntries.firstOrNull { it.id == entryId } ?: return false
        journalEntries.remove(existing)
        auditLog.append(audit(actor, "ledger:delete", entryId, AuditOutcome.DELETED, confirmation.reason))
        return true
    }

    @Synchronized
    fun entries(actor: DemoIdentity, entityId: String): List<JournalEntry> {
        requireEntity(entityId)
        authorization.require(actor, DemoPermission.LEDGER_READ, entityId)
        return journalEntries.filter { it.entityId == entityId }.toList()
    }

    private fun validate(entry: JournalEntry) {
        requireEntity(entry.entityId)
        require(entry.provenance.classification == DataClassification.DEMO) {
            "Only DEMO-classified records may enter the synthetic ledger"
        }
        require(entry.provenance.sourceType == DataSourceType.SYNTHETIC) {
            "Synthetic ledger accepts SYNTHETIC source records only"
        }
        require(!entry.provenance.verified && !entry.provenance.providerConnected) {
            "Synthetic records cannot claim provider verification or connectivity"
        }
        require(entry.lines.size >= 2) { "A journal requires at least two lines" }
        entry.lines.forEach { line ->
            require(line.amount > BigDecimal.ZERO) { "Journal amounts must be positive" }
            require(line.currency.matches(Regex("[A-Z]{3}"))) { "Currency must be ISO-style 3-letter code" }
            val account = accountsById[line.accountId] ?: error("Unknown ledger account: ${line.accountId}")
            require(account.entityId == entry.entityId) { "Journal cannot cross entity boundaries" }
            require(account.currency == line.currency) { "Line currency must match account currency" }
        }
        entry.lines.groupBy { it.currency }.forEach { (currency, lines) ->
            val debits = lines.filter { it.side == EntrySide.DEBIT }
                .fold(BigDecimal.ZERO) { total, line -> total + line.amount }
            val credits = lines.filter { it.side == EntrySide.CREDIT }
                .fold(BigDecimal.ZERO) { total, line -> total + line.amount }
            require(debits.compareTo(credits) == 0) {
                "Unbalanced $currency journal: debits=$debits credits=$credits"
            }
        }
    }

    private fun requireEntity(entityId: String): DemoEntity =
        entitiesById[entityId] ?: error("Unknown demo entity: $entityId")

    private fun audit(actor: DemoIdentity, action: String, targetId: String, outcome: AuditOutcome, reason: String) =
        AuditEvent(
            id = nextId("ledger"),
            actorId = actor.id,
            actorRole = actor.role,
            action = action,
            targetId = targetId,
            outcome = outcome,
            reason = reason,
            occurredAt = Instant.now(),
            provenance = demoProvenance("audit:$targetId")
        )
}

data class DemoLedgerBundle(
    val identities: List<DemoIdentity>,
    val entities: List<DemoEntity>,
    val accounts: List<LedgerAccount>,
    val ledger: InMemoryDemoLedger,
    val auditReader: DemoAuditReader
)

/** Reproducibly seeds ten fictional companies and balanced opening journals. */
object DemoLedgerFactory {
    private val entityNames = listOf(
        "Aster Harbor Holdings LLC", "Blue Meridian Services Inc.",
        "Cedar Orbit Logistics LLC", "Delta Lantern Software Inc.",
        "Evergreen Vector Trading LLC", "Fable Ridge Manufacturing Inc.",
        "Golden Current Media LLC", "Horizon Vale Consulting Inc.",
        "Ivory Compass Research LLC", "Juniper Atlas Properties Inc."
    )

    fun create(): DemoLedgerBundle {
        val entities = entityNames.mapIndexed { index, name ->
            DemoEntity(
                id = "demo-entity-${(index + 1).toString().padStart(2, '0')}",
                legalName = name,
                jurisdiction = "US-DEMO",
                functionalCurrency = "USD"
            )
        }
        val accounts = entities.flatMap { entity ->
            listOf(
                LedgerAccount("${entity.id}-cash", entity.id, "1000", "Demo operating cash", AccountType.ASSET),
                LedgerAccount("${entity.id}-receivable", entity.id, "1100", "Demo receivables", AccountType.ASSET),
                LedgerAccount("${entity.id}-payable", entity.id, "2000", "Demo accounts payable", AccountType.LIABILITY),
                LedgerAccount("${entity.id}-capital", entity.id, "3000", "Demo contributed capital", AccountType.EQUITY),
                LedgerAccount("${entity.id}-revenue", entity.id, "4000", "Demo service revenue", AccountType.REVENUE),
                LedgerAccount("${entity.id}-expense", entity.id, "5000", "Demo operating expense", AccountType.EXPENSE)
            )
        }
        val audit = InMemoryAuditLog()
        val authorization = DemoAuthorizationService(audit)
        val ledger = InMemoryDemoLedger(authorization, audit, entities, accounts)
        val owner = DemoIdentityDirectory.find("demo-owner")!!
        entities.forEachIndexed { index, entity ->
            val opening = BigDecimal("100000.00").add(BigDecimal(index * 1000))
            ledger.post(
                owner,
                JournalEntry(
                    id = "seed-${entity.id}-capital",
                    entityId = entity.id,
                    description = "Synthetic opening capital fixture",
                    occurredAt = Instant.parse("2026-01-01T00:00:00Z"),
                    lines = listOf(
                        JournalLine("${entity.id}-cash", EntrySide.DEBIT, opening, "USD"),
                        JournalLine("${entity.id}-capital", EntrySide.CREDIT, opening, "USD")
                    )
                )
            )
            ledger.post(
                owner,
                JournalEntry(
                    id = "seed-${entity.id}-revenue",
                    entityId = entity.id,
                    description = "Synthetic service invoice fixture",
                    occurredAt = Instant.parse("2026-01-15T00:00:00Z"),
                    lines = listOf(
                        JournalLine("${entity.id}-receivable", EntrySide.DEBIT, BigDecimal("1250.00"), "USD"),
                        JournalLine("${entity.id}-revenue", EntrySide.CREDIT, BigDecimal("1250.00"), "USD")
                    )
                )
            )
            ledger.post(
                owner,
                JournalEntry(
                    id = "seed-${entity.id}-payable",
                    entityId = entity.id,
                    description = "Synthetic vendor bill fixture",
                    occurredAt = Instant.parse("2026-01-20T00:00:00Z"),
                    lines = listOf(
                        JournalLine("${entity.id}-expense", EntrySide.DEBIT, BigDecimal("375.00"), "USD"),
                        JournalLine("${entity.id}-payable", EntrySide.CREDIT, BigDecimal("375.00"), "USD")
                    )
                )
            )
        }
        return DemoLedgerBundle(
            DemoIdentityDirectory.all(), entities, accounts, ledger, DemoAuditReader(authorization, audit)
        )
    }
}

private const val DEMO_WORKSPACE_ID = "ficc-demo-workspace"
private fun nextId(prefix: String): String = "$prefix-${java.util.UUID.randomUUID()}"
fun demoProvenance(reference: String) = DataProvenance(sourceReference = reference)
