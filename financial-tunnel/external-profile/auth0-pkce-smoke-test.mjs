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

const domain = (process.env.AUTH0_DOMAIN ?? "dev-ekleezvw1eidw3w4.us.auth0.com").replace(/^https?:\/\//, "").replace(/\/$/, "");
const clientId = process.env.AUTH0_CLIENT_ID ?? "8aBZEd7KvARDB7jecLL8NOIc3F61PBuF";
const audience = process.env.AUTH0_AUDIENCE ?? "https://eria-financial-tunnel-sandbox.example/api";
const redirectUri = process.env.AUTH0_REDIRECT_URI ?? "http://localhost:3000/callback";
const apiBase = (process.env.ERIA_API_BASE ?? "http://127.0.0.1:8787").replace(/\/$/, "");
const port = Number(new URL(redirectUri).port || 80);

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
