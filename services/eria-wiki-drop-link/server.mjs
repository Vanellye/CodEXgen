import { createHash, timingSafeEqual, randomUUID } from "node:crypto";
import { createServer as httpCreateServer } from "node:http";
import { appendFile, mkdir, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const GENESIS_HASH = "0".repeat(64);
const MAX_BODY_BYTES = 16 * 1024;
const CATEGORIES = new Set(["Reference", "Architecture", "Research", "Governance", "Implementation", "Other"]);
const INTENT_SCOPES = new Set(["publish_wiki", "background_dispatch"]);

function hashEntry(entry) {
  const { hash: _hash, ...unsigned } = entry;
  return createHash("sha256").update(JSON.stringify(unsigned)).digest("hex");
}

function json(res, status, body) {
  const data = JSON.stringify(body);
  res.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "content-length": Buffer.byteLength(data),
    "cache-control": "no-store",
    "x-content-type-options": "nosniff",
    "referrer-policy": "no-referrer"
  });
  res.end(data);
}

async function readBody(req) {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > MAX_BODY_BYTES) {
      const error = new Error("Request body is too large.");
      error.status = 413;
      throw error;
    }
    chunks.push(chunk);
  }
  try {
    return JSON.parse(Buffer.concat(chunks).toString("utf8"));
  } catch {
    const error = new Error("Request body must be valid JSON.");
    error.status = 400;
    throw error;
  }
}

function validText(value, max, required = false) {
  return typeof value === "string" && value.length <= max && (!required || value.trim().length > 0);
}

async function loadLedger(file) {
  let raw;
  try {
    raw = await readFile(file, "utf8");
  } catch (error) {
    if (error.code === "ENOENT") return [];
    throw error;
  }
  if (!raw.trim()) return [];
  const entries = [];
  let previousHash = GENESIS_HASH;
  for (const [index, line] of raw.trimEnd().split("\n").entries()) {
    let entry;
    try {
      entry = JSON.parse(line);
    } catch {
      throw new Error(`ERIA ledger integrity failure: invalid JSON on line ${index + 1}.`);
    }
    if (entry.seq !== index + 1 || entry.previousHash !== previousHash || entry.hash !== hashEntry(entry)) {
      throw new Error(`ERIA ledger integrity failure at sequence ${index + 1}; refusing to start.`);
    }
    previousHash = entry.hash;
    entries.push(entry);
  }
  return entries;
}

