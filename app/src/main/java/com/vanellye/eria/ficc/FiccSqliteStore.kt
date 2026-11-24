package com.vanellye.eria.ficc

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import java.math.BigDecimal
import java.security.MessageDigest
import java.time.Instant

data class FiccStoreCounts(val entities:Int,val accounts:Int,val journals:Int,val journalLines:Int,val auditEvents:Int)

/** App-private SQLite persistence for synthetic FICC fixtures. Local storage is not tamper-proof. */
class FiccSqliteStore(context:Context):SQLiteOpenHelper(context.applicationContext,"ficc_demo.db",null,1) {
 override fun onCreate(db:SQLiteDatabase) {
  db.execSQL("CREATE TABLE entities(id TEXT PRIMARY KEY, legal_name TEXT NOT NULL, jurisdiction TEXT NOT NULL, currency TEXT NOT NULL, provenance_ref TEXT NOT NULL)")
  db.execSQL("CREATE TABLE accounts(id TEXT PRIMARY KEY, entity_id TEXT NOT NULL, code TEXT NOT NULL, name TEXT NOT NULL, type TEXT NOT NULL, currency TEXT NOT NULL, provenance_ref TEXT NOT NULL)")
  db.execSQL("CREATE TABLE journals(id TEXT PRIMARY KEY, entity_id TEXT NOT NULL, description TEXT NOT NULL, occurred_at TEXT NOT NULL, provenance_ref TEXT NOT NULL)")
  db.execSQL("CREATE TABLE journal_lines(id INTEGER PRIMARY KEY AUTOINCREMENT, journal_id TEXT NOT NULL, account_id TEXT NOT NULL, side TEXT NOT NULL, amount TEXT NOT NULL, currency TEXT NOT NULL)")
  db.execSQL("CREATE TABLE audit_events(sequence INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT UNIQUE NOT NULL,actor_id TEXT NOT NULL,actor_role TEXT NOT NULL,action TEXT NOT NULL,target_id TEXT NOT NULL,outcome TEXT NOT NULL,reason TEXT NOT NULL,occurred_at TEXT NOT NULL,provenance_ref TEXT NOT NULL,previous_hash TEXT NOT NULL,event_hash TEXT NOT NULL)")
  db.execSQL("CREATE INDEX idx_accounts_entity ON accounts(entity_id)")
  db.execSQL("CREATE INDEX idx_journals_entity ON journals(entity_id)")
 }
 override fun onUpgrade(db:SQLiteDatabase,oldVersion:Int,newVersion:Int) {
  // Forward-only schema migrations: never drop user or audit data.
 }

 fun seedIfEmpty(bundle:DemoLedgerBundle) {
  val db=writableDatabase; db.beginTransaction()
  try {
   val count=db.rawQuery("SELECT COUNT(*) FROM entities",null).use { it.moveToFirst();it.getInt(0) }
   if(count==0) {
    bundle.entities.forEach { e -> db.insertOrThrow("entities",null,ContentValues().apply {
     put("id",e.id);put("legal_name",e.legalName);put("jurisdiction",e.jurisdiction);put("currency",e.functionalCurrency);put("provenance_ref",e.provenance.sourceReference)
    }) }
    bundle.accounts.forEach { a -> db.insertOrThrow("accounts",null,ContentValues().apply {
     put("id",a.id);put("entity_id",a.entityId);put("code",a.code);put("name",a.name);put("type",a.type.name);put("currency",a.currency);put("provenance_ref",a.provenance.sourceReference)
    }) }
    val owner=DemoIdentityDirectory.find("demo-owner")!!
    bundle.entities.forEach { e -> bundle.ledger.entries(owner,e.id).forEach { insertJournal(db,it) } }
    bundle.auditReader.events(owner).forEach { appendAudit(db,it) }
   }
   db.setTransactionSuccessful()
  } finally { db.endTransaction() }
 }

 fun counts():FiccStoreCounts {
  val db=readableDatabase
  fun n(table:String)=db.rawQuery("SELECT COUNT(*) FROM $table",null).use { it.moveToFirst();it.getInt(0) }
  return FiccStoreCounts(n("entities"),n("accounts"),n("journals"),n("journal_lines"),n("audit_events"))
 }
 fun entityNames():List<String> = readableDatabase.rawQuery("SELECT legal_name FROM entities ORDER BY id",null).use { c -> buildList { while(c.moveToNext()) add(c.getString(0)) } }

