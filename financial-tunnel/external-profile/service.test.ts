import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { createExternalProfileServer, hashTransactionPreview } from "./service.ts";
import type { ExternalProfile, ExternalProfileStore, AuthorizationEvidence, ExternalIdentity, ProfileRole } from "./contracts.ts";

function fixture(roles: ProfileRole[] = ["member"]) {
  const profile: ExternalProfile = {
    id:"11111111-1111-4111-8111-111111111111", issuer:"https://issuer.example", subject:"subject-1",
    email:"user@example.test", displayName:"Test User", roles, status:"ACTIVE",
    createdAt:"2026-01-01T00:00:00.000Z", updatedAt:"2026-01-01T00:00:00.000Z",
  };
  const evidence = new Map<string, AuthorizationEvidence>();
  const store: ExternalProfileStore = {
    async upsertIdentity(_identity: ExternalIdentity) { return profile; },
    async getProfile(id) { return id === profile.id ? profile : null; },
    async appendAuthorizationEvidence(e) { evidence.set(e.id,e); },
    async getAuthorizationEvidence(id) { return evidence.get(id) ?? null; },
    async setRoles(id, next) { if(id!==profile.id)return null; profile.roles=next; return profile; },
  };
  return {profile,store,evidence};
}
async function withServer(handler: ReturnType<typeof createExternalProfileServer>, run: (base:string)=>Promise<void>) {
  await new Promise<void>(resolve=>handler.listen(0,"127.0.0.1",resolve));
  const address=handler.address();
  if(!address || typeof address==="string") throw new Error("No test server address");
  try { await run(`http://127.0.0.1:${address.port}`); } finally { await new Promise<void>(resolve=>handler.close(()=>resolve())); }
}
const preview = {initiatedBySubject:"initiator-2",amountMinor:1250,currency:"USD",destinationRef:"synthetic-destination-001",network:"internal",expiresAt:"2030-01-01T00:00:00.000Z"};

test("external identity is required and profile endpoint returns server-side roles",async()=>{
 const {store}=fixture(["member"]);
 const server=createExternalProfileServer({store,verifier:{async verify(t){if(t!=="valid")throw Error("bad token");return{issuer:"https://issuer.example",subject:"subject-1"};}}});
 await withServer(server,async base=>{
  assert.equal((await fetch(base+"/v1/profiles/me")).status,401);
  const response=await fetch(base+"/v1/profiles/me",{headers:{authorization:"Bearer valid"}});
  assert.equal(response.status,200);
  const data=await response.json() as any;
  assert.deepEqual(data.profile.roles,["member"]);
 });
});

test("member cannot authorize and denial is recorded",async()=>{
 const {store,evidence}=fixture(["member"]);
 const server=createExternalProfileServer({store,verifier:{async verify(){return{issuer:"https://issuer.example",subject:"subject-1"};}},now:()=>new Date("2029-01-01T00:00:00.000Z")});
 await withServer(server,async base=>{
  const action="transfer.execute";
  const previewHash=hashTransactionPreview(action,preview);
  const response=await fetch(base+"/v1/authorization-decisions",{method:"POST",headers:{authorization:"Bearer valid","content-type":"application/json"},body:JSON.stringify({action,preview,previewHash})});
  assert.equal(response.status,403);
  assert.equal(evidence.size,1);
  assert.equal([...evidence.values()][0].decision,"DENY");
 });
});

test("approver can create preview-bound authorization evidence",async()=>{
 const {store,evidence}=fixture(["financial_approver"]);
 const server=createExternalProfileServer({store,verifier:{async verify(){return{issuer:"https://issuer.example",subject:"subject-1"};}},now:()=>new Date("2029-01-01T00:00:00.000Z")});
 await withServer(server,async base=>{
  const action="transfer.execute";
  const previewHash=hashTransactionPreview(action,preview);
  const response=await fetch(base+"/v1/authorization-decisions",{method:"POST",headers:{authorization:"Bearer valid","content-type":"application/json"},body:JSON.stringify({action,preview,previewHash})});
  assert.equal(response.status,201);
  assert.equal(evidence.size,1);
  assert.equal([...evidence.values()][0].decision,"ALLOW");
 });
});

test("tampered preview hash is rejected before evidence is written",async()=>{
 const {store,evidence}=fixture(["financial_approver"]);
 const server=createExternalProfileServer({store,verifier:{async verify(){return{issuer:"https://issuer.example",subject:"subject-1"};}}});
 await withServer(server,async base=>{
  const response=await fetch(base+"/v1/authorization-decisions",{method:"POST",headers:{authorization:"Bearer valid","content-type":"application/json"},body:JSON.stringify({action:"transfer.execute",preview,previewHash:"0".repeat(64)})});
  assert.equal(response.status,400);
  assert.equal(evidence.size,0);
 });
});

test("initiator cannot approve their own transaction",async()=>{
 const {store,evidence}=fixture(["financial_approver"]);
 const server=createExternalProfileServer({store,verifier:{async verify(){return{issuer:"https://issuer.example",subject:"subject-1"};}},now:()=>new Date("2029-01-01T00:00:00.000Z")});
 await withServer(server,async base=>{
  const selfPreview={...preview,initiatedBySubject:"subject-1"};
  const action="transfer.execute";
  const response=await fetch(base+"/v1/authorization-decisions",{method:"POST",headers:{authorization:"Bearer valid","content-type":"application/json"},body:JSON.stringify({action,preview:selfPreview,previewHash:hashTransactionPreview(action,selfPreview)})});
  assert.equal(response.status,403);
  assert.equal([...evidence.values()][0].reason,"SELF_APPROVAL_PROHIBITED");
 });
});
