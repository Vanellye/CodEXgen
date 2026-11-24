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
}
