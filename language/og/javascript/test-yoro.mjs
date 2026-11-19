import assert from "node:assert/strict";
import { encodeBytes, decodeBytes, validateVectors } from "./yoro-star-codec.mjs";
import { parse } from "./yoro-parser.mjs";
const vectors = new URL("../test-vectors/yoro-star-v2.tsv", import.meta.url);
console.log("JavaScript shared vectors passed:", validateVectors(vectors));
for (let n = 0; n < 256; n++) {
  const bytes = Uint8Array.of(n);
  assert.deepEqual([...decodeBytes(encodeBytes(bytes))], [n]);
}
assert.throws(() => decodeBytes("Ɣơ/2:kkkk"));
const ast = parse('§core { △(☆, k, ∞); "hello" → ∴ result; }');
assert.equal(ast.type, "Program");
assert.equal(ast.body[0].type, "Scope");
assert.equal(ast.body[0].body[0].type, "Triad");
console.log("JavaScript parser smoke tests passed");