export async function createServer({ dataDir, token }) {
  if (!dataDir || typeof dataDir !== "string") throw new Error("dataDir is required.");
  if (!token || typeof token !== "string" || token.length < 32) {
    throw new Error("ERIA_API_TOKEN must contain at least 32 characters.");
  }

  const root = path.resolve(dataDir);
  await mkdir(root, { recursive: true, mode: 0o700 });
  const ledgerFile = path.join(root, "events.jsonl");
  const initial = await loadLedger(ledgerFile);
  let sequence = initial.length;
  let previousHash = initial.at(-1)?.hash ?? GENESIS_HASH;
  let writeQueue = Promise.resolve();

  async function append(type, payload) {
    const operation = writeQueue.then(async () => {
      const entry = {
        seq: sequence + 1,
        at: new Date().toISOString(),
        type,
        payload,
        previousHash
      };
      entry.hash = hashEntry(entry);
      await appendFile(ledgerFile, JSON.stringify(entry) + "\n", { encoding: "utf8", mode: 0o600 });
      sequence = entry.seq;
      previousHash = entry.hash;
      return entry;
    });
    writeQueue = operation.catch(() => {});
    return operation;
  }

  function authorized(req) {
    const header = req.headers.authorization ?? "";
    const supplied = header.startsWith("Bearer ") ? header.slice(7) : "";
    const a = Buffer.from(supplied);
    const b = Buffer.from(token);
    return a.length === b.length && timingSafeEqual(a, b);
  }

  function currentLinks() {
    const state = new Map();
    for (const entry of initial.concat(runtimeEntries)) {
      if (entry.type === "link.created") state.set(entry.payload.id, entry.payload);
      if (entry.type === "link.archived") state.delete(entry.payload.id);
    }
    return [...state.values()];
  }

  const runtimeEntries = [];
  const server = httpCreateServer(async (req, res) => {
    try {
      const url = new URL(req.url, "http://eria.local");
      if (req.method === "GET" && url.pathname === "/health") {
        return json(res, 200, { ok: true, service: "eria-wiki-drop-link", version: 1 });
      }
      if (!url.pathname.startsWith("/api/")) return json(res, 404, { error: "Not found." });
      if (!authorized(req)) return json(res, 401, { error: "Bearer token required." });

      if (req.method === "GET" && url.pathname === "/api/links") {
        const query = (url.searchParams.get("q") ?? "").trim().toLowerCase();
        const links = currentLinks().filter(link =>
          [link.title, link.url, link.category, link.description, link.source].join(" ").toLowerCase().includes(query)
        );
        return json(res, 200, { links });
      }

      if (req.method === "POST" && url.pathname === "/api/links") {
        const body = await readBody(req);
        if (!validText(body.title, 200, true)) return json(res, 400, { error: "title must be 1–200 characters." });
        if (!validText(body.url, 2048, true)) return json(res, 400, { error: "url must be 1–2048 characters." });
        let parsed;
        try { parsed = new URL(body.url); } catch { return json(res, 400, { error: "url must be valid." }); }
        if (!["http:", "https:"].includes(parsed.protocol)) return json(res, 400, { error: "Only HTTP and HTTPS URLs are accepted." });
        const category = body.category ?? "Other";
        if (!CATEGORIES.has(category)) return json(res, 400, { error: "Unsupported category." });
        if (!validText(body.description ?? "", 2000) || !validText(body.source ?? "", 500)) {
          return json(res, 400, { error: "description or source exceeds its allowed length." });
        }
        const link = {
          id: randomUUID(),
          url: parsed.href,
          title: body.title.trim(),
          category,
          description: (body.description ?? "").trim(),
          source: (body.source ?? "").trim(),
          createdAt: new Date().toISOString()
        };
        const entry = await append("link.created", link);
        runtimeEntries.push(entry);
        return json(res, 201, { link });
      }

      const archiveMatch = url.pathname.match(/^\/api\/links\/([0-9a-f-]{36})$/i);
      if (req.method === "DELETE" && archiveMatch) {
        const id = archiveMatch[1];
        if (!currentLinks().some(link => link.id === id)) return json(res, 404, { error: "Link not found." });
        const entry = await append("link.archived", { id });
        runtimeEntries.push(entry);
        return json(res, 200, { archived: true, id, recordRetainedInLedger: true });
      }

      if (req.method === "POST" && url.pathname === "/api/authorization-intents") {
        const body = await readBody(req);
        if (!INTENT_SCOPES.has(body.scope)) return json(res, 400, { error: "Unsupported authorization scope." });
        if (body.confirmation !== body.scope) return json(res, 403, { error: "Exact-scope confirmation required." });
        if (!validText(body.reason ?? "", 1000)) return json(res, 400, { error: "reason must be 0–1000 characters." });
        const intent = {
          id: randomUUID(),
          scope: body.scope,
          reason: (body.reason ?? "").trim(),
          recordedAt: new Date().toISOString(),
          executionEnabled: false
        };
        const entry = await append("authorization.intent", intent);
        runtimeEntries.push(entry);
        return json(res, 201, { intent, executionEnabled: false });
      }

      if (req.method === "GET" && url.pathname === "/api/audit") {
        await writeQueue;
        return json(res, 200, {
          integrity: "verified",
          entries: initial.concat(runtimeEntries)
        });
      }
      return json(res, 404, { error: "Not found." });
    } catch (error) {
      const status = Number.isInteger(error.status) ? error.status : 500;
      return json(res, status, { error: status === 500 ? "Internal service error." : error.message });
    }
  });

  return server;
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const port = Number(process.env.PORT ?? 8787);
  const dataDir = process.env.ERIA_DATA_DIR ?? "./data";
  const token = process.env.ERIA_API_TOKEN;
  const server = await createServer({ dataDir, token });
  server.listen(port, "0.0.0.0", () => {
    process.stdout.write(`ERIA Wiki Drop-Link API listening on port ${port}\n`);
  });
}
