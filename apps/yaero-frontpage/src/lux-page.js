import { createBeacon, createPathEdge, findLightPath, explainLightPath } from "./lux-direction.js";

const beacons = [
  createBeacon({ id: "origin", label: "Origin", axis: "X", evidenceRef: "demo:origin", light: "VERIFIED" }),
  createBeacon({ id: "bridge", label: "Bridge", axis: "Y", evidenceRef: "demo:bridge", light: "VERIFIED" }),
  createBeacon({ id: "horizon", label: "Horizon", axis: "T", evidenceRef: "demo:horizon", light: "PARTIAL" })
];
const edges = [
  createPathEdge({ from: "origin", to: "bridge", direction: "THROUGH", evidenceRef: "demo:edge-1", cost: 1 }),
  createPathEdge({ from: "bridge", to: "horizon", direction: "OVER", evidenceRef: "demo:edge-2", cost: 2 })
];

document.querySelector("#find-path").addEventListener("click", () => {
  const origin = document.querySelector("#origin").value;
  const destination = document.querySelector("#destination").value;
  const result = findLightPath({ beacons, edges, origin, destination });
  document.querySelector("#lux-output").textContent = JSON.stringify({
    ...result,
    english: explainLightPath(result),
    note: "Demo graph only. Replace demo beacons and edges with verified project data before production."
  }, null, 2);
});
