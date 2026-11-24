/**
 * Ŷæṛö singular dimensional split (in2).
 * The source snapshot is preserved; projections are read-only and independently inspectable.
 */

const DIMENSIONS = ["identity", "relationship", "state", "time"];

export function splitIn2(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) {
    throw new TypeError("in2 expects a structured object.");
  }
  if (typeof input.sourceSnapshot !== "string" || !input.sourceSnapshot.length) {
    throw new TypeError("sourceSnapshot is required and must preserve the original input.");
  }
  if (typeof input.sourceRef !== "string" || !input.sourceRef.length) {
    throw new TypeError("sourceRef is required for provenance.");
  }
  const projections = {};
  for (const dimension of DIMENSIONS) {
    const supplied = Object.prototype.hasOwnProperty.call(input, dimension);
    const value = supplied ? input[dimension] : undefined;
    projections[dimension] = Object.freeze({
      dimension,
      value: value === undefined ? null : value,
      sourceRef: input.sourceRef,
      sourceSnapshot: input.sourceSnapshot,
      status: !supplied || value === null || value === undefined ? "UNKNOWN" : "PRESENT"
    });
  }
  return Object.freeze({
    operation: "in2",
    model: "singular-dimensional-projection/1",
    sourceRef: input.sourceRef,
    sourceSnapshot: input.sourceSnapshot,
    projections: Object.freeze(projections),
    navigation: Object.freeze({
      OVER: "whole-system context",
      UNDER: "nested, hidden, or residual material",
      THROUGH: "lineage and dependency paths"
    }),
    invariants: Object.freeze([
      "Original source snapshot is unchanged.",
      "Each projection contains one semantic dimension.",
      "Missing and null values remain UNKNOWN; they are not converted to zero.",
      "Every projection links to the original source reference."
    ])
  });
}

export function translateDimensionsToEnglish(split) {
  const labels = {
    identity: "what the subject is",
    relationship: "how the subject connects to other subjects",
    state: "what is established about the subject now",
    time: "when it applies or how it changes over time"
  };
  const lines = Object.entries(split.projections).map(([key, projection]) =>
    labels[key] + ": " + (projection.status === "UNKNOWN" ? "unknown (not supplied)" : JSON.stringify(projection.value))
  );
  return {
    literal: lines,
    interpretation: "This is a structured separation of one source into independent semantic views. It does not prove that the views are physically separate dimensions.",
    provenance: { sourceRef: split.sourceRef, sourcePreserved: true }
  };
}
