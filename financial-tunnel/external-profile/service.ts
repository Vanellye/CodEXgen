import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { createHash, randomUUID, timingSafeEqual } from "node:crypto";
import type {
  AuthorizationEvidence, ExternalIdentity, ExternalProfileStore, ProfileRole, TransactionPreview,
} from "./contracts.ts";
import { createOidcVerifier, type OidcVerifier } from "./oidc.ts";
import { Pool } from "pg";
import { PostgresExternalProfileStore } from "./pg-store.ts";

const POLICY_VERSION = "external-profile-policy/1.0.0";
const ALLOWED_ACTIONS = new Set(["transfer.execute", "payment.create", "wallet.withdraw"]);
const ROLE_SET = new Set<ProfileRole>(["member", "financial_approver", "profile_admin"]);

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
    if (raw.length > 16_384) throw new Error("Request body too large.");
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
