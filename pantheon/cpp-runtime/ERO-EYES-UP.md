# ERO Source Identity — EYES UP / Spectral Series

**Status:** C++11 descriptive source-inspection model on the ALEPH feature branch.

## Identity
ERO is represented as a declared source identity with a stable identifier, human-readable label, and origin reference. An incomplete identity is invalid. The origin reference is a provenance label, not proof that an external source has been authenticated.

## EYES UP
EYES UP performs layered inspection across source identity, history and lineage, dependencies, write permissions, and uncertainty. The spectral series distinguishes VERIFIED, INFERRED, and UNKNOWN records. Inferences remain inferences; unknowns remain visible until investigated.

## Authority boundary
ERO identifies where information claims to originate. It does not grant write rights. EYES UP does not execute generated code, alter files, change Git references, approve merges, or elevate inferred evidence. Code generation and adoption remain separate steps requiring explicit authorization from an authorized human.

## Meaning
“Spectre serisum” is used here as the name of the layered spectral inspection series: look through successive traces without mistaking a shadow, pattern, or hypothesis for verified origin.

## Verification
The pantheon_ero_source_test target covers identity validation, record collection, evidence-state reporting, and incomplete-source rejection. Build and CTest execution remain required before claiming runtime verification.
