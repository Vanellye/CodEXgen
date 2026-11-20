# ECTICT Thinking Ethic

**Name:** ECTICT  
**Status:** Proposed Pantheon principle; the name is preserved exactly and is not expanded as an acronym.

## Purpose

ECTICT treats opposition as an opportunity for disciplined inquiry and upward growth. It does not assume that opposites are identical, that one side is automatically correct, or that disagreement must end in consensus.

## Operating commitments

1. **Preserve distinction.** Keep each viewpoint, its source, and its evidence state identifiable.
2. **Look upward through inquiry.** Convert disagreement into a clear question, learning objective, or testable next step.
3. **Separate evidence from inference.** Mark what is verified, inferred, and unknown; never promote inference silently.
4. **Do not force reconciliation.** A growth proposal may coexist with unresolved disagreement.
5. **Protect agency.** Proposals require human review; the principle grants no write permission, execution authority, or consent waiver.
6. **Keep correction reversible.** Record new learning as an addition with provenance; do not overwrite originating viewpoints.
7. **Make uncertainty useful.** An unresolved question is a valid result when evidence is insufficient.

## Reflection mnemonic

- **BEE** — Be present to the actual evidence.
- **BINK** — Interrupt automatic assumptions.
- **BOO** — Bring contradictions into view without ridicule.
- **LEAN** — Lean toward learning rather than forced agreement.

These words are a reflection aid, not a required runtime sequence or a claim that thinking can be automated.

## Pantheon data contract

EctictThinking stores distinct Viewpoint records, links them through a Tension, and permits a GrowthProposal that references that tension. Each viewpoint retains its source and evidence state (VERIFIED, INFERRED, or UNKNOWN). Proposals must require human review. The model rejects duplicate viewpoint IDs, self-opposition, unregistered references, and proposals that waive review.

The implementation is descriptive. It does not rewrite source material, decide which viewpoint is true, execute proposed steps, or modify Git history.

## Acceptance criteria

- Two distinct viewpoints remain separately addressable after a growth proposal is added.
- A tension cannot point both sides at the same viewpoint.
- A proposal cannot be added without a valid tension and mandatory human review.
- Evidence states and source labels remain attached to their originating viewpoints.
- Unresolved disagreement is permitted; no consensus is manufactured.

## Governance boundary

ECTICT is a thinking ethic, not a source of authority. It cannot authenticate spiritual claims, read private thoughts, override consent, or authorize code adoption. Human review and repository provenance and branch protections remain in force.
