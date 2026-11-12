# ERIA Factual Logic Core

This module gives claims explicit epistemic labels and preserves source/provenance references.

## Claim classes
- OBSERVED: direct observation; method, scope, and limitations still need to be stated.
- SOURCE_REPORTED: attributed to a source; not independently corroborated.
- CORROBORATED: a supporting reference is supplied; this is not infallible proof.
- HYPOTHESIS: a proposed explanation, not established fact.
- INTERPRETATION: meaning inferred from evidence, not established fact.
- UNCLASSIFIED: rejected as not established.

## Required discipline
Keep source identity, provenance/history, supporting evidence, interpretation, uncertainty, and authorization distinct. A digest or reference can support traceability or integrity checks; it does not establish truth, consent, completeness, or representativeness. This formatter labels caller-supplied data; it does not authenticate sources or independently validate evidence.

## Build
```sh
cc -std=c99 -Wall -Wextra -Werror -I. FACTUAL_LOGIC.c tests/test_FACTUAL_LOGIC.c -o factual-logic-test
./factual-logic-test
```

This is a small contract layer, not a universal truth engine. Integrations must preserve original records, append corrections, expose uncertainty, and require human review for consequential decisions.
