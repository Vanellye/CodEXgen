import { SimulatorProvider } from "./adapters/simulator-provider";
import { ProviderRegistry } from "./registry/provider-registry";

/** Builds the safe default registry: one in-memory simulator, no live adapters. */
export function createDefaultFinancialRegistry(): ProviderRegistry {
  const registry = new ProviderRegistry();
  registry.register(new SimulatorProvider());
  return registry;
}

export { SimulatorProvider } from "./adapters/simulator-provider";
export { ProviderRegistry, ProviderRegistryError } from "./registry/provider-registry";
export type * from "./contracts/types";
export type { FinancialProvider } from "./contracts/provider";
