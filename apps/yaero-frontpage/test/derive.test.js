import test from "node:test";
import assert from "node:assert/strict";

function validateScopes(source) {
  let depth = 0;
  for (const char of source) {
    if (char === "{") depth++;
    if (char === "}") depth--;
    if (depth < 0) throw new Error("Unexpected closing scope");
  }
  if (depth !== 0) throw new Error("Unclosed scope");
  return true;
}

test("accepts balanced scopes", () => {
  assert.equal(validateScopes("§x { △(a,b,c); }"), true);
});
test("rejects an unclosed scope", () => {
  assert.throws(() => validateScopes("§x { a → b;"), /Unclosed scope/);
});
test("rejects an extra closing scope", () => {
  assert.throws(() => validateScopes("}"), /Unexpected closing scope/);
});
