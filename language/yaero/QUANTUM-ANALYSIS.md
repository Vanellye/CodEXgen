# Ŷæṛö quantum-computing research boundary

Ŷæṛö treats quantum computing as an optional data-representation and analysis layer, not as an automatic replacement for classical execution.

## Near-term scope

- Preserve source code and immutable snapshots.
- Derive AST, typed IR, dependency graphs, control-flow graphs, and data-flow summaries.
- Export well-defined problem instances to isolated quantum-inspired or quantum-computing experiments.
- Keep classical baseline algorithms beside every experimental method.
- Record input hashes, algorithm versions, seeds, device/backend, shots or iterations, wall-clock time, memory, and output quality.

## Claims policy

No quantum speedup, advantage, or semantic equivalence is asserted without measured, reproducible benchmarks and a proof appropriate to the claim. A quantum-inspired heuristic is labelled as such and compared against a strong classical baseline.

## Isolation and safety

Experiments run on copies of derived data. They cannot write to source repositories, trigger deployments, or access credentials. Result artifacts include provenance and explicit limitations. Hardware availability and problem suitability are evaluated case by case; no quantum hardware is assumed.

## First experiments

1. Graph partitioning on small dependency graphs.
2. Search/optimization on bounded IR scheduling instances.
3. Compare classical heuristics, quantum-inspired heuristics, and available quantum backends using identical problem instances.
4. Publish negative results and resource costs as well as improvements.
