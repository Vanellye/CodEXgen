import { describe, expect, it } from "vitest";
import { accountBalance, createLedger, postEntry } from "../src/core/ledger.js";
import { onePointOneDollar, valueUnits } from "../src/core/valuation.js";
import { parseDriveway } from "../src/dsl/parser.js";

const base = () => createLedger([
  { id:"cash", name:"Cash", kind:"asset", currency:"USD" },
  { id:"equity", name:"Opening equity", kind:"equity", currency:"USD" }
]);
const entry = { id:"e1", memo:"Opening balance", currency:"USD", source:"test", createdAt:"2026-01-01T00:00:00Z",
  lines:[{accountId:"cash",debitMinor:10000,creditMinor:0},{accountId:"equity",debitMinor:0,creditMinor:10000}] };
describe("Driveway ledger", () => {
  it("posts a balanced journal and computes account balance", () => {
    const ledger = postEntry(base(), entry);
    expect(accountBalance(ledger,"cash")).toBe(10000);
    expect(ledger.entries).toHaveLength(1);
  });
  it("rejects unbalanced entries", () => {
    expect(() => postEntry(base(), {...entry, lines:[...entry.lines.slice(0,1),{accountId:"equity",debitMinor:0,creditMinor:9000}]})).toThrow(/balanced/);
  });
  it("rejects duplicate entry IDs", () => {
    const once = postEntry(base(),entry);
    expect(() => postEntry(once,entry)).toThrow(/Duplicate/);
  });
  it("values points at the configured 1 point = 1 USD valuation", () => {
    expect(valueUnits(7,onePointOneDollar)).toBe(700);
    expect(onePointOneDollar.valuationOnly).toBe(true);
  });
  it("parses the Driveway DSL starter", () => {
    const spec = parseDriveway('project "Demo"\nledger "main":\n    currency USD\n    mode double_entry\n    immutable true');
    expect(spec.project).toBe("Demo");
    expect(spec.ledger).toBe("main");
  });
});
