package com.vanellye.eria.ficc

import java.math.BigDecimal
import java.time.Instant

enum class ProviderExecutionMode { LOCAL_SIMULATION, LIVE_PROVIDER }
enum class ProviderCapability { ACCOUNT_DISCOVERY, BALANCE_READ, TRANSACTION_READ, PAYMENT_INITIATION, TRANSFER_INITIATION }
data class ProviderAccountSnapshot(val providerAccountId:String,val displayName:String,val currency:String,val availableBalance:BigDecimal,val provenance:DataProvenance)
data class ProviderTransactionSnapshot(val providerTransactionId:String,val description:String,val amount:BigDecimal,val currency:String,val occurredAt:Instant,val provenance:DataProvenance)

interface FiccProviderAdapter {
 val providerId:String
 val capabilities:Set<ProviderCapability>
 fun accounts():List<ProviderAccountSnapshot>
 fun transactions(accountId:String):List<ProviderTransactionSnapshot>
}

/** Live-provider mode is rejected in this demonstration build. */
object FiccProviderPolicy {
 fun requireAllowed(mode:ProviderExecutionMode) { check(mode==ProviderExecutionMode.LOCAL_SIMULATION) { "Live financial providers are disabled in FICC demo mode" } }
}

/** Deterministic local fixture adapter. No network, credentials, or provider SDK. */
class DeterministicProviderSandbox:FiccProviderAdapter {
 override val providerId="ficc.synthetic.sandbox.v1"
 override val capabilities=setOf(ProviderCapability.ACCOUNT_DISCOVERY,ProviderCapability.BALANCE_READ,ProviderCapability.TRANSACTION_READ)
 override fun accounts():List<ProviderAccountSnapshot> {
  FiccProviderPolicy.requireAllowed(ProviderExecutionMode.LOCAL_SIMULATION)
  return listOf(ProviderAccountSnapshot("sandbox-operating-001","Synthetic Operating Account","USD",BigDecimal("125000.00"),demoProvenance("provider-sandbox:account")))
 }
 override fun transactions(accountId:String):List<ProviderTransactionSnapshot> {
  FiccProviderPolicy.requireAllowed(ProviderExecutionMode.LOCAL_SIMULATION)
  require(accountId=="sandbox-operating-001") { "Unknown synthetic sandbox account" }
  val p=demoProvenance("provider-sandbox:transactions")
  return listOf(
   ProviderTransactionSnapshot("sandbox-tx-001","Synthetic customer receipt",BigDecimal("1250.00"),"USD",Instant.parse("2026-01-15T12:00:00Z"),p),
   ProviderTransactionSnapshot("sandbox-tx-002","Synthetic office expense",BigDecimal("-375.00"),"USD",Instant.parse("2026-01-20T12:00:00Z"),p)
  )
 }
}
