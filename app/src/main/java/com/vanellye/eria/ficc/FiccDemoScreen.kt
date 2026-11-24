package com.vanellye.eria.ficc

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.Button
import androidx.compose.material.Card
import androidx.compose.material.MaterialTheme
import androidx.compose.material.OutlinedButton
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp

@Composable
fun FiccDemoScreen(onBack:()->Unit,modifier:Modifier=Modifier) {
 val context=LocalContext.current
 val sessions=remember { FiccDemoSessionManager(context) }
 val store=remember { FiccSqliteStore(context) }
 val sandbox=remember { DeterministicProviderSandbox() }
 var session by remember { mutableStateOf(sessions.current()) }
 var counts by remember { mutableStateOf(FiccStoreCounts(0,0,0,0,0,0)) }
 var names by remember { mutableStateOf(emptyList<String>()) }
 var auditValid by remember { mutableStateOf(false) }
 var balance by remember { mutableStateOf("Not loaded") }
 DisposableEffect(store) {
  store.seedIfEmpty(DemoLedgerFactory.create());counts=store.counts();names=store.entityNames();auditValid=store.verifyAuditChain()
  onDispose { store.close() }
 }
 Column(modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),verticalArrangement=Arrangement.spacedBy(12.dp)) {
  Row(Modifier.fillMaxWidth()) { Text("FICC • Demo workspace",style=MaterialTheme.typography.h6);OutlinedButton(onClick=onBack) { Text("Back") } }
  Text("Synthetic data only • local SQLite • live providers disabled")
  Card(Modifier.fillMaxWidth()) {
   Column(Modifier.padding(12.dp),verticalArrangement=Arrangement.spacedBy(8.dp)) {
    Text("Demo identity session",style=MaterialTheme.typography.subtitle1)
    if(session==null) {
     Text("Select a demo role. This is not real login or identity verification.")
     DemoIdentityDirectory.all().forEach { identity -> Button(onClick={session=sessions.start(identity.id)}) { Text("Continue as "+identity.displayName) } }
    } else {
     Text("Active: "+session!!.identity.displayName+" • "+session!!.identity.role)
     Text("Expires: "+session!!.expiresAt.toString())
     OutlinedButton(onClick={sessions.end();session=null}) { Text("End demo session") }
    }
   }
  }
  Card(Modifier.fillMaxWidth()) {
   Column(Modifier.padding(12.dp),verticalArrangement=Arrangement.spacedBy(6.dp)) {
    Text("Persistent synthetic ledger",style=MaterialTheme.typography.subtitle1)
    Text("Entities: "+counts.entities+" • Accounts: "+counts.accounts)
    Text("Journals: "+counts.journals+" • Lines: "+counts.journalLines)
    Text("Audit events: "+counts.auditEvents+" • Reconciliations: "+counts.reconciliations)
    Text("Audit hash chain: "+if(auditValid) "VALID" else "NOT VERIFIED")
    Text("App-private SQLite storage • device-local")
   }
  }
  Card(Modifier.fillMaxWidth()) {
   Column(Modifier.padding(12.dp),verticalArrangement=Arrangement.spacedBy(6.dp)) {
    Text("Provider adapter sandbox",style=MaterialTheme.typography.subtitle1)
    Text("Adapter: "+sandbox.providerId+" • LOCAL_SIMULATION")
    Button(onClick={balance=sandbox.accounts().first().availableBalance.toPlainString()}) { Text("Load synthetic balance") }
    Text("Synthetic balance: "+balance+" USD")
    Text("No bank, wallet, payment, transfer, or external API is connected.")
   }
  }
  Text("Fictional entities",style=MaterialTheme.typography.subtitle1)
  names.forEach { Text("• "+it) }
  Text("Demo data persists across app restarts on this device. Local SQLite is not a production or tamper-proof accounting system.",style=MaterialTheme.typography.caption)
 }
}
