import { describe, expect, it } from "vitest";
import { parseDriveway } from "../src/dsl/parser.js";
const source = "project \"AshLedger\"\n\nledger \"primary\":\n    currency USD\n    mode double_entry\n    immutable true\n\naccount \"wallet\":\n    type asset\n    source ash_wallet\n    network avalanche\n\naccount \"rewards\":\n    type liability\n    unit POINT\n\nrule \"points_value\":\n    1 POINT = 1 USD\n    valuation_only true\n\nworkflow \"reconcile\":\n    read accounts\n    verify entries\n    check balances\n    require approval before posting\n";
describe("Driveway DSL", () => {
  it("parses the complete AshLedger declaration", () => {
    const s = parseDriveway(source);
    expect(s).toMatchObject({project:"AshLedger",ledger:"primary",currency:"USD",mode:"double_entry",immutable:true});
    expect(s.accounts).toEqual([
      {id:"wallet",type:"asset",source:"ash_wallet",network:"avalanche"},
      {id:"rewards",type:"liability",unit:"POINT"}
    ]);
    expect(s.rules[0]).toMatchObject({name:"points_value",expression:"1 POINT = 1 USD",valuationOnly:true});
    expect(s.workflows[0].steps).toEqual(["read accounts","verify entries","check balances","require approval before posting"]);
  });
  it("rejects the truncated requireles token", () => {
    expect(() => parseDriveway(source.replace("require approval before posting","requireles"))).toThrow(/incomplete approval/);
  });
  it("rejects malformed declarations", () => {
    expect(() => parseDriveway(source.replace('project "AshLedger"',"project AshLedger"))).toThrow(/unrecognized declaration/);
  });
});
