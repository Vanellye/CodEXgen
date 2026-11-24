import test from "node:test";
import assert from "node:assert/strict";
import { decodeCurrencyRecord, renderCurrencyEnglish, interpretCurrencyIntent } from "../src/semantics/currency.js";
import { splitIn2, translateDimensionsToEnglish } from "../src/semantics/dimensional-in2.js";

test("decodes exact USD minor units and translates to English", () => {
  const source = JSON.stringify({ schema: "yaero.currency/1", currency: "USD", minorUnits: "12345", exponent: 2, sourceRef: "fixture:usd-1" });
  const decoded = decodeCurrencyRecord(source);
  assert.equal(decoded.status, "DECODED");
  assert.equal(decoded.minorUnits, "12345");
  assert.equal(decoded.sourceSnapshot, source);
  assert.equal(renderCurrencyEnglish(decoded).english, "one hundred twenty-three dollars and forty-five cents");
});

test("supports zero-decimal KRW without fabricating fractional units", () => {
  const decoded = decodeCurrencyRecord({ schema: "yaero.currency/1", currency: "KRW", minorUnits: "5000", exponent: 0 });
  assert.equal(renderCurrencyEnglish(decoded).english, "five thousand won");
});

test("unknown currency remains unknown, never zero", () => {
  const decoded = decodeCurrencyRecord({ schema: "yaero.currency/1", currency: "XYZ", minorUnits: "0" });
  assert.equal(decoded.status, "UNKNOWN_CURRENCY");
  assert.equal(decoded.minorUnits, "0");
});

test("does not infer transaction purpose from amount", () => {
  const decoded = decodeCurrencyRecord({ schema: "yaero.currency/1", currency: "EUR", minorUnits: "250", exponent: 2 });
  assert.equal(interpretCurrencyIntent(decoded).label, "UNKNOWN");
  assert.equal(interpretCurrencyIntent(decoded, { action: "payment" }).label, "PAYMENT");
});

test("in2 creates independent, provenance-linked projections", () => {
  const sourceSnapshot = '{"identity":"invoice-7","relationship":{"to":"vendor-2"},"state":"unpaid","time":null}';
  const split = splitIn2({ sourceRef: "fixture:invoice-7", sourceSnapshot, identity: "invoice-7", relationship: { to: "vendor-2" }, state: "unpaid", time: null });
  assert.equal(split.sourceSnapshot, sourceSnapshot);
  assert.equal(split.projections.identity.value, "invoice-7");
  assert.equal(split.projections.time.status, "UNKNOWN");
  assert.equal(split.projections.state.sourceRef, "fixture:invoice-7");
  assert.equal(translateDimensionsToEnglish(split).provenance.sourcePreserved, true);
});

test("in2 rejects inputs without source provenance", () => {
  assert.throws(() => splitIn2({ sourceSnapshot: "{}", identity: "x" }), /sourceRef/);
});

test("in2 exposes omitted axes as UNKNOWN rather than dropping them", () => {
  const split = splitIn2({ sourceRef: "fixture:minimal", sourceSnapshot: "{}", identity: "one" });
  assert.equal(split.projections.identity.status, "PRESENT");
  assert.equal(split.projections.relationship.status, "UNKNOWN");
  assert.equal(split.projections.state.status, "UNKNOWN");
  assert.equal(split.projections.time.status, "UNKNOWN");
});
