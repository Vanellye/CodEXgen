import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

const schema = JSON.parse(fs.readFileSync(new URL("../knowledge-graph.schema.json", import.meta.url)));
const fixture = JSON.parse(fs.readFileSync(new URL("../fixtures/knowledge-graph.valid.json", import.meta.url)));
const ajv = new Ajv2020({ allErrors: true, strict: true });
addFormats(ajv);
const validate = ajv.compile(schema);

test("canonical fixture conforms to the shared graph schema", () => {
  assert.equal(validate(fixture), true, JSON.stringify(validate.errors));
});

test("event sequence is unique, contiguous, and append ordered", () => {
  const sequences = fixture.events.map(event => event.sequence);
  assert.deepEqual(sequences, [1, 2, 3, 4]);
  assert.equal(new Set(sequences).size, sequences.length);
  assert.equal(new Set(fixture.events.map(event => event.eventId)).size, fixture.events.length);
});

test("edge endpoints resolve to nodes introduced earlier in the event stream", () => {
  const nodes = new Set();
  for (const event of fixture.events) {
    if (event.type === "node.created") nodes.add(event.node.id);
    if (event.type === "edge.created") {
      assert.ok(nodes.has(event.edge.fromNodeId));
      assert.ok(nodes.has(event.edge.toNodeId));
    }
  }
});

test("supersession appends a correction and retains the original record", () => {
  const original = fixture.events.find(event => event.type === "node.created" && event.node.id === "node.evidence");
  const correction = fixture.events.find(event => event.type === "node.superseded");
  assert.ok(original);
  assert.equal(correction.subjectId, original.node.id);
  assert.notEqual(correction.replacementId, original.node.id);
  assert.equal(original.node.label, "Evidence record");
});

test("schema rejects missing provenance and mutable update fields", () => {
  const invalid = structuredClone(fixture);
  delete invalid.events[0].node.source;
  assert.equal(validate(invalid), false);
  const mutable = structuredClone(fixture);
  mutable.events[0].node.updatedAt = "2026-11-15T12:04:00Z";
  assert.equal(validate(mutable), false);
});
