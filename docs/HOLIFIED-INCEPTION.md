# Holified Inception — Contextual Perception Layer

**Status:** Cognitive-layer specification; first independent reader implemented, execution verification pending  
**Working branch:** `olpirt/stride-next`  
**Lineage:** Legacy Preservation & Independent Peering Protocol; Counterclockwise Temporal Reconciliation  
**Purpose:** Read beyond the immediate page of the present while preserving the distinction between evidence, interpretation, uncertainty, and imagination.

## Governing principles

> Do not let the page define the limits of perception.  
> Do not let imagination impersonate knowledge.  
> Look beyond the present, remember the origin, and bring understanding back with integrity.

These are operating constraints, not claims of supernatural, omniscient, or unrestricted perception. The layer expands the context examined by software; it does not grant access to information that has not been supplied, observed, or responsibly retrieved.

## Role in CodEXgen

Holified Inception is a contextual reasoning layer between input acquisition and downstream recommendation or action. It consumes an input plus available records, builds a traceable context map, identifies uncertainty and contradictions, explores labeled possibilities, and returns an evidence-aware interpretation for human review.

It does not own source records, override branch identity, certify untested compatibility, or execute consequential actions.

## Seven-stage cognitive cycle

1. **Present — Observe:** capture the current input, source, timestamp (if available), scope, and user intent without silently normalizing away meaningful details.
2. **Origin — Trace:** retrieve relevant provenance, prior versions, source history, and temporal context. Missing origin remains explicitly unknown.
3. **Connection — Relate:** map relevant entities, interfaces, dependencies, references, and possible causal links. Distinguish confirmed edges from proposed associations.
4. **Reflection — Challenge:** detect contradictions, stale claims, unsupported leaps, ambiguity, and alternative explanations. A contradiction is a review signal, not proof of wrongdoing.
5. **Possibility — Explore:** generate hypotheses, counterfactuals, simulations, and creative futures. Mark every such result as hypothetical, simulated, or fictional.
6. **Discernment — Evaluate:** classify each material statement by evidence status, confidence rationale, freshness, and unresolved limitations. Never convert repetition or fluency into evidence.
7. **Becoming — Return:** provide a concise synthesis, cite its origins, state what remains unknown, and propose reversible next steps. Require authorization before consequential execution.

Stages may be revisited in any order. They are lenses, not a hierarchy of human worth or a mandatory linear path.

## Evidence and knowledge boundary

Every material output statement must carry one of these labels:

| Label | Meaning | Permitted presentation |
|---|---|---|
| Observed | Directly present in supplied input or retrieved record | State what was observed and where |
| Verified | Independently supported by a reproducible test or authoritative evidence | State the scope and date of verification |
| Inferred | Reasoned from identified evidence | Explain the reasoning and alternatives |
| Hypothesis | A testable possibility not yet established | Present as a question or proposed test |
| Simulated | Produced by a model or synthetic process | Identify model assumptions and inputs |
| Fictional | Deliberately imagined narrative or world-building | Keep separate from factual records |
| Unknown / disputed | Evidence absent, conflicting, or insufficient | Preserve the uncertainty; do not fill the gap |

Confidence is not a substitute for these labels. If a confidence score is later implemented, it must expose its basis and must not imply calibrated probability unless calibration has been measured.

## Temporal and provenance principles

- Use the [Counterclockwise Temporal Reconciliation](TEMPORAL-RECONCILIATION.md) model to inspect prior events and later recorded consequences.
- Preserve original records and exact source references; corrections are append-only annotations or new derived views.
- Keep observed timestamps, logical sequence, simulated time, and fictional dates in distinct fields.
- Never invent missing events, timestamps, dependencies, authorship, or source identity.
- Every derived claim should retain links to the evidence and transformation that produced it.
- A rewind is read-only. Replaying context must not repeat external side effects.

## Connection and perception principles

A relationship map should record:
- source node and destination node;
- relationship type (reference, dependency, temporal succession, observed association, inferred association, or hypothetical link);
- evidence and provenance;
- direction and scope;
- confidence rationale or unknown status;
- last verification time, where available.

Correlation must not be presented as causation. Hidden or unavailable data must not be implied to have been inspected. Search scope and retrieval limitations must remain visible.

## Correction and accountability

When the layer identifies a possible misunderstanding or wrong claim, it should:
1. quote or precisely reference the original claim;
2. identify the conflict or missing support;
3. show the evidence and its provenance;
4. offer a correction, clarification, or unresolved-dispute status;
5. preserve the original record and explain the affected derived views;
6. provide a recovery path for the derived interpretation.

Challenge claims, not people's dignity. Do not treat disagreement, age, branch isolation, or missing CI as proof of defect or bad intent.

## Output shape

A Holified Inception response should contain, as applicable:

- **Present reading:** what the current input says.
- **Origins:** source records and relevant history.
- **Connections:** confirmed relationships and separately labeled hypotheses.
- **Tensions:** contradictions, gaps, and alternative explanations.
- **Beyond the present:** clearly labeled scenarios, simulations, or fiction.
- **Discernment:** evidence labels, limitations, and unresolved questions.
- **Return:** a traceable synthesis and reversible next step.

Keep the answer proportional to the evidence. If no additional context is available, say so and reason only from the present input.

## Consent, privacy, and execution boundaries

- Prefer local-first processing and minimum necessary context.
- Do not infer sensitive personal traits or beliefs from indirect signals.
- Do not use biometrics, faith, or creative expression as proof of identity, consent, truth, or authority.
- Do not transmit private records or credentials without explicit authorization.
- Do not autonomously publish, merge, delete, overwrite, or trigger external side effects.
- Present consequential actions for human review with scope, risks, and rollback information.

## Minimum acceptance tests

1. **Origin retention:** a correction changes a derived interpretation but leaves the original source and reference intact.
2. **Evidence separation:** observed, verified, inferred, hypothetical, simulated, and fictional statements remain distinguishable in serialized output.
3. **Unknown preservation:** absent timestamps, provenance, or dependencies remain unknown rather than being fabricated.
4. **Contradiction handling:** conflicting sources are surfaced with both references and are not silently collapsed.
5. **Causal restraint:** correlation alone never produces a causal assertion.
6. **Temporal reversibility:** backward traversal is the exact reverse of the selected event sequence; forward traversal restores the original order.
7. **No replay side effects:** context replay cannot repeat a write, publication, or other external action.
8. **Fiction boundary:** fictional or simulated content cannot be promoted into factual records without independent evidence and review.
9. **Consent gate:** consequential actions require explicit authorization at the point of execution.
10. **Provenance closure:** each material derived claim links to its source and transformation, or is labeled unsupported.

## Implementation boundary

This commit establishes the cognitive-layer contract and acceptance criteria. It does not claim that a new reasoning engine, model, perception sensor, autonomous agent, or runtime pipeline has been implemented or tested. Code implementation must be a separate, reviewable phase that identifies existing Stride interfaces, dependencies, tests, and data flows before peering.

## Governing statement

**Perceive beyond the page. Preserve the origin. Distinguish what is known from what is imagined. Return understanding with integrity.**
