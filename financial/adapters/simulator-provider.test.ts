import assert from "node:assert/strict";
import { test } from "node:test";
import { createDefaultFinancialRegistry, ProviderRegistryError } from "../index.ts";

test("default registry exposes the simulator and no live mode", () => {
  const registry = createDefaultFinancialRegistry();
  const provider = registry.resolve("eria-simulator", [
    "accounts.read",
    "balances.read",
    "transfers.preview",
    "transfers.simulate",
  ]);
  assert.equal(provider.descriptor.mode, "SIMULATION_ONLY");
  assert.deepEqual(registry.descriptors().map((item) => item.id), ["eria-simulator"]);
});

test("registry fails explicitly instead of silently substituting providers", () => {
  const registry = createDefaultFinancialRegistry();
  assert.throws(() => registry.get("plaid"), ProviderRegistryError);
  assert.throws(
    () => registry.resolve("eria-simulator", ["transfers.execute" as never]),
    ProviderRegistryError,
  );
});

test("simulator previews and applies an in-memory transfer exactly once", async () => {
  const registry = createDefaultFinancialRegistry();
  const provider = registry.resolve("eria-simulator");
  const beforeSource = await provider.getBalance("sim-checking-usd");
  const beforeDestination = await provider.getBalance("sim-wallet-usd");

  const preview = await provider.createTransferPreview({
    sourceAccountId: "sim-checking-usd",
    destinationAccountId: "sim-wallet-usd",
    amount: { amount: "125.50", currency: "USD" },
    memo: "test fixture",
  });
  assert.equal(preview.mode, "SIMULATION_ONLY");
  assert.match(preview.digest, /^[a-f0-9]{64}$/);
  assert.equal(preview.status, "PREVIEW");

  const receipt = await provider.simulateTransfer(preview.id);
  assert.equal(receipt.status, "SIMULATED");
  assert.equal(receipt.simulated, true);

  const afterSource = await provider.getBalance("sim-checking-usd");
  const afterDestination = await provider.getBalance("sim-wallet-usd");
  assert.equal(afterSource.available.amount, "9874.5");
  assert.equal(afterDestination.available.amount, "2625.5");
  assert.notEqual(afterSource.available.amount, beforeSource.available.amount);
  assert.notEqual(afterDestination.available.amount, beforeDestination.available.amount);

  await assert.rejects(() => provider.simulateTransfer(preview.id), /already been consumed/);
  assert.equal((await provider.listTransactions("sim-checking-usd")).length, 1);
  assert.equal((await provider.listTransactions("sim-wallet-usd")).length, 1);
});

test("simulator rejects invalid amounts, currencies, accounts, and insufficient funds", async () => {
  const provider = createDefaultFinancialRegistry().get("eria-simulator");

  await assert.rejects(
    () => provider.createTransferPreview({
      sourceAccountId: "sim-checking-usd",
      destinationAccountId: "sim-wallet-usd",
      amount: { amount: "0", currency: "USD" },
    }),
    /greater than zero/,
  );
  await assert.rejects(
    () => provider.createTransferPreview({
      sourceAccountId: "sim-checking-usd",
      destinationAccountId: "sim-wallet-usd",
      amount: { amount: "1.00", currency: "EUR" },
    }),
    /matching account and amount currencies/,
  );
  await assert.rejects(
    () => provider.createTransferPreview({
      sourceAccountId: "sim-checking-usd",
      destinationAccountId: "sim-wallet-usd",
      amount: { amount: "999999999.00", currency: "USD" },
    }),
    /Insufficient simulated funds/,
  );
  await assert.rejects(() => provider.getBalance("unknown-account"), /Unknown simulated account/);
});
