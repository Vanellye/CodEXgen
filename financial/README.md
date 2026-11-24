# ERIA Financial Provider Foundation

This directory contains the first shared contract and provider registry for the ERIA / ASH Financial Tunnel.

## Contract source of truth

- `contracts/financial-provider.schema.json` — language-neutral JSON Schema contract.
- `contracts/types.ts` — TypeScript types matching the schema.
- `app/src/main/java/com/vanellye/eria/financial/FinancialProvider.kt` — Kotlin mirror for Android/MCP integration.

Money is represented as a decimal string on the wire. Do not use binary floating-point for financial amounts.

## Provider boundary

- `contracts/provider.ts` — provider interface.
- `registry/provider-registry.ts` — explicit provider selection and capability checks.
- `adapters/simulator-provider.ts` — first working adapter; in-memory synthetic accounts and ledger only.
- `index.ts` — default composition root.

The registry currently accepts only `SIMULATION_ONLY` providers. It never silently substitutes another provider. The simulator has no network client, credentials, external endpoint, or real-funds capability. Its `simulateTransfer` method changes only synthetic in-memory balances and records explicitly simulated ledger entries.

## Default fixture

- Synthetic Checking: USD 10,000.00
- Synthetic Wallet: USD 2,500.00
- Transfer fee: USD 0.00

These are test fixtures, not real accounts or balances.

## Run the simulator tests

From the repository root:

```sh
node --experimental-strip-types --test financial/adapters/simulator-provider.test.ts
```

The root `npm test` command also includes this test file.

## Security boundary

This provider foundation contains no PONS dependency. Simulation does not authorize a live transaction. Any future live adapter must be a separately reviewed implementation with provider-native authentication and independent, fresh user confirmation bound to an exact transaction preview. No live provider is registered or enabled by this baseline.
