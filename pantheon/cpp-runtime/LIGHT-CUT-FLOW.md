# Light Cut — Directional Flow Routing

## Intent

Light Cut is a bounded, declarative routing operation for directing a numeric data-flow packet across explicitly named destinations. "Light" means transparent and inspectable; "cut" means partition, not deletion or concealment.

## Contract

- Preserve the packet's source identity in every routed segment.
- Require finite, nonnegative input amounts.
- Require unique, nonempty destinations.
- Require finite, nonnegative route weights whose sum is 1 within a fixed tolerance.
- Preserve total flow: routed segment amounts sum to the input amount within floating-point tolerance.
- Reject invalid routing plans rather than silently dropping, duplicating, or amplifying flow.
- Produce a routing plan only. It does not open sockets, read devices, mutate an external stream, or execute downstream actions.
- Downstream execution remains subject to the existing Pantheon authorization boundary.

## Directional example

A packet of 100 units can be partitioned into:
- forward: 60 units (weight 0.6)
- upward: 40 units (weight 0.4)

The source identity accompanies both segments. These are illustrative data-flow units, not physical energy or signal output.

## Relationship to IDnfk and SACREL

IDnfk classifies the subject and routes unfamiliar cases to OTHER for inspection. Light Cut operates only after a valid route plan is supplied; it does not override OTHER, uncertainty, review, or authorization requirements.

SACREL temporal integrity applies: changed routing weights create a new, inspectable plan. They do not rewrite the original packet or its prior routing record.

## Verification

The C++11 test covers conservation, directional partitioning, source retention, missing weight, duplicate destinations, negative weights, non-finite amounts, and missing source identity.
