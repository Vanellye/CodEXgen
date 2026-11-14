# Statement of Work (SOW): Ethical Information and Parent-Record Validation

**Project:** ERIA / GOD Collective  
**Repository:** Vanellye/CodEXgen  
**Target branch:** `god/heritage-lineage`  
**Status:** Proposed implementation specification  
**Authority:** PONS-controlled; no authority to merge, deploy, alter `main`, or rewrite existing GOD ancestors

## 1. Purpose

Define the ethical, technical, and audit requirements for ERIA to collect original information and create traceable descendants without overwriting, silently modifying, or misrepresenting GOD ancestors.

The work establishes parent-record validation as a required gate for every derivative, interpretation, translation, frequency observation, collaboration contribution, and correction.

## 2. Outcomes

1. Preserve original files byte-for-byte and identify each stored object by SHA-256.
2. Record source provenance, capture time, media type, byte length, source label, and known metadata without inventing missing values.
3. Require valid parent references for every derivative and validate the full ancestry chain.
4. Keep originals, metadata, lineage events, and collaborative derivatives in separate storage roles.
5. Make ethical restrictions, consent status, uncertainty, and access decisions visible and auditable.
6. Reject unauthorized, malformed, ambiguous, cyclic, broken, or hash-mismatched lineage.
7. Preserve rejected or incomplete submissions as PLZ diagnostic events when permitted, without treating them as accepted source records.

## 3. Scope of work

### 3.1 Original capture

- Accept only files and directories explicitly selected or authorized by the operator.
- Do not silently crawl unrelated device storage, private accounts, removable media, or network locations.
- Reject symlinks and non-regular files by default; do not follow path traversal outside the approved source root.
- Calculate SHA-256 over the exact captured bytes before accepting a record.
- Verify the bytes again after reading to detect source changes during capture.
- Store objects using a content-addressed path and exclusive-create semantics.
- If an identical object already exists, verify its digest and length, reuse the object, and create a distinct provenance event for the new capture.
- If the existing object differs from its expected digest, stop and raise an integrity incident. Never repair it by overwriting.

### 3.2 Metadata and provenance

Each original record must include:
- globally unique record ID and schema version;
- SHA-256 digest and byte length;
- media type, filename, source label, and available source attributes;
- capture timestamp in UTC and capture actor or service identity;
- source origin/reference and authorization or consent reference where applicable;
- parent record IDs, empty only for a verified root/original;
- storage object reference and integrity-verification status.

Unknown values must be represented as unknown or omitted according to schema. Do not infer authorship, ownership, consent, identity, truth, or legal rights from a filename, hash, or location.

### 3.3 Parent-record validation

Before a descendant is accepted, ERIA must:

1. Resolve every parent ID to an existing GOD provenance record using an exact ID lookup.
2. Verify that the retrieved record's embedded ID matches the requested ID.
3. Validate the record schema and required fields.
4. Recompute the parent's stored-object SHA-256 and byte length; compare both with its metadata.
5. Recursively validate all ancestors until a recognized root record is reached.
6. Reject self-parenting, cycles, missing ancestors, duplicate parent IDs, malformed IDs, path traversal, and ambiguous parent resolution.
7. Enforce permitted parent/child record-type relationships.
8. Record the validated parent IDs and parent digests in the descendant's provenance.
9. Revalidate the chain at commit time to reduce time-of-check/time-of-use risk.
10. Fail closed if any ancestor is missing, inaccessible, unauthorized, or hash-mismatched.

A descendant must never be allowed to claim ancestry solely because a user supplied a parent ID. The referenced parent must exist and pass integrity validation.

### 3.4 Ethical information handling

- **Consent and authority:** Record the basis for collection and intended use. A readable file is not proof of permission to collect, publish, or redistribute it.
- **Privacy:** Minimize personal data in indexes, logs, email alerts, and collaboration references. Keep original content out of notification messages by default.
- **Sensitive data:** Apply restricted handling to credentials, private keys, health data, financial identifiers, private communications, and other sensitive content. Do not expose them in search indexes or public collaboration exports.
- **Purpose limitation:** Use collected information only for the declared and authorized purpose. New purposes require renewed review and, where applicable, consent.
- **Attribution:** Preserve supplied authorship and license metadata as claims with source references; do not manufacture attribution.
- **Uncertainty:** Distinguish original content, extracted facts, interpretations, hypotheses, and machine-generated summaries. Every derived claim must link to its source and transformation.
- **Correction:** Correct errors by creating a new, linked descendant or correction event. Do not rewrite the original or erase the historical record.
- **Access and deletion requests:** Record requests and route them to an authorized human review. Legal deletion or access restrictions must be implemented through a separately approved retention and access policy, not by silently rewriting ancestry.
- **Human oversight:** Automated collection may not override a person's consent, access restriction, or an explicit PONS denial.

