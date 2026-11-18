import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { createServer } from "./server.mjs";

const TOKEN = "test-token-".padEnd(40, "x");

async function withServer(run) {
  const dataDir = await mkdtemp(path.join(os.tmpdir(), "eria-wiki-drop-"));
  const server = await createServer({ dataDir, token: TOKEN });
  await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  const base = `http://127.0.0.1:${address.port}`;
  try { await run(base, dataDir); }
  finally {
    await new Promise(resolve => server.close(resolve));
    await rm(dataDir, { recursive: true, force: true });
  }
}

const auth = { authorization: `Bearer ${TOKEN}`, "content-type": "application/json" };

test("health is public and API routes require authentication", async () => {
  await withServer(async base => {
    const health = await fetch(base + "/health");
    assert.equal(health.status, 200);
    const denied = await fetch(base + "/api/links");
    assert.equal(denied.status, 401);
  });
});

test("creates, lists, and archives links without deleting provenance", async () => {
  await withServer(async (base, dataDir) => {
    const created = await fetch(base + "/api/links", {
      method: "POST", headers: auth,
      body: JSON.stringify({ title: "ERIA docs", url: "https://example.com/eria", category: "Architecture" })
    });
    assert.equal(created.status, 201);
    const { link } = await created.json();

    const listed = await fetch(base + "/api/links", { headers: auth });
    assert.equal((await listed.json()).links.length, 1);

    const archived = await fetch(base + "/api/links/" + link.id, { method: "DELETE", headers: auth });
    assert.equal(archived.status, 200);
    assert.equal((await archived.json()).recordRetainedInLedger, true);

    const after = await fetch(base + "/api/links", { headers: auth });
    assert.equal((await after.json()).links.length, 0);
    const ledger = (await readFile(path.join(dataDir, "events.jsonl"), "utf8")).trim().split("\n");
    assert.equal(ledger.length, 2);
    assert.match(ledger[0], /link.created/);
    assert.match(ledger[1], /link.archived/);
  });
});

test("rejects unsafe URL schemes and records authorization intent without enabling execution", async () => {
  await withServer(async base => {
    const unsafe = await fetch(base + "/api/links", {
      method: "POST", headers: auth,
      body: JSON.stringify({ title: "bad", url: "javascript:alert(1)" })
    });
    assert.equal(unsafe.status, 400);

    const intent = await fetch(base + "/api/authorization-intents", {
      method: "POST", headers: auth,
      body: JSON.stringify({ scope: "publish_wiki", confirmation: "publish_wiki", reason: "Reviewed request" })
    });
    assert.equal(intent.status, 201);
    assert.equal((await intent.json()).executionEnabled, false);

    const mismatch = await fetch(base + "/api/authorization-intents", {
      method: "POST", headers: auth,
      body: JSON.stringify({ scope: "background_dispatch", confirmation: "publish_wiki" })
    });
    assert.equal(mismatch.status, 403);
  });
});

test("refuses to start when the append-only ledger has been altered", async () => {
  const dataDir = await mkdtemp(path.join(os.tmpdir(), "eria-wiki-tamper-"));
  try {
    const server = await createServer({ dataDir, token: TOKEN });
    await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
    const base = `http://127.0.0.1:${server.address().port}`;
    await fetch(base + "/api/links", {
      method: "POST", headers: auth,
      body: JSON.stringify({ title: "one", url: "https://example.com" })
    });
    await new Promise(resolve => server.close(resolve));
    const file = path.join(dataDir, "events.jsonl");
    const contents = await readFile(file, "utf8");
    await (await import("node:fs/promises")).writeFile(file, contents.replace('"title":"one"', '"title":"two"'));
    await assert.rejects(() => createServer({ dataDir, token: TOKEN }), /integrity failure/);
  } finally {
    await rm(dataDir, { recursive: true, force: true });
  }
});
