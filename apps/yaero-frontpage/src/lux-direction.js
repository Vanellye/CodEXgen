/**
 * Ŷæṛö LUX — Interdimensional Direction Domain.
 * A symbolic navigation graph across declared semantic axes.
 * "Light" means traceable guidance/evidence, not physical faster-than-light travel.
 */
export const AXES = Object.freeze(["X", "Y", "Z", "T"]);
export const DIRECTIONS = Object.freeze(["OVER", "UNDER", "THROUGH"]);

function requireText(value, field) {
  if (typeof value !== "string" || !value.trim()) throw new TypeError(field + " must be a non-empty string.");
  return value.trim();
}

export function createBeacon({ id, label, axis, coordinate = null, evidenceRef, light = "UNVERIFIED" }) {
  id = requireText(id, "id");
  label = requireText(label, "label");
  evidenceRef = requireText(evidenceRef, "evidenceRef");
  if (!AXES.includes(axis)) throw new TypeError("axis must be X, Y, Z, or T.");
  if (!["VERIFIED", "PARTIAL", "UNVERIFIED"].includes(light)) throw new TypeError("light must be VERIFIED, PARTIAL, or UNVERIFIED.");
  return Object.freeze({ id, label, axis, coordinate, evidenceRef, light });
}

export function createPathEdge({ from, to, direction, evidenceRef, cost = 1 }) {
  from = requireText(from, "from");
  to = requireText(to, "to");
  evidenceRef = requireText(evidenceRef, "evidenceRef");
  if (from === to) throw new TypeError("Self-edges are not permitted.");
  if (!DIRECTIONS.includes(direction)) throw new TypeError("direction must be OVER, UNDER, or THROUGH.");
  if (!Number.isFinite(cost) || cost <= 0) throw new TypeError("cost must be a positive finite number.");
  return Object.freeze({ from, to, direction, evidenceRef, cost });
}

/** Find a minimum-cost path through explicitly supplied edges only. */
export function findLightPath({ beacons, edges, origin, destination, allowUnverified = false }) {
  const byId = new Map(beacons.map(beacon => [beacon.id, beacon]));
  if (!byId.has(origin) || !byId.has(destination)) {
    return { status: "UNKNOWN_DESTINATION", path: [], explanation: "Origin or destination beacon is not registered." };
  }
  if (!allowUnverified && (byId.get(origin).light === "UNVERIFIED" || byId.get(destination).light === "UNVERIFIED")) {
    return { status: "UNVERIFIED_ENDPOINT", path: [], explanation: "Endpoint evidence is unverified; confirm it or explicitly allow unverified navigation." };
  }
  const distance = new Map([[origin, 0]]);
  const previous = new Map();
  const remaining = new Set(byId.keys());
  while (remaining.size) {
    let current = null;
    for (const id of remaining) {
      if (distance.has(id) && (current === null || distance.get(id) < distance.get(current))) current = id;
    }
    if (current === null) break;
    if (current === destination) break;
    remaining.delete(current);
    for (const edge of edges) {
      if (edge.from !== current || !byId.has(edge.to) || !remaining.has(edge.to)) continue;
      if (!allowUnverified && byId.get(edge.to).light === "UNVERIFIED") continue;
      const nextDistance = distance.get(current) + edge.cost;
      if (!distance.has(edge.to) || nextDistance < distance.get(edge.to)) {
        distance.set(edge.to, nextDistance);
        previous.set(edge.to, { from: current, edge });
      }
    }
  }
  if (!distance.has(destination)) {
    return { status: "NO_EVIDENCED_PATH", path: [], explanation: "No connected route exists in the supplied evidence graph. No coordinates or transitions were invented." };
  }
  const path = [];
  let cursor = destination;
  while (cursor !== origin) {
    const item = previous.get(cursor);
    if (!item) return { status: "INTERNAL_PATH_ERROR", path: [] };
    path.unshift({ beacon: byId.get(cursor), via: item.edge });
    cursor = item.from;
  }
  path.unshift({ beacon: byId.get(origin), via: null });
  return {
    status: "PATH_FOUND",
    path,
    totalCost: distance.get(destination),
    light: path.every(step => step.beacon.light === "VERIFIED") ? "VERIFIED" : "PARTIAL",
    explanation: "Direction was computed only from declared beacons and evidence-linked edges."
  };
}

export function explainLightPath(result) {
  if (result.status !== "PATH_FOUND") return result.explanation;
  return result.path.map((step, index) => {
    const beacon = step.beacon;
    return (index + 1) + ". " + beacon.label + " (" + beacon.axis + " axis; " + beacon.light.toLowerCase() + " light)";
  }).join("\n") + "\nEvidence status: " + result.light.toLowerCase() + ".";
}
