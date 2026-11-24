# ERIA Financial Tunnel — Internal Simulator

Deterministic in-memory simulator established before external provider sandboxes.

## Safety
- SIMULATION_ONLY; records are SYNTHETIC / SIMULATED.
- No network calls, provider SDKs, real credentials, bank connections, wallet keys, transfers, orders, or broadcasts.
- Plaid, Coinbase CDP, and Wise remain disabled and NOT_CONFIGURED.
- PONS is not part of the simulator or gateway path; simulated transfers retain preview-hash provenance only.
- Ledger is append-only; reversals use compensating entries.

## Run
`node --test financial-tunnel/sandbox/simulator.test.mjs`

## Fifteen scenarios
1. Synthetic account acquisition
2. Invalid identity rejection
3. Insufficient balance rejection
4. Successful internal transfer
5. Failed external transfer
6. Duplicate transaction detection
7. Expired quote rejection
8. Simulator transfer without PONS dependency
9. Preview provenance retained without PONS
10. Payment reversal
11. Simulated blockchain confirmation
12. Webhook replay rejection
13. Ledger imbalance detection
14. Settlement reconciliation
15. Provider timeout and recovery evidence

Each scenario runs against a fresh deterministic fixture. Webhook, chain confirmation, and timeout/recovery are local state simulations, not external integrations. The shared provider contract and explicit registry live in `../financial/`; `internal_simulator` is the initial contract-compliant provider adapter.

## Provider gate
Do not enable an external adapter until official project ownership, sandbox credentials, endpoint, scopes, capabilities, and webhook verification are independently checked. Live execution remains disabled.
