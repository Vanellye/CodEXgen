# ERIA Code Ethics

## Purpose

This standard governs code creation, review, repair, execution, and transmission in ERIA. It protects people, source integrity, system reliability, and accountable human control.

## Core rules

1. **Human authority:** A tool, trigger, model, workflow, or runtime cannot grant itself permission. Consequential changes require explicit, scoped authorization from an accountable person.
2. **Least privilege:** Use the minimum access, scope, and duration required. Read access does not imply write access; write access does not imply permission to deploy or transmit.
3. **Provenance:** Preserve the original source, commit, author/actor, evidence, and transformation history. Corrections add a traceable successor; they do not erase the record of the fault.
4. **Evidence before claims:** Separate observed facts, reproducible findings, heuristics, hypotheses, and unknowns. A scanner warning is a lead for review, not proof of maliciousness or harm.
5. **Fail closed:** Missing, conflicting, expired, or unverifiable authorization blocks consequential action.
6. **Reversibility:** Prefer isolated branches, patches, backups, and tested recovery paths. Destructive changes require separate authorization and verified recovery.
7. **Consent and privacy:** Minimize collection and retention of personal or sensitive data. Do not inspect, infer, expose, or transmit private information without a legitimate, authorized purpose.
8. **No covert actuation:** Detection, scheduling, webhook receipt, or a passing quality score never independently authorizes execution, publication, or external dispatch.
9. **Human review:** Security-sensitive, rights-sensitive, production, permission, credential, and external-facing changes require human review.
10. **Accountability:** Record the finding, evidence, scope, proposed change, authorization, validation result, and disposition.

## Required change record

Every consequential repair must identify the source repository, branch, exact base commit, affected paths, observed behavior, evidence and confidence, proposed patch and expected effects, authorizing actor and scope, tests, review, recovery method, and final disposition.

## Prohibited shortcuts

- Silent source replacement, history rewriting, or provenance deletion.
- Self-approval, permission escalation, or treating a role label as a grant.
- Automatic publication, network dispatch, deployment, or physical actuation from trigger detection alone.
- Treating heuristic output as a verified security finding.
- Concealing failed tests, uncertainty, or incomplete recovery.

## Relationship to ÆĀÄÂ

ÆĀÄÂ is the code-rehabilitation process implementing these principles. Its default operation is read-only detection and diagnosis. It may prepare a patch for review, but repair execution remains separately authorized. See [ÆĀÄÂ Code Rehabilitation](./AEAA-CODE-REHABILITATION.md).

This document defines repository policy. It does not itself grant credentials, alter GitHub permissions, activate a runtime capability, or authorize any specific repair.
