package com.vanellye.eria.financial

import java.math.BigDecimal

/**
 * Kotlin mirror of financial/contracts/financial-provider.schema.json.
 * Keep field names and enum values aligned with the language-neutral schema.
 * This contract contains no gateway approval-service or PONS dependency.
 */
enum class ExecutionMode { SIMULATION_ONLY }

enum class FinancialCapability {
    ACCOUNTS_READ,
    BALANCES_READ,
    TRANSACTIONS_READ,
    TRANSFERS_PREVIEW,
    TRANSFERS_SIMULATE,
    RECONCILIATION_READ,
}

data class Money(
    val amount: BigDecimal,
    val currency: String,
) {
    init {
        require(amount >= BigDecimal.ZERO) { "Money amount cannot be negative." }
        require(currency.matches(Regex("^[A-Z]{3}$"))) { "Currency must be an ISO-style uppercase code." }
    }
}

data class ProviderDescriptor(
    val id: String,
    val displayName: String,
    val mode: ExecutionMode,
    val capabilities: Set<FinancialCapability>,
)

data class FinancialAccount(
    val id: String,
    val providerId: String,
    val name: String,
    val type: String,
    val currency: String,
    val status: String,
)

data class AccountBalance(
    val accountId: String,
    val available: Money,
    val ledger: Money,
    val asOf: String,
)

data class FinancialTransaction(
    val id: String,
    val providerId: String,
    val accountId: String,
    val direction: String,
    val amount: Money,
    val status: String,
    val description: String,
    val createdAt: String,
    val simulated: Boolean,
)

data class TransferDraft(
    val sourceAccountId: String,
    val destinationAccountId: String,
    val amount: Money,
    val memo: String? = null,
)

data class TransferPreview(
    val id: String,
    val providerId: String,
    val mode: ExecutionMode,
    val draft: TransferDraft,
    val fee: Money,
    val totalDebit: Money,
    val expiresAt: String,
    val digest: String,
    val status: String,
)

data class SimulationReceipt(
    val id: String,
    val previewId: String,
    val providerId: String,
    val mode: ExecutionMode,
    val status: String,
    val simulated: Boolean,
    val createdAt: String,
)

data class ReconciliationSnapshot(
    val providerId: String,
    val mode: ExecutionMode,
    val accountCount: Int,
    val transactionCount: Int,
    val generatedAt: String,
)

interface FinancialProvider {
    val descriptor: ProviderDescriptor

    suspend fun listAccounts(): List<FinancialAccount>
    suspend fun getBalance(accountId: String): AccountBalance
    suspend fun listTransactions(accountId: String): List<FinancialTransaction>
    suspend fun createTransferPreview(draft: TransferDraft): TransferPreview

    /** Must mutate only a local synthetic ledger; never call an external provider. */
    suspend fun simulateTransfer(previewId: String): SimulationReceipt

    suspend fun getReconciliationSnapshot(): ReconciliationSnapshot
}

/**
 * Explicit registry: exact provider selection, no automatic fallback.
 * The initial runtime accepts simulation-only adapters exclusively.
 */
class ProviderRegistry {
    private val providers = linkedMapOf<String, FinancialProvider>()

    fun register(provider: FinancialProvider) {
        val descriptor = provider.descriptor
        require(descriptor.id.matches(Regex("^[a-z][a-z0-9-]{1,63}$"))) {
            "Invalid provider id: ${descriptor.id}"
        }
        require(descriptor.mode == ExecutionMode.SIMULATION_ONLY) {
            "Only simulation-only providers are enabled in this baseline."
        }
        require(!providers.containsKey(descriptor.id)) {
            "Provider already registered: ${descriptor.id}"
        }
        providers[descriptor.id] = provider
    }

    fun resolve(
        providerId: String,
        required: Set<FinancialCapability> = emptySet(),
    ): FinancialProvider {
        val provider = providers[providerId]
            ?: error("Provider not registered: $providerId")
        val missing = required - provider.descriptor.capabilities
        require(missing.isEmpty()) {
            "Provider $providerId lacks required capabilities: ${missing.joinToString()}"
        }
        return provider
    }

    fun descriptors(): List<ProviderDescriptor> = providers.values.map { it.descriptor }
}