 fun postJournal(actor:DemoIdentity,entry:JournalEntry) {
  val auth=DemoAuthorizationService(InMemoryAuditLog())
  auth.require(actor,DemoPermission.LEDGER_POST,entry.entityId,entry.provenance.classification)
  require(entry.provenance.classification==DataClassification.DEMO && entry.provenance.sourceType==DataSourceType.SYNTHETIC && !entry.provenance.verified && !entry.provenance.providerConnected) { "Only synthetic DEMO data is accepted" }
  require(entry.lines.size>=2 && entry.lines.all { it.amount>BigDecimal.ZERO }) { "Journal requires at least two positive lines" }
  entry.lines.groupBy { it.currency }.forEach { (currency,lines) ->
   val d=lines.filter { it.side==EntrySide.DEBIT }.fold(BigDecimal.ZERO) { a,l -> a+l.amount }
   val c=lines.filter { it.side==EntrySide.CREDIT }.fold(BigDecimal.ZERO) { a,l -> a+l.amount }
   require(d.compareTo(c)==0) { "Unbalanced $currency journal" }
  }
  val db=writableDatabase;db.beginTransaction()
  try {
   entry.lines.forEach { l -> db.rawQuery("SELECT entity_id,currency FROM accounts WHERE id=?",arrayOf(l.accountId)).use { c ->
    require(c.moveToFirst() && c.getString(0)==entry.entityId && c.getString(1)==l.currency) { "Account/entity/currency mismatch for " + l.accountId }
   } }
   insertJournal(db,entry)
   appendAudit(db,AuditEvent("sqlite-post-"+entry.id,actor.id,actor.role,"ledger:post",entry.id,AuditOutcome.POSTED,"Balanced synthetic journal persisted",Instant.now(),demoProvenance("sqlite-audit:"+entry.id)))
   db.setTransactionSuccessful()
  } finally { db.endTransaction() }
 }

 fun verifyAuditChain():Boolean {
  var previous=GENESIS
  return readableDatabase.rawQuery("SELECT event_id,actor_id,actor_role,action,target_id,outcome,reason,occurred_at,provenance_ref,previous_hash,event_hash FROM audit_events ORDER BY sequence",null).use { c ->
   while(c.moveToNext()) {
    val payload=(0..8).map { c.getString(it) }.joinToString("|")
    if(c.getString(9)!=previous) return@use false
    val expected=sha256(previous+payload)
    if(c.getString(10)!=expected) return@use false
    previous=expected
   };true
  }
 }

 private fun insertJournal(db:SQLiteDatabase,e:JournalEntry) {
  db.insertOrThrow("journals",null,ContentValues().apply { put("id",e.id);put("entity_id",e.entityId);put("description",e.description);put("occurred_at",e.occurredAt.toString());put("provenance_ref",e.provenance.sourceReference) })
  e.lines.forEach { l -> db.insertOrThrow("journal_lines",null,ContentValues().apply { put("journal_id",e.id);put("account_id",l.accountId);put("side",l.side.name);put("amount",l.amount.toPlainString());put("currency",l.currency) }) }
 }
 private fun appendAudit(db:SQLiteDatabase,e:AuditEvent) {
  val previous=db.rawQuery("SELECT event_hash FROM audit_events ORDER BY sequence DESC LIMIT 1",null).use { if(it.moveToFirst()) it.getString(0) else GENESIS }
  val payload=listOf(e.id,e.actorId,e.actorRole.name,e.action,e.targetId,e.outcome.name,e.reason,e.occurredAt.toString(),e.provenance.sourceReference).joinToString("|")
  val digest=sha256(previous+payload)
  db.insertOrThrow("audit_events",null,ContentValues().apply {
   put("event_id",e.id);put("actor_id",e.actorId);put("actor_role",e.actorRole.name);put("action",e.action);put("target_id",e.targetId);put("outcome",e.outcome.name);put("reason",e.reason);put("occurred_at",e.occurredAt.toString());put("provenance_ref",e.provenance.sourceReference);put("previous_hash",previous);put("event_hash",digest)
  })
 }
 private fun sha256(s:String)=MessageDigest.getInstance("SHA-256").digest(s.toByteArray()).joinToString("") { "%02x".format(it) }
 companion object { private const val GENESIS="FICC-DEMO-AUDIT-GENESIS-v1" }
}