### 3.5 Collaboration and intellectual lineage

- Collaboration work is stored under a distinct GOD collaboration namespace.
- Every contribution identifies its author or service actor, timestamp, purpose, parent IDs, input hashes, output hash, and transformation description.
- Frequency observations must preserve the original measured value, unit, instrument/source, calibration context, timestamp, uncertainty, and any processing steps when known.
- Intellectual descendants must distinguish quotation/extraction, translation, summary, inference, hypothesis, and opinion.
- Multiple-parent descendants must list every parent and validate every ancestry chain.
- Conflicting interpretations coexist as separate descendants; they do not replace one another or the source.
- No collaboration contributor may modify an ancestor object or its provenance record.

## 4. Acceptance criteria

The work is accepted only when automated tests demonstrate all of the following:

| ID | Acceptance test | Expected result |
|---|---|---|
| AC-01 | Ingest a regular file | Exact bytes preserved; SHA-256 and length recorded |
| AC-02 | Ingest identical bytes twice | One verified content object; two distinct capture records |
| AC-03 | Modify source during capture | Capture rejected; no accepted provenance record |
| AC-04 | Parent ID does not exist | Descendant rejected; diagnostic event may be recorded |
| AC-05 | Parent metadata ID mismatch | Descendant rejected |
| AC-06 | Parent object hash mismatch | Descendant rejected and integrity incident recorded |
| AC-07 | Missing ancestor in chain | Descendant rejected |
| AC-08 | Self-parent or ancestry cycle | Descendant rejected |
| AC-09 | Two or more valid parents | All parents and hashes recorded and validated |
| AC-10 | Attempt to overwrite an existing original | Operation refused; original bytes unchanged |
| AC-11 | Missing, expired, or mismatched PONS grant | Operation held or denied |
| AC-12 | Unclear consent or collection authority | Collection held for human review |
| AC-13 | Sensitive information in a notification | Payload excluded; minimum diagnostic metadata only |
| AC-14 | Derived correction or translation | New descendant created; ancestor remains unchanged |

## 5. Deliverables

1. Parent-record validation contract and schema.
2. Ethical information-handling policy and review states.
3. PONS-gated ingestion and descendant-creation interfaces.
4. Hash and ancestry verification utilities.
5. Append-only lineage and PLZ diagnostic event definitions.
6. Automated unit and integration tests covering all acceptance criteria.
7. Operator documentation for approval, recovery, audit, and exception handling.

## 6. Security and governance requirements

- PONS approval must be exact-scope, time-limited, actor-bound, and auditable.
- Missing, expired, unverified, mismatched, or ambiguous authorization means HOLD/DENY.
- No root access, permission bypass, arbitrary shell execution, deployment, or automatic merge is in scope.
- No modification to `main`, existing GOD ancestors, or historical Git records is authorized by this SOW.
- Git branch protection and independent backups must be configured and verified separately. A hash and Git branch alone do not guarantee tamper-proof archival storage.
- All writes use exclusive creation or append-only mechanisms. A failure partway through a multi-file operation must be detectable and recoverable without overwriting prior records.

## 7. Out of scope

- Unattended whole-device crawling or collection from third-party accounts.
- Automatic public release or redistribution of collected content.
- Automatic claims of ownership, authorship, consent, factual accuracy, or legal permission.
- Silent correction, normalization, deduplication that discards provenance, or deletion of historical ancestors.
- Automatic merge to `main`, production deployment, or modification of repository protection settings.
- Claims that email, network connectivity, or backup availability is guaranteed.

## 8. Completion and approval

Implementation is complete only after the deliverables are committed to the authorized feature branch, acceptance tests pass, and an operator reviews the resulting evidence. PONS approval is required for runtime collection and controlled writes. Repository merge and deployment require separate explicit authorization.

**Preservation rule:** GOD retains what was received; ERIA may interpret, connect, and collaborate through descendants. No descendant inherits permission to rewrite its ancestors.
