import test from "node:test";
import assert from "node:assert/strict";
import { createBeacon, createPathEdge, findLightPath, explainLightPath } from "../src/lux-direction.js";

const beacons = [
  createBeacon({ id: "origin", label: "Origin", axis: "X", evidenceRef: "evidence:origin", light: "VERIFIED" }),
  createBeacon({ id: "bridge", label: "Bridge", axis: "Y", evidenceRef: "evidence:bridge", light: "VERIFIED" }),
  createBeacon({ id: "horizon", label: "Horizon", axis: "T", evidenceRef: "evidence:horizon", light: "PARTIAL" })
];
const edges = [
  createPathEdge({ from: "origin", to: "bridge", direction: "THROUGH", evidenceRef: "edge:1", cost: 2 }),
  createPathEdge({ from: "bridge", to: "horizon", direction: "OVER", evidenceRef: "edge:2", cost: 1 })
];

test("finds a minimum-cost evidence-linked direction", () => {
  const result = findLightPath({ beacons, edges, origin: "origin", destination: "horizon" });
  assert.equal(result.status, "PATH_FOUND");
  assert.equal(result.totalCost, 3);
  assert.equal(result.light, "PARTIAL");
  assert.match(explainLightPath(result), /Horizon/);
});

test("does not invent paths to unknown destinations", () => {
  const result = findLightPath({ beacons, edges, origin: "origin", destination: "void" });
  assert.equal(result.status, "UNKNOWN_DESTINATION");
});

test("blocks unverified endpoints by default", () => {
  const uncertain = createBeacon({ id: "unknown", label: "Unknown", axis: "Z", evidenceRef: "evidence:unknown" });
  const result = findLightPath({ beacons: [...beacons, uncertain], edges, origin: "origin", destination: "unknown" });
  assert.equal(result.status, "UNVERIFIED_ENDPOINT");
});

test("does not traverse unverified intermediate beacons by default", () => {
  const unverified = createBeacon({ id: "dark", label: "Dark node", axis: "Z", evidenceRef: "evidence:dark" });
  const result = findLightPath({
    beacons: [...beacons, unverified],
    edges: [createPathEdge({ from: "origin", to: "dark", direction: "UNDER", evidenceRef: "edge:dark" }), createPathEdge({ from: "dark", to: "horizon", direction: "THROUGH", evidenceRef: "edge:exit" })],
    origin: "origin", destination: "horizon"
  });
  assert.equal(result.status, "NO_EVIDENCED_PATH");
});

test("rejects unsupported axis and invalid direction", () => {
  assert.throws(() => createBeacon({ id: "bad", label: "Bad", axis: "Q", evidenceRef: "x" }), /axis/);
  assert.throws(() => createPathEdge({ from: "a", to: "b", direction: "TELEPORT", evidenceRef: "x" }), /direction/);
});
