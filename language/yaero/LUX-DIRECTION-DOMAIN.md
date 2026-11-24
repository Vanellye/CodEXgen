# Ŷæṛö LUX — Interdimensional Direction Domain

## Identity

**LUX** is the light-guided direction domain within Ŷæṛö. It represents orientation, discoverability, evidence quality, and navigation through a declared multidimensional information model.

The term *interdimensional* refers to navigation across semantic axes and linked model spaces. It does not claim physical portals, faster-than-light travel, or access to scientifically unverified dimensions.

## Four axes

- **X — Identity:** what the subject or place is.
- **Y — Relation:** how it connects to other subjects or places.
- **Z — State:** its established condition or layer.
- **T — Time:** when it applies, or how it changes.

## Three direction operators

- **OVER:** move to a broader context or parent scope.
- **UNDER:** inspect a nested context, sublayer, or child scope.
- **THROUGH:** follow an evidence-linked relationship or transition.

## Light model

A beacon is a named, typed node with an axis, optional coordinate, evidence reference, and evidence status:

- `VERIFIED`: supported by the declared evidence.
- `PARTIAL`: some evidence exists, but the destination or relation remains incomplete.
- `UNVERIFIED`: not yet supported sufficiently for default navigation.

Light is a trust and orientation signal, not a physical energy measurement. Unverified endpoints and edges are excluded by default. A caller can explicitly permit unverified nodes for exploratory analysis, and the result must retain that uncertainty.

## Direction algorithm

The initial engine computes a minimum-cost route over a finite directed graph supplied by the caller. It does not invent coordinates, destinations, or edges. Each edge includes a direction operator and evidence reference. If no route exists, the engine returns `NO_EVIDENCED_PATH`.

## Provenance and safety

- Every beacon and edge requires an evidence reference.
- No source snapshot is mutated.
- No destination is guessed from a name alone.
- No automatic external action or repository write is authorized by a route result.
- Unknown remains unknown; partial evidence remains partial.
- Navigation output is descriptive and auditable.

## Public domain

The proposed public identity is `yaerolux.com`, intended as the entry point for the LUX direction domain. Availability and registration are separate: an availability check does not reserve a name. Registration requires explicit purchase approval and registrant contact information.
