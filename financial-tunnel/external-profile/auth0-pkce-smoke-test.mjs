#!/usr/bin/env node
/**
 * Local Auth0 Authorization Code + PKCE smoke test.
 *
 * The access token stays in process memory and is never printed or written.
 * Requires the external-profile API to be running locally and its PostgreSQL
 * schema to be provisioned before the final /v1/profiles/me request can pass.
 */
import { createServer } from "node:http";
import { createHash, randomBytes, timingSafeEqual } from "node:crypto";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const domain = (process.env.AUTH0_DOMAIN ?? "dev-ekleezvw1eidw3w4.us.auth0.com").replace(/^https?:\/\//, "").replace(/\/$/, "");
const clientId = process.env.AUTH0_CLIENT_ID ?? "8aBZEd7KvARDB7jecLL8NOIc3F61PBuF";
const audience = process.env.AUTH0_AUDIENCE ?? "https://eria-financial-tunnel-sandbox.example/api";
const redirectUri = process.env.AUTH0_REDIRECT_URI ?? "http://localhost:3000/callback";
const apiBase = (process.env.ERIA_API_BASE ?? "http://127.0.0.1:8787").replace(/\/$/, "");
const port = Number(new URL(redirectUri).port || 80);

const cliArgs = process.argv.slice(2);
function argValue(name) {
  const index = cliArgs.indexOf(name);
  return index >= 0 ? cliArgs[index + 1] : undefined;
}
const proposalArg = argValue("--proposal-id");
const proposalId = proposalArg;
const checkOnly = cliArgs.includes("--check");
const proposalFile = argValue("--proposal-file");
const approveId = argValue("--approve-proposal");
const showQueue = cliArgs.includes("--admin-queue");
const decision = argValue("--decision");
const reason = argValue("--reason");
const actions = [Boolean(proposalId), Boolean(proposalFile), Boolean(approveId), showQueue].filter(Boolean).length;
if (actions > 1) throw new Error("Choose one action: --proposal-file, --admin-queue, --approve-proposal, or --proposal-id.");
if (proposalId && !/^[0-9a-f-]{36}$/i.test(proposalId)) throw new Error("Invalid --proposal-id.");
if (approveId && !/^[0-9a-f-]{36}$/i.test(approveId)) throw new Error("Invalid --approve-proposal.");
if (checkOnly && !proposalId) throw new Error("--check requires --proposal-id.");
if (approveId && (!["ALLOW", "DENY"].includes(decision) || !reason || !reason.trim() || reason.length > 500)) {
  throw new Error("--approve-proposal requires --decision ALLOW|DENY and --reason (1-500 characters).");
}
let proposalPayload;
if (proposalFile) {
  try { proposalPayload = JSON.parse(readFileSync(proposalFile, "utf8")); }
  catch { throw new Error("Could not read --proposal-file as valid JSON."); }
}

if (!/^[A-Za-z0-9.-]+$/.test(domain) || !clientId || !audience) {
  throw new Error("Invalid Auth0 configuration.");
}
if (new URL(redirectUri).hostname !== "localhost" || new URL(redirectUri).pathname !== "/callback") {
  throw new Error("For this local smoke test, AUTH0_REDIRECT_URI must use http://localhost:<port>/callback.");
}

const verifier = randomBytes(32).toString("base64url");
const challenge = createHash("sha256").update(verifier).digest("base64url");
const state = randomBytes(24).toString("base64url");
const expectedState = Buffer.from(state);
const authorize = new URL(`https://${domain}/authorize`);
authorize.search = new URLSearchParams({
  response_type: "code",
  client_id: clientId,
  redirect_uri: redirectUri,
  audience,
  scope: "openid profile email",
  state,
  code_challenge: challenge,
  code_challenge_method: "S256",
}).toString();

let finished = false;
const server = createServer(async (req, res) => {
  const callback = new URL(req.url ?? "/", redirectUri);
  if (callback.pathname !== "/callback") {
    res.writeHead(404).end("Not found");
    return;
  }
  if (callback.searchParams.has("error")) {
    finished = true;
    res.writeHead(400, { "content-type": "text/plain" }).end("Auth0 login was not completed. You may close this tab.");
    process.stderr.write(`Auth0 returned: ${callback.searchParams.get("error")}\n`);
    server.close();
    return;
  }
  const returnedState = Buffer.from(callback.searchParams.get("state") ?? "");
  if (returnedState.length !== expectedState.length || !timingSafeEqual(returnedState, expectedState)) {
    res.writeHead(400, { "content-type": "text/plain" }).end("Invalid OAuth state. You may close this tab.");
    process.stderr.write("OAuth state validation failed.\n");
    return;
  }
  const code = callback.searchParams.get("code");
  if (!code) {
    res.writeHead(400, { "content-type": "text/plain" }).end("Missing authorization code.");
    return;
  }
  if (finished) return;
  finished = true;
  res.writeHead(200, { "content-type": "text/plain" }).end("ERIA sign-in received. You may close this tab and return to the terminal.");

  try {
    const tokenResponse = await fetch(`https://${domain}/oauth/token`, {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "authorization_code",
        client_id: clientId,
        code,
        redirect_uri: redirectUri,
        code_verifier: verifier,
      }),
    });
    const tokenBody = await tokenResponse.json();
    if (!tokenResponse.ok || typeof tokenBody.access_token !== "string") {
      throw new Error(`Token exchange failed (HTTP ${tokenResponse.status}): ${tokenBody.error ?? "unknown_error"} ${tokenBody.error_description ?? ""}`.trim());
    }

    const profileResponse = await fetch(`${apiBase}/v1/profiles/me`, {
      headers: { authorization: `Bearer ${tokenBody.access_token}`, accept: "application/json" },
    });
    const profileBody = await profileResponse.text();
    process.stdout.write(`GET /v1/profiles/me -> HTTP ${profileResponse.status}\n`);
    process.stdout.write(profileBody + "\n");
    if (!profileResponse.ok) process.exitCode = 1;

    if (profileResponse.ok && proposalPayload) {
      const submitted = await fetch(`${apiBase}/v1/code-change-proposals`, {
        method: "POST",
        headers: { authorization: `Bearer ${tokenBody.access_token}`, "content-type": "application/json", accept: "application/json" },
        body: JSON.stringify(proposalPayload),
      });
      const submittedBody = await submitted.text();
      process.stdout.write(`POST /v1/code-change-proposals -> HTTP ${submitted.status}\\n`);
      process.stdout.write(submittedBody + "\\n");
      if (!submitted.ok) process.exitCode = 1;
    }

    if (profileResponse.ok && showQueue) {
      const queue = await fetch(`${apiBase}/v1/admin/code-change-proposals`, {
        headers: { authorization: `Bearer ${tokenBody.access_token}`, accept: "application/json" },
      });
      process.stdout.write(`GET /v1/admin/code-change-proposals -> HTTP ${queue.status}\\n`);
      process.stdout.write(await queue.text() + "\\n");
      if (!queue.ok) process.exitCode = 1;
    }

    if (profileResponse.ok && approveId) {
      const reviewed = await fetch(`${apiBase}/v1/code-change-proposals/${approveId}/decision`, {
        method: "POST",
        headers: { authorization: `Bearer ${tokenBody.access_token}`, "content-type": "application/json", accept: "application/json" },
        body: JSON.stringify({ decision, reason: reason.trim() }),
      });
      process.stdout.write(`POST code-change decision -> HTTP ${reviewed.status}\\n`);
      process.stdout.write(await reviewed.text() + "\\n");
      if (!reviewed.ok) process.exitCode = 1;
    }

    if (profileResponse.ok && proposalId) {
      const writerPath = fileURLToPath(new URL("./apply-approved-code-change.mjs", import.meta.url));
      const writerArgs = [writerPath, proposalId, ...(checkOnly ? ["--check"] : [])];
      const applied = spawnSync(process.execPath, writerArgs, {
        encoding: "utf8",
        env: { ...process.env, ERIA_API_TOKEN: tokenBody.access_token, ERIA_API_BASE: apiBase },
      });
      if (applied.stdout) process.stdout.write(applied.stdout);
      if (applied.stderr) process.stderr.write(applied.stderr);
      if (applied.error) throw applied.error;
      if (applied.status !== 0) process.exitCode = applied.status ?? 1;
    }
  } catch (error) {
    process.stderr.write((error instanceof Error ? error.message : String(error)) + "\n");
    process.exitCode = 1;
  } finally {
    server.close();
  }
});

server.listen(port, "127.0.0.1", () => {
  process.stdout.write("ERIA Auth0 PKCE smoke test is listening locally.\n");
  process.stdout.write("Open this URL in your own browser to sign in (the access token will not be displayed):\n\n");
  process.stdout.write(authorize.toString() + "\n\n");
  process.stdout.write(`Callback: ${redirectUri}\nAPI: GET ${apiBase}/v1/profiles/me\n`);
});
