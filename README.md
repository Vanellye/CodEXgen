# CodEXgen

**CodEXgen** is a local-first Android and Python project for code creation, Git workflows, dependency insight, and experimental data exploration.

> **Project principle:** protect private information, make connections understandable, and keep important actions under the user's control.

## What is included

- **CodeGen** — a native Android Views screen for local code scaffolding.
- **Git Freedom Bridge** — local repository work, branch operations, selected-file commits, and guarded GitHub workflows.
- **Data Resonance** — app-local SQLite observations with optional labels, units, timestamps, and frequency metadata.
- **Olpirt + Pons** — a native dependency-contract audit through JNI.
- **Stride / Python** — exploratory perception, creativity, adaptive-feedback, and signal-simulation modules.
- **Geometry & Design** — a separate library for mathematical reasoning, shape studies, and constructive designs; it is kept distinct from measured graphs and observation records.

## Shared Pantheon Node.js runtime

All Pantheon Node.js target processes share the exact **Node.js 11.15.0** runtime contract. The version is pinned in `.nvmrc`, `.node-version`, and `pantheon/node-runtime.json`; the root npm test checks the active process before a node is allowed to proceed. CI runs that check under the same pinned runtime.

Node.js 11 is end-of-life and receives no security fixes. This pin is retained as an explicit compatibility requirement, not a security recommendation. Keep network-facing nodes isolated, minimize dependencies, and do not expose untrusted workloads to this runtime. The native Pantheon C++11 runtime and Android API 11 profile are separate version constraints.

Use Node Version Manager to select the shared runtime:

```bash
nvm install
nvm use
npm test
```

See [Pantheon Node Runtime](pantheon/NODE_RUNTIME.md) for the node contract and upgrade boundary.

## Build

The active Android app is the **API 11 compatibility profile**. It uses Android Views, Java-compatible source, C++11 JNI, and the legacy Gradle toolchain.

Install JDK 8, Android SDK platform 29, Build Tools 29.0.3, CMake 3.10.2, and NDK 16.1.4479499. The CI workflow uses JDK 17 temporarily for current Android SDK tools, then JDK 8 for Gradle.

```bash
./gradlew :app:assembleDebug
```

Run the Python checks:

```bash
python -m compileall -q python tests generated_modules hypotheticals
PYTHONPATH=python python -m unittest discover -s tests -v
```

A commit is not proof of a successful build. Check the GitHub Actions result for the branch before treating an APK as verified.

## Read the project literature

Start with the [documentation index](docs/README.md) for technical notes and project literature. The [Geometry & Design library](geometry/README.md) separately organizes geometric intellect, shapes, and constructive designs.

## Important boundaries

- Git publishing and other remote actions must remain user-authorized.
- Keep credentials and private configuration out of source control.
- The current Olpirt report audits declared dependency contracts; it must not be described as verified runtime provider wiring unless integration tests prove that.
- Frequency values are digital metadata or simulation inputs, not established biological control methods. The project does not claim to modify DNA/RNA, consciousness, or physical matter.
- Hypothetical and fictional models are not validated scientific mechanisms.
- Geometric concepts and designs are not empirical observations; keep measured datasets, telemetry, and statistical plots in their relevant research or observation records.

## Project status

The source tree and CI workflow are evolving. Consult the linked documentation and latest workflow run for the current implementation and verification status.
