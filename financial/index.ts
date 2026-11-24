import { SimulatorProvider } from "./adapters/simulator-provider.ts";
import { ProviderRegistry } from "./registry/provider-registry.ts";

/** Builds the safe default registry: one in-memory simulator, no live adapters. */
export function createDefaultFinancialRegistry(): ProviderRegistry {
  const registry = new ProviderRegistry();
  registry.register(new SimulatorProvider());
  return registry;
}

export { SimulatorProvider } from "./adapters/simulator-provider.ts";
export { ProviderRegistry, ProviderRegistryError } from "./registry/provider-registry.ts";
export type * from "./contracts/types.ts";
export type { FinancialProvider } from "./contracts/provider.ts";
