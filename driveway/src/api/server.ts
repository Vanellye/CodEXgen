import { createServer } from "node:http";
import { createLedger } from "../core/ledger.js";
import { onePointOneDollar, valueUnits } from "../core/valuation.js";
import { parseDriveway } from "../dsl/parser.js";

const server = createServer(async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "http://localhost:5173");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") { res.writeHead(204).end(); return; }
  const send = (status: number, body: unknown) => { res.writeHead(status, { "content-type": "application/json" }); res.end(JSON.stringify(body)); };
  if (req.url === "/health") return send(200, { ok: true, service: "driveway-api", mode: "starter" });
  if (req.url === "/api/demo") return send(200, {
    ledger: "AshLedger demo", journalEntries: 0, mode: "read-only preview",
    pointValuation: { rate: "1 POINT = 1 USD", valuationOnly: true }
  });
  if (req.url === "/api/valuation" && req.method === "POST") {
    let body = ""; for await (const chunk of req) body += chunk;
    try {
      const input = JSON.parse(body) as { points: number };
      const cents = valueUnits(input.points, onePointOneDollar);
      return send(200, { points: input.points, currency: "USD", amount: cents / 100, valuationOnly: true });
    } catch (error) { return send(400, { error: error instanceof Error ? error.message : "Invalid request" }); }
  }
  if (req.url === "/api/parse" && req.method === "POST") {
    let body = ""; for await (const chunk of req) body += chunk;
    try { return send(200, parseDriveway(JSON.parse(body).source)); }
    catch (error) { return send(400, { error: error instanceof Error ? error.message : "Parse failed" }); }
  }
  return send(404, { error: "Not found" });
});
createLedger();
server.listen(8787, "0.0.0.0", () => console.log("Driveway API listening on :8787"));
