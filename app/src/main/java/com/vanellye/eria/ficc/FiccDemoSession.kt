package com.vanellye.eria.ficc

import android.content.Context
import java.time.Instant

data class DemoSession(val identity:DemoIdentity,val issuedAt:Instant,val expiresAt:Instant)

/** Demo role selector only; this is not authentication or identity proofing. */
class FiccDemoSessionManager(context:Context) {
 private val prefs=context.applicationContext.getSharedPreferences("ficc_demo_session",Context.MODE_PRIVATE)
 fun current(now:Instant=Instant.now()):DemoSession? {
  val id=prefs.getString("identity_id",null)?:return null
  val issued=prefs.getLong("issued_at",0L);val expires=prefs.getLong("expires_at",0L)
  if(issued<=0L || expires<=now.toEpochMilli()) { end();return null }
  val identity=DemoIdentityDirectory.find(id)?:run { end();return null }
  return DemoSession(identity,Instant.ofEpochMilli(issued),Instant.ofEpochMilli(expires))
 }
 fun start(identityId:String,now:Instant=Instant.now()):DemoSession {
  val identity=requireNotNull(DemoIdentityDirectory.find(identityId)) { "Unknown demo principal" }
  val expires=now.plusSeconds(1800)
  check(prefs.edit().putString("identity_id",identity.id).putLong("issued_at",now.toEpochMilli()).putLong("expires_at",expires.toEpochMilli()).commit())
  return DemoSession(identity,now,expires)
 }
 fun end() { prefs.edit().remove("identity_id").remove("issued_at").remove("expires_at").commit() }
}
