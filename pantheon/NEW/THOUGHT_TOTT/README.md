# THOUGHT TOTT — Correction-to-Learning Layer

**State:** Staged; not wired into runtime.

THOUGHT TOTT turns reviewed corrections into reusable, traceable learning notes. It does not rewrite history, silently train on private material, infer a person's beliefs, or promote a single correction into a universal rule.

## Learning record

Each lesson retains:
- stable lesson ID and originating correction/notice ID;
- source and corrected-record references;
- the observed mistake and the correction;
- the evidence reference and review basis;
- the reusable lesson stated narrowly;
- scope where the lesson applies;
- classification: proposed, accepted, challenged, or superseded;
- reviewer and timestamp.

## Recycling flow

1. **Notice:** discover correction notices, reversions, failed tests, reopened issues, and superseded representations.
2. **Trace:** link each notice to its original record, affected commit/branch, and evidence.
3. **Compare:** distinguish an actual defect from a changed requirement, deliberate reversal, experiment, or unresolved disagreement.
4. **Extract:** draft a narrowly scoped lesson; do not generalize beyond the evidence.
5. **Review:** accept, challenge, or defer the lesson. A repeated pattern raises priority for review, not truth status.
6. **Reuse:** surface accepted lessons as checks or prompts when a similar change appears.
7. **Retest:** verify the lesson against the new context; record false positives and exceptions.
8. **Preserve:** keep prior notices, lesson versions, dissent, and supersession links.

## Required distinctions

- **Correction** says what was changed and why.
- **Lesson** says what may be reusable and within what scope.
- **Evidence** supports the correction or lesson; provenance records where it came from.
- **Acceptance** records review status; it does not guarantee universal truth.
- **Memory** is not identity: lessons do not speak for people or recreate missing people.

## Review cadence

Use change detection, not repeated ceremonial approval. Review new or changed evidence, contradictions, scope changes, safety impact, and consequential use. Reuse an accepted lesson without re-approval for routine, reversible checks within its recorded scope. Explicit approval remains necessary for publication, sensitive-data use, consequential actions, destructive edits, or scope expansion.

## Privacy and safety

Only ingest authorized, minimized records. No covert monitoring, private-stream scraping, sensitive-trait inference, profiling, manipulation, or targeting. Do not treat a commit message alone as proof that a code change was correct. Repository history is evidence of recorded changes, not a complete account of every past correction or conversation.

## Build and test

```sh
cc -std=c99 -Wall -Wextra -Werror -Ipantheon/NEW/THOUGHT_TOTT \
  pantheon/NEW/THOUGHT_TOTT/THOUGHT_TOTT.c \
  pantheon/NEW/THOUGHT_TOTT/tests/test_THOUGHT_TOTT.c -o /tmp/thought-tott-test
/tmp/thought-tott-test
```

The initial module validates and formats a lesson proposal. It does not crawl Git history, ingest every prior correction, update model weights, or execute repository changes. Those require separate adapters, evidence validation, and authorization.
