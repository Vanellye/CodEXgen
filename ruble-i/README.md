# ₽.ı (Ruble-I) — deterministic value and evidence language

Status: experimental specification and local simulation only.

Ruble-I is a declarative language for modelling account balances, bounded allowances, transfers, currency/token exchange quotes, and time-stamped evidence. The reference model is deterministic and uses integer minor units. It does not connect to banks, wallets, exchanges, payment rails, minting services, or external databases.

## Safety boundary

- SIMULATE is the only execution mode in this initial version.
- No live transfer, withdrawal, mint, token issuance, settlement, credit posting, or provider call is implemented.
- A simulated transfer must name one source, one destination, one currency, one positive integer amount, and a unique transaction ID.
- An exchange must use a separately recorded quote with a rational rate, quote ID, timestamp, and expiry. No automatic conversion or hidden spread.
- Allowances are separate, period-scoped budgets. Hourly replenishment is a deterministic simulation rule, not a bank payment.
- Every event is hash-chained. Reversal means a compensating event; history is never overwritten.
- Scientific records, source-code interpretations, and benchmark results are evidence objects, not money or permissions.
- “Quantum speedup” is not assumed. Quantum-inspired or quantum-computing claims require independently reproducible benchmarks against a defined classical baseline.
- Legacy PONS/AVS records are retained as historical evidence. This simulator does not treat their approvals as new ₽.ı grants.

## Quick start

    python -m unittest discover -s ruble-i/tests -v
    python ruble-i/runtime.py ruble-i/examples/allowance-and-exchange.rubi

The sample produces a local simulated ledger report only.

## Language files

- SPEC.md — grammar, semantics, invariants, and migration contract.
- runtime.py — deterministic simulation interpreter.
- examples/allowance-and-exchange.rubi — sample program.
- tests/ — regression tests.

No production financial integration is claimed. A future bank adapter would require a separately reviewed implementation, provider-specific beneficiary verification, fresh human approval bound to exact transfer details, independent settlement evidence, and explicit authorization.