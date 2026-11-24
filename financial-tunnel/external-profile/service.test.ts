import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { createExternalProfileServer, hashTransactionPreview } from "./service.ts";
import type { ExternalProfile, ExternalProfileStore, AuthorizationEvidence, CodeChangeDecision, CodeChangeProposal, ExternalIdentity, ProfileRole } from "./contracts.ts";

function fixture(roles: ProfileRole[] = ["member"]) {
  const profile: ExternalProfile = {
    id:"11111111-1111-4111-8111-111111111111", issuer:"https://issuer.example", subject:"subject-1",
    email:"user@example.test", displayName:"Test User", roles, status:"ACTIVE",
    createdAt:"2026-01-01T00:00:00.000Z", updatedAt:"2026-01-01T00:00:00.000Z",
  };
  const evidence = new Map<string, AuthorizationEvidence>();
  const proposals = new Map<string, CodeChangeProposal>();
  const decisions = new Map<string, CodeChangeDecision>();
  const adminProfile: ExternalProfile = { ...profile, id:"22222222-2222-4222-8222-222222222222", subject:"admin-2", roles:["profile_admin"] };
  const store: ExternalProfileStore = {
    async upsertIdentity(identity: ExternalIdentity) { return identity.subject === "admin-2" ? adminProfile : profile; },
    async getProfile(id) { return id === profile.id ? profile : null; },
    async appendAuthorizationEvidence(e) { evidence.set(e.id,e); },
    async getAuthorizationEvidence(id) { return evidence.get(id) ?? null; },
    async setRoles(id, next) { if(id!==profile.id)return null; profile.roles=next; return profile; },
    async createCodeChangeProposal(p) { proposals.set(p.id,p); },
    async getCodeChangeProposal(id) { return proposals.get(id) ?? null; },
    async decideCodeChangeProposal(d) { if(decisions.has(d.proposalId))return null; decisions.set(d.proposalId,d); return d; },
    async getCodeChangeDecision(id) { return decisions.get(id) ?? null; },
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


const codePatch = [
  "diff --git a/financial-tunnel/index.ts b/financial-tunnel/index.ts",
  "index 1111111..2222222 100644",
  "--- a/financial-tunnel/index.ts",
  "+++ b/financial-tunnel/index.ts",
  "@@ -1,1 +1,2 @@",
  " export {};",
  "+// ADMIN-reviewed code change test fixture",
].join("\n");
const codeProposalBody = {
  repository:"Vanellye/CodEXgen",
  branch:"feature/eria-financial-tunnel",
  baseSha:"a".repeat(40),
  files:["financial-tunnel/index.ts"],
  patch:codePatch,
};

test("code change proposals are stored pending independent ADMIN review",async()=>{
 const {store}=fixture(["member"]);
 const server=createExternalProfileServer({store,verifier:{async verify(){return{issuer:"https://issuer.example",subject:"subject-1"};}}});
 await withServer(server,async base=>{
  const response=await fetch(base+"/v1/code-change-proposals",{method:"POST",headers:{authorization:"Bearer valid","content-type":"application/json"},body:JSON.stringify(codeProposalBody)});
  assert.equal(response.status,201);
  const result=await response.json() as any;
  assert.equal(result.status,"PENDING_ADMIN_REVIEW");
  assert.equal(result.branch,"feature/eria-financial-tunnel");
  const read=await fetch(base+"/v1/code-change-proposals/"+result.proposalId,{headers:{authorization:"Bearer valid"}});
  assert.equal(read.status,200);
  assert.equal((await read.json() as any).status,"PENDING_ADMIN_REVIEW");
 });
});

test("only a distinct profile_admin may approve a code change proposal",async()=>{
 const {store}=fixture(["member"]);
 const verifier={async verify(token:string){return{issuer:"https://issuer.example",subject:token};}};
 const server=createExternalProfileServer({store,verifier});
 await withServer(server,async base=>{
  const created=await fetch(base+"/v1/code-change-proposals",{method:"POST",headers:{authorization:"Bearer subject-1","content-type":"application/json"},body:JSON.stringify(codeProposalBody)});
  const proposal=await created.json() as any;
  const memberDecision=await fetch(base+"/v1/code-change-proposals/"+proposal.proposalId+"/decision",{method:"POST",headers:{authorization:"Bearer subject-1","content-type":"application/json"},body:JSON.stringify({decision:"ALLOW",reason:"reviewed"})});
  assert.equal(memberDecision.status,403);
  const adminDecision=await fetch(base+"/v1/code-change-proposals/"+proposal.proposalId+"/decision",{method:"POST",headers:{authorization:"Bearer admin-2","content-type":"application/json"},body:JSON.stringify({decision:"ALLOW",reason:"Independent ADMIN review passed."})});
  assert.equal(adminDecision.status,201);
  assert.equal((await adminDecision.json() as any).status,"APPROVED_NOT_APPLIED");
  const duplicate=await fetch(base+"/v1/code-change-proposals/"+proposal.proposalId+"/decision",{method:"POST",headers:{authorization:"Bearer admin-2","content-type":"application/json"},body:JSON.stringify({decision:"ALLOW",reason:"duplicate"})});
  assert.equal(duplicate.status,409);
 });
});

test("code change self-approval and protected target branches are rejected",async()=>{
 const {store}=fixture(["member"]);
 const server=createExternalProfileServer({store,verifier:{async verify(token:string){return{issuer:"https://issuer.example",subject:token};}}});
 await withServer(server,async base=>{
  const invalid=await fetch(base+"/v1/code-change-proposals",{method:"POST",headers:{authorization:"Bearer subject-1","content-type":"application/json"},body:JSON.stringify({...codeProposalBody,branch:"main"})});
  assert.equal(invalid.status,400);
  const created=await fetch(base+"/v1/code-change-proposals",{method:"POST",headers:{authorization:"Bearer admin-2","content-type":"application/json"},body:JSON.stringify(codeProposalBody)});
  const proposal=await created.json() as any;
  const self=await fetch(base+"/v1/code-change-proposals/"+proposal.proposalId+"/decision",{method:"POST",headers:{authorization:"Bearer admin-2","content-type":"application/json"},body:JSON.stringify({decision:"ALLOW",reason:"self"})});
  assert.equal(self.status,403);
 });
});
