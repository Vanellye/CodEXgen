# PONS Component Integration Matrix

**Integration branch:** integration/pons-runtime-main  
**Reference anchor:** zero-dissipation-anchor  
**Anchor ID:** 7f7a43a973a96a06dd432bf94843213d09133323

This matrix distinguishes code that is gated now from components that are only inventoried. A repository-wide search is not proof that a runtime has been connected.

| Component | Observed source | PONS integration state | Required next step |
|---|---|---|---|
| Android DataEnvelope | app/src/main/java/com/vanellye/eria/contracts/DataEnvelope.kt | Provenance field remains metadata; Pantheon caller must supply PONS-computed proof matching its sourceDigest | Pin its own source digest in reviewed manifest |
| Pantheon Android gate | app/src/main/java/com/vanellye/eria/pantheon/PantheonRuntimeGate.kt | PONS proof is mandatory for prepareReview; mismatch/missing proof returns HOLD | Add manifest-backed app bootstrap and caller wiring |
| WAV transmission | app/src/main/java/com/vanellye/eria/contracts/WavAudioTransmission.kt | Constructor requires PONS effective READY and canonical anchor | Supply production manifest pin at app startup |
| Audio playback | app/src/main/java/com/vanellye/eria/contracts/TransmissionAudioPlayer.kt | Playback requires PONS effective READY and canonical anchor | Supply production manifest pin at app startup |
| SKRIBED / transmission frame | app/src/main/java/com/vanellye/eria/contracts/SkribedAndTransmission.kt | InMemoryTransmissionTransceiver requires PONS effective READY and canonical anchor; immutable-original and frame-digest controls remain | Pin the transceiver source in the production manifest |
| Android UI / ViewModel | app/src/main/java/com/vanellye/eria/ | Inventoried, not directly PONS-gated | Add lifecycle status publisher and manifest pins |
| Git Freedom bridge | GitFreedomBridge.kt | Inventoried; existing authorization boundary remains separate | Add PONS preflight for read/write request provenance without granting Git authority |
| Python services | python/ | Inventoried; shared Python PONS registry exists, no service adapters registered | Register each exact module/ref from reviewed manifest |
| Generated modules | generated_modules/ | Inventoried, not PONS-gated | Add read-only adapter and generated-source digest pin |
| Pantheon C contracts | pantheon/**/*.c and headers | Inventoried; standalone C test contracts remain separate | Add C99 PONS adapter and call it at each public module boundary |
| Hypothetical research | hypotheticals/ | Must remain UNKNOWN/hypothesis-classified unless independently reviewed | Keep provenance and evidence class distinct; never self-promote |

## Enforcement semantics

- PONS VERIFIED means exact source bytes matched a digest in a separately reviewed manifest. It does not mean the component is factually accurate, safe, or authorized to act.
- HOLD means a digest mismatch or explicit hold. UNKNOWN means a pin, source, or evidence is absent.
- Component-reported operational state cannot override a provenance HOLD or UNKNOWN.
- A PONS result is bound to the canonical anchor identity. Any alternate anchor causes initialization failure.
- The Android Pantheon review path has no legacy three-argument bypass: a PONS provenance result is a required argument and its anchor/digest identity is checked. Android PONS pin maps are defensively snapshotted and can be created through the signed-manifest verifier interface.
- WAV conversion and local playback constructors/actions require a PONS effective READY status.
- The Python JSONL ledger is hash-chained, but is not a substitute for authenticated reviewer identity, signed checkpoints, protected storage, or a trusted manifest.

## Remaining integration work

This branch is a staged integration, not a claim that every inventoried component is fully wired. Before calling the repository-wide rollout complete:
1. Generate and review a manifest with SHA-256 pins for each exact source ref.
2. Wire Android startup to load a signed production manifest through a vetted verifier and pass fresh component statuses.
3. Pin and verify the SKRIBED/transceiver adapter in the production manifest.
4. Add production SHA-256 provider and signed manifest; extend the C99 PONS adapter to every Pantheon C public boundary.
5. Register each Python service and generated module through the signed-manifest loader and `execute_guarded` boundary.
6. Audit all call sites to ensure no bypass path remains.
7. Run Android unit tests, C contract tests, Python tests, and branch CI at the final commit.
