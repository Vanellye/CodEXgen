# Statement of Work: Autonomous Repository Interpretation and Representation Forge

**Project:** ERIA / GOD Collective
**Repository:** Vanellye/CodEXgen
**Target branch:** `god/heritage-lineage`
**Engine:** `tools/eria_repository_forge.py`
**Schema:** `eria.repository-forge/1`
**Execution mode:** Explicitly invoked, read-only source inspection

## 1. Purpose

Create a complete, evidence-grounded representation of a selected Git working tree so ERIA can inventory the repository, extract structural information, identify source relationships, and prepare a navigable interpretation layer without changing original source files or Git history.

“Autonomous” means the forge performs the requested inventory and extraction steps without requiring the operator to open each file manually. It does **not** mean continuous background surveillance, unattended device crawling, arbitrary execution, or permission to mutate a repository.

## 2. Required pipeline

1. **Select and bind scope.** The operator selects one existing Git working tree. The inventory source is the Git file list: tracked files plus non-ignored untracked files. Git internals and ignored files are outside this first version.
2. **Inventory.** Record each discovered relative path and classify it as observed, restricted, excluded from deep parsing, non-regular, or unavailable.
3. **Preserve identity.** For eligible regular files, calculate SHA-256 and exact byte length from the bytes read. Do not normalize line endings, rewrite encodings, or save altered source content.
4. **Detect format.** Label known languages and data/document formats from file extensions. Unknown formats remain “Other” or opaque; do not guess a parser.
5. **Extract structure.** Parse supported formats without executing them. Current structural extractors include Python AST, JSON/TOML/XML top-level structure, Markdown headings, and declaration/import patterns for common source languages.
6. **Map relationships.** Resolve only demonstrable local import references. Keep unresolved or external imports as import observations; do not fabricate edges.
7. **Forge representation.** Produce a versioned JSON report with repository revision, inventory summary, per-file identity, structural observations, local relationships, and explicit safety/limitation metadata.
8. **Export separately.** If the operator requests a file, write the representation to a new path outside the scanned repository using exclusive creation. Never overwrite an earlier representation.

## 3. Representation contract

Every eligible file entry may include:

- repository-relative path;
- detected language or format;
- byte length and SHA-256;
- classification and parse status;
- extracted symbol names and source line numbers where available;
- imports and resolved local import relationships;
- document headings or structured-data keys where applicable.

The repository-level envelope includes:

- schema and generation timestamp;
- repository name, current Git branch, and HEAD revision;
- inventory basis and aggregate counts;
- per-file entries and evidence-backed relationship edges;
- the distinction between observed facts and any later inferred interpretations;
- explicit safety flags and known limitations.

No source payload is copied into the representation by default. Secret values are redacted before structural parsing. Files with sensitive names are listed as restricted metadata and are not opened or hashed. Binary files are identified and hashed where eligible, but are not decoded as text. Files above the structural parsing size limit are still streamed for a digest but are not parsed.

## 4. Interpretation rules

- A path, digest, size, language label, syntax node, heading, or resolved import is an **OBSERVATION**.
- Architectural meaning, author intent, correctness, security, dependency behavior, and runtime effects are not proven by syntax extraction.
- Any future semantic interpretation must be separately labeled **INFERRED**, cite exact file paths and line ranges, preserve uncertainty, and retain the source digest used.
- Conflicting interpretations must coexist as separate descendants; no interpretation replaces its source or another interpretation.
- Machine-generated descriptions are not authorship, consent, license, or factual verification.

## 5. Ethical and security boundary

- No source file, original GOD object, provenance record, or Git object may be rewritten by the forge.
- No source code is executed, imported as a runtime module, compiled, installed, or invoked.
- No network, remote account, package manager, host shell, root access, or permission bypass is used.
- Git calls are read-only inventory/revision queries only.
- Symlinks are not followed. Path traversal outside the selected repository is rejected.
- Sensitive-name files and secret-like values are excluded from deep extraction; reports must not contain secret values.
- Report output must be outside the selected repository and use exclusive creation.
- A report is a derivative representation. To store it in GOD, the caller must separately use the PONS-authorized ingestion path, and its parent record(s) must pass the recursive parent-validation engine.

## 6. Operational interface

From the repository root:

```bash
python tools/eria_repository_forge.py . --output "$HOME/eria-repository-forge.json"
```

The target must be a new path outside the repository. Without `--output`, the report is emitted to standard output. The command does not run as a watcher or daemon.

## 7. Acceptance criteria

| ID | Requirement | Expected evidence |
|---|---|---|
| RF-01 | Inventory selected Git worktree | Every Git-listed path has a classification |
| RF-02 | Hash eligible regular files | SHA-256 and byte length match the exact file bytes |
| RF-03 | Parse Python source safely | AST symbols/imports extracted without executing code |
| RF-04 | Parse supported structured formats | Keys/headings/tags extracted, source values omitted |
| RF-05 | Build local relationships | Edges only for resolvable local imports |
| RF-06 | Restrict sensitive files | Sensitive-name files are not opened or hashed |
| RF-07 | Reject symlinks and traversal | No symlink target or outside path is read |
| RF-08 | Preserve source/Git state | Before/after source hashes and HEAD remain unchanged |
| RF-09 | Export safely | New external report created; existing outputs are not overwritten |
| RF-10 | Expose uncertainty | Parse failures, exclusions, and limitations remain visible |

## 8. Non-goals for version 1

- Continuous filesystem watcher or unattended device-wide collection.
- Semantic claims that require human judgment or an external AI model.
- Execution, compilation, tests, dependency installation, or runtime tracing of scanned code.
- Reading ignored files, Git internals, secrets, private account data, or remote repositories.
- Automatic commits, branches, merges, deployment, transmission, or public publication.
- Automatic registration of the representation as a GOD record.

## 9. Governance

This SOW authorizes implementation on `god/heritage-lineage` only. It does not authorize changes to `main`, overwriting GOD ancestors, changing branch protection, merging, or deployment. Any future ingestion of the generated representation remains subject to exact-scope PONS authorization and complete parent-chain validation.

**Preservation rule:** The forge may represent the repository; it may not become the authority to rewrite it.
