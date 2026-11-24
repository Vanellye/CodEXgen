import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { createHash, randomUUID, timingSafeEqual } from "node:crypto";
import type {
  AuthorizationEvidence, CodeChangeDecision, CodeChangeProposal, ExternalIdentity, ExternalProfileStore, ProfileRole, TransactionPreview,
} from "./contracts.ts";
import { createOidcVerifier, type OidcVerifier } from "./oidc.ts";
import { Pool } from "pg";
import { PostgresExternalProfileStore } from "./pg-store.ts";

const POLICY_VERSION = "external-profile-policy/1.0.0";
const ALLOWED_ACTIONS = new Set(["transfer.execute", "payment.create", "wallet.withdraw"]);
const ROLE_SET = new Set<ProfileRole>(["member", "financial_approver", "profile_admin"]);
const CODE_REPOSITORY = "Vanellye/CodEXgen" as const;
const CODE_BRANCH = "feature/eria-financial-tunnel" as const;
const MAX_CODE_PATCH_BYTES = 128 * 1024;

function validCodePath(path: unknown): path is string {
  if (typeof path !== "string" || path.length > 240 || !/^(financial-tunnel|financial)\/[A-Za-z0-9._\/-]+$/.test(path)) return false;
  const parts = path.split("/");
  if (parts.some((part) => !part || part === "." || part === "..")) return false;
  if (/(^|\/)(\.env(?:\.|$)|\.git|secrets?)(\/|$)/i.test(path)) return false;
  return true;
}

function validateCodePatch(input: any): { files: string[]; patch: string; patchSha256: string; baseSha: string } | null {
  if (input.repository !== CODE_REPOSITORY || input.branch !== CODE_BRANCH ||
      typeof input.baseSha !== "string" || !/^[0-9a-f]{40}$/i.test(input.baseSha) ||
      typeof input.patch !== "string" || !input.patch.length ||
      Buffer.byteLength(input.patch, "utf8") > MAX_CODE_PATCH_BYTES ||
      !Array.isArray(input.files) || input.files.length < 1 || input.files.length > 20) return null;
  const files = [...new Set(input.files)];
  if (files.length !== input.files.length || !files.every(validCodePath)) return null;
  if (input.patch.includes("GIT binary patch") || /^rename (from|to) /m.test(input.patch) ||
      /^(new|old) file mode (120000|160000)$/m.test(input.patch) ||
      /^\\+\\+\\+ \\/dev\\/null$/m.test(input.patch)) return null;
  const headers = [...input.patch.matchAll(/^diff --git a\\/([^\\n]+) b\\/([^\\n]+)$/gm)];
  if (!headers.length) return null;
  const patchFiles = headers.map((m) => m[1]);
  const contentHeaders = [...input.patch.matchAll(/^(---|\\+\\+\\+) (?:([ab]\\/[^\\n]+)|(\\/dev\\/null))$/gm)];
  if (headers.some((m) => m[1] !== m[2] || !validCodePath(m[1])) ||
      patchFiles.length !== files.length || new Set(patchFiles).size !== files.length || patchFiles.some((p) => !files.includes(p)) ||
      contentHeaders.length !== headers.length * 2 ||
      contentHeaders.some((m) => m[1] === "+++" ? !m[2] || !validCodePath(m[2].slice(2)) || !files.includes(m[2].slice(2)) :
        (m[3] !== "/dev/null" && (!m[2] || !validCodePath(m[2].slice(2)) || !files.includes(m[2].slice(2)))))) return null;
  return {
    files, patch: input.patch, baseSha: input.baseSha,
    patchSha256: createHash("sha256").update(input.patch, "utf8").digest("hex"),
  };
}

export function hashTransactionPreview(action: string, preview: TransactionPreview): string {
  const canonical = JSON.stringify({
    action, initiatedBySubject: preview.initiatedBySubject, amountMinor: preview.amountMinor, currency: preview.currency.toUpperCase(),
    destinationRef: preview.destinationRef, network: preview.network ?? "",
    expiresAt: new Date(preview.expiresAt).toISOString(),
  });
  return createHash("sha256").update(canonical).digest("hex");
}

