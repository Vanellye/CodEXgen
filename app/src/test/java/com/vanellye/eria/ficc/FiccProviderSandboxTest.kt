package com.vanellye.eria.ficc

import java.math.BigDecimal
import org.junit.Assert.*
import org.junit.Test

class FiccProviderSandboxTest {
 @Test fun sandboxIsDeterministicAndSynthetic() {
  val adapter=DeterministicProviderSandbox()
  assertEquals("ficc.synthetic.sandbox.v1",adapter.providerId)
  assertEquals(BigDecimal("125000.00"),adapter.accounts().single().availableBalance)
  assertEquals(2,adapter.transactions("sandbox-operating-001").size)
  assertTrue(adapter.accounts().single().provenance.classification==DataClassification.DEMO)
  assertFalse(adapter.accounts().single().provenance.providerConnected)
 }
 @Test fun liveProviderModeIsRejected() {
  val error=runCatching { FiccProviderPolicy.requireAllowed(ProviderExecutionMode.LIVE_PROVIDER) }.exceptionOrNull()
  assertNotNull(error)
  assertTrue(error!!.message!!.contains("disabled"))
 }
 @Test fun sandboxRejectsUnknownAccount() {
  assertTrue(runCatching { DeterministicProviderSandbox().transactions("real-account") }.isFailure)
 }

 @Test fun fixtureBalancesAndTransactionsAreExactAndDeterministic() {
  val adapter=DeterministicProviderSandbox()
  val firstAccounts=adapter.accounts()
  val secondAccounts=adapter.accounts()
  assertEquals(firstAccounts,secondAccounts)
  val account=firstAccounts.single()
  assertEquals("sandbox-operating-001",account.providerAccountId)
  assertEquals("USD",account.currency)
  assertEquals(BigDecimal("125000.00"),account.availableBalance)
  assertEquals("provider-sandbox:account",account.provenance.sourceReference)

  val firstTransactions=adapter.transactions(account.providerAccountId)
  assertEquals(firstTransactions,adapter.transactions(account.providerAccountId))
  assertEquals(listOf("sandbox-tx-001","sandbox-tx-002"),firstTransactions.map { it.providerTransactionId })
  assertEquals(listOf(BigDecimal("1250.00"),BigDecimal("-375.00")),firstTransactions.map { it.amount })
  assertTrue(firstTransactions.all {
   it.currency=="USD" &&
    it.provenance.classification==DataClassification.DEMO &&
    it.provenance.sourceType==DataSourceType.SYNTHETIC &&
    !it.provenance.verified && !it.provenance.providerConnected &&
    it.provenance.sourceReference=="provider-sandbox:transactions"
  })
 }

 @Test fun sandboxExposesReadOnlyCapabilitiesOnly() {
  val capabilities=DeterministicProviderSandbox().capabilities
  assertEquals(
   setOf(ProviderCapability.ACCOUNT_DISCOVERY,ProviderCapability.BALANCE_READ,ProviderCapability.TRANSACTION_READ),
   capabilities
  )
  assertFalse(capabilities.contains(ProviderCapability.PAYMENT_INITIATION))
  assertFalse(capabilities.contains(ProviderCapability.TRANSFER_INITIATION))
 }

}