function send(res: ServerResponse, status: number, body: unknown): void {
  res.writeHead(status, { "content-type": "application/json", "cache-control": "no-store" });
  res.end(JSON.stringify(body));
}
async function bodyJson(req: IncomingMessage): Promise<any> {
  let raw = "";
  for await (const chunk of req) {
    raw += chunk.toString();
    if (raw.length > 160_000) throw new Error("Request body too large.");
  }
  return raw ? JSON.parse(raw) : {};
}
function bearer(req: IncomingMessage): string | null {
  const value = req.headers.authorization;
  return typeof value === "string" && value.startsWith("Bearer ") ? value.slice(7) : null;
}
function safeEqual(a: string, b: string): boolean {
  const aa = Buffer.from(a), bb = Buffer.from(b);
  return aa.length === bb.length && timingSafeEqual(aa, bb);
}

export function createExternalProfileServer(deps: {
  store: ExternalProfileStore;
  verifier: OidcVerifier;
  now?: () => Date;
}) {
  const now = deps.now ?? (() => new Date());
  return createServer(async (req, res) => {
    try {
      const url = new URL(req.url ?? "/", "http://localhost");
      if (req.method === "GET" && url.pathname === "/healthz") return send(res, 200, { status: "ok", service: "external-profile", mode: "API_ONLY_NO_EXECUTION" });
      const token = bearer(req);
      if (!token) return send(res, 401, { error: "BEARER_TOKEN_REQUIRED" });
      let identity: ExternalIdentity;
      try { identity = await deps.verifier.verify(token); }
      catch { return send(res, 401, { error: "INVALID_EXTERNAL_IDENTITY" }); }
      const profile = await deps.store.upsertIdentity(identity);
      if (profile.status !== "ACTIVE") return send(res, 403, { error: "PROFILE_SUSPENDED" });

      if (req.method === "GET" && url.pathname === "/v1/profiles/me") {
        return send(res, 200, { profile });
      }

      if (req.method === "GET" && url.pathname === "/v1/admin/code-change-proposals") {
        if (!profile.roles.includes("profile_admin")) return send(res, 403, { error: "PROFILE_ADMIN_REQUIRED" });
        const proposals = await deps.store.listCodeChangeProposals();
        const queue = await Promise.all(proposals.map(async (proposal) => {
          const decision = await deps.store.getCodeChangeDecision(proposal.id);
          return {
            proposalId: proposal.id, proposerSubject: proposal.proposerSubject,
            repository: proposal.repository, branch: proposal.branch, baseSha: proposal.baseSha,
            files: proposal.files, patchSha256: proposal.patchSha256, createdAt: proposal.createdAt,
            decision: decision?.decision ?? null,
            status: decision ? (decision.decision === "ALLOW" ? "APPROVED_NOT_APPLIED" : "REJECTED") : "PENDING_ADMIN_REVIEW",
          };
        }));
        return send(res, 200, { proposals: queue });
      }

      // Any active profile may submit a proposal; only a different profile_admin may decide it.
      if (req.method === "POST" && url.pathname === "/v1/code-change-proposals") {
        const input = await bodyJson(req);
        const validated = validateCodePatch(input);
        if (!validated) return send(res, 400, { error: "INVALID_CODE_CHANGE_PROPOSAL" });
        const proposal: CodeChangeProposal = {
          id: randomUUID(), proposerProfileId: profile.id, proposerSubject: identity.subject,
          repository: CODE_REPOSITORY, branch: CODE_BRANCH, baseSha: validated.baseSha,
          files: validated.files, patch: validated.patch, patchSha256: validated.patchSha256,
          createdAt: now().toISOString(),
        };
        await deps.store.createCodeChangeProposal(proposal);
        return send(res, 201, {
          proposalId: proposal.id, repository: proposal.repository, branch: proposal.branch,
          baseSha: proposal.baseSha, files: proposal.files, patchSha256: proposal.patchSha256,
          status: "PENDING_ADMIN_REVIEW", createdAt: proposal.createdAt,
        });
      }

      const codeProposalMatch = url.pathname.match(/^\/v1\/code-change-proposals\/([0-9a-f-]{36})(?:\/(decision))?$/i);
      if (codeProposalMatch && req.method === "GET" && !codeProposalMatch[2]) {
        const proposal = await deps.store.getCodeChangeProposal(codeProposalMatch[1]);
        if (!proposal) return send(res, 404, { error: "CODE_CHANGE_PROPOSAL_NOT_FOUND" });
        if (proposal.proposerProfileId !== profile.id && !profile.roles.includes("profile_admin")) {
          return send(res, 403, { error: "CODE_CHANGE_PROPOSAL_ACCESS_DENIED" });
        }
        const decision = await deps.store.getCodeChangeDecision(proposal.id);
        return send(res, 200, { proposal, decision, status: decision ? (decision.decision === "ALLOW" ? "APPROVED_NOT_APPLIED" : "REJECTED") : "PENDING_ADMIN_REVIEW" });
      }

      if (codeProposalMatch && req.method === "POST" && codeProposalMatch[2] === "decision") {
        if (!profile.roles.includes("profile_admin")) return send(res, 403, { error: "PROFILE_ADMIN_REQUIRED" });
        const proposal = await deps.store.getCodeChangeProposal(codeProposalMatch[1]);
        if (!proposal) return send(res, 404, { error: "CODE_CHANGE_PROPOSAL_NOT_FOUND" });
        if (proposal.proposerProfileId === profile.id || proposal.proposerSubject === identity.subject) {
          return send(res, 403, { error: "CODE_CHANGE_SELF_APPROVAL_PROHIBITED" });
        }
        const input = await bodyJson(req);
        if ((input.decision !== "ALLOW" && input.decision !== "DENY") ||
            typeof input.reason !== "string" || !input.reason.trim() || input.reason.trim().length > 500) {
          return send(res, 400, { error: "INVALID_CODE_CHANGE_DECISION" });
        }
        const decision: CodeChangeDecision = {
          id: randomUUID(), proposalId: proposal.id, approverProfileId: profile.id,
          approverSubject: identity.subject, decision: input.decision,
          reason: input.reason.trim(), createdAt: now().toISOString(),
        };
        const saved = await deps.store.decideCodeChangeProposal(decision);
        if (!saved) return send(res, 409, { error: "CODE_CHANGE_ALREADY_DECIDED" });
        return send(res, 201, {
          proposalId: saved.proposalId, decision: saved.decision, decisionId: saved.id,
          approvedFor: saved.decision === "ALLOW" ? proposal.branch : null,
          status: saved.decision === "ALLOW" ? "APPROVED_NOT_APPLIED" : "REJECTED",
        });
      }


      if (req.method === "POST" && url.pathname === "/v1/authorization-decisions") {
        const input = await bodyJson(req);
        const action = input.action;
        const p = input.preview as TransactionPreview | undefined;
        if (typeof action !== "string" || !ALLOWED_ACTIONS.has(action) || !p ||
            typeof p.initiatedBySubject !== "string" || p.initiatedBySubject.length < 1 || p.initiatedBySubject.length > 200 ||
            !Number.isSafeInteger(p.amountMinor) || p.amountMinor <= 0 ||
            typeof p.currency !== "string" || !/^[A-Za-z]{3}$/.test(p.currency) ||
            typeof p.destinationRef !== "string" || p.destinationRef.length < 3 || p.destinationRef.length > 200 ||
            typeof p.expiresAt !== "string" || !Number.isFinite(Date.parse(p.expiresAt)) ||
            (p.network !== undefined && (typeof p.network !== "string" || p.network.length > 80))) {
          return send(res, 400, { error: "INVALID_TRANSACTION_PREVIEW" });
        }
        const expectedHash = hashTransactionPreview(action, p);
        if (typeof input.previewHash !== "string" || !/^[a-f0-9]{64}$/.test(input.previewHash) || !safeEqual(expectedHash, input.previewHash)) {
          return send(res, 400, { error: "PREVIEW_HASH_MISMATCH" });
        }
        const isApprover = profile.roles.includes("financial_approver") || profile.roles.includes("profile_admin");
        const notExpired = Date.parse(p.expiresAt) > now().getTime();
        const differentActor = identity.subject !== p.initiatedBySubject;
        const allowed = isApprover && notExpired && differentActor;
        const evidence: AuthorizationEvidence = {
          id: randomUUID(), profileId: profile.id, actorSubject: identity.subject, action,
          preview: { ...p, currency: p.currency.toUpperCase() }, previewHash: expectedHash,
          decision: allowed ? "ALLOW" : "DENY",
          reason: allowed ? "INDEPENDENT_APPROVER_AND_FRESH_PREVIEW" : (!differentActor ? "SELF_APPROVAL_PROHIBITED" : (!notExpired ? "PREVIEW_EXPIRED" : "APPROVER_ROLE_REQUIRED")),
          policyVersion: POLICY_VERSION, createdAt: now().toISOString(),
        };
        await deps.store.appendAuthorizationEvidence(evidence);
        return send(res, allowed ? 201 : 403, { decision: evidence.decision, evidenceId: evidence.id, previewHash: evidence.previewHash, policyVersion: evidence.policyVersion });
      }

      const evidenceMatch = url.pathname.match(/^\/v1\/authorization-decisions\/([0-9a-f-]{36})$/i);
      if (req.method === "GET" && evidenceMatch) {
        const evidence = await deps.store.getAuthorizationEvidence(evidenceMatch[1]);
        if (!evidence) return send(res, 404, { error: "EVIDENCE_NOT_FOUND" });
        if (evidence.profileId !== profile.id && !profile.roles.includes("profile_admin")) return send(res, 403, { error: "EVIDENCE_ACCESS_DENIED" });
        return send(res, 200, { evidence });
      }

      const rolesMatch = url.pathname.match(/^\/v1\/admin\/profiles\/([0-9a-f-]{36})\/roles$/i);
      if (req.method === "PUT" && rolesMatch) {
        if (!profile.roles.includes("profile_admin")) return send(res, 403, { error: "PROFILE_ADMIN_REQUIRED" });
        const input = await bodyJson(req);
        if (!Array.isArray(input.roles) || input.roles.length === 0 || input.roles.some((r: unknown) => typeof r !== "string" || !ROLE_SET.has(r as ProfileRole))) {
          return send(res, 400, { error: "INVALID_ROLE_SET" });
        }
        const updated = await deps.store.setRoles(rolesMatch[1], [...new Set(input.roles)] as ProfileRole[], identity.subject);
        return updated ? send(res, 200, { profile: updated }) : send(res, 404, { error: "PROFILE_NOT_FOUND" });
      }
      return send(res, 404, { error: "NOT_FOUND" });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Internal error";
      return send(res, message === "Request body too large." ? 413 : 400, { error: message });
    }
  });
}

export async function startExternalProfileApi(): Promise<void> {
  const pool = new Pool({ connectionString: process.env.DATABASE_URL, ssl: process.env.DATABASE_SSL === "true" ? { rejectUnauthorized: true } : undefined });
  const store = new PostgresExternalProfileStore(pool);
  const verifier = createOidcVerifier();
  const port = Number(process.env.EXTERNAL_PROFILE_PORT ?? 8787);
  const host = process.env.EXTERNAL_PROFILE_HOST ?? "127.0.0.1";
  const server = createExternalProfileServer({ store, verifier });
  server.listen(port, host, () => process.stdout.write(`external-profile API listening on http://${host}:${port}\n`));
  const close = () => server.close(() => { void pool.end(); });
  process.on("SIGINT", close);
  process.on("SIGTERM", close);
}

if (process.argv[1] && import.meta.url === new URL(`file://${process.argv[1]}`).href) {
  startExternalProfileApi().catch((error) => { process.stderr.write(String(error) + "\n"); process.exitCode = 1; });
}
