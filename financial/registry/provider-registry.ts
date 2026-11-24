import { hasCapabilities, type FinancialProvider } from "./provider";
import type { FinancialCapability, ProviderDescriptor } from "./types";

export class ProviderRegistryError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ProviderRegistryError";
  }
}

/**
 * Explicit provider registry. It never chooses a substitute or silently fails
 * over to another provider when a provider is missing or lacks a capability.
 */
export class ProviderRegistry {
  readonly #providers = new Map<string, FinancialProvider>();

  register(provider: FinancialProvider): void {
    const { id, mode, capabilities } = provider.descriptor;
    if (!/^[a-z][a-z0-9-]{1,63}$/.test(id)) {
      throw new ProviderRegistryError(`Invalid provider id: ${id}`);
    }
    if (mode !== "SIMULATION_ONLY") {
      throw new ProviderRegistryError(
        "This initial registry accepts simulation-only providers; live and external sandbox modes are not enabled.",
      );
    }
    if (new Set(capabilities).size !== capabilities.length) {
      throw new ProviderRegistryError(`Provider ${id} declares duplicate capabilities.`);
    }
    if (this.#providers.has(id)) {
      throw new ProviderRegistryError(`Provider already registered: ${id}`);
    }
    this.#providers.set(id, provider);
  }

  get(providerId: string): FinancialProvider {
    const provider = this.#providers.get(providerId);
    if (!provider) {
      throw new ProviderRegistryError(`Provider not registered: ${providerId}`);
    }
    return provider;
  }

  resolve(
    providerId: string,
    requiredCapabilities: readonly FinancialCapability[] = [],
  ): FinancialProvider {
    const provider = this.get(providerId);
    if (!hasCapabilities(provider, requiredCapabilities)) {
      const missing = requiredCapabilities.filter(
        (capability) => !provider.descriptor.capabilities.includes(capability),
      );
      throw new ProviderRegistryError(
        `Provider ${providerId} lacks required capabilities: ${missing.join(", ")}`,
      );
    }
    return provider;
  }

  descriptors(): readonly ProviderDescriptor[] {
    return [...this.#providers.values()].map((provider) => ({
      ...provider.descriptor,
      capabilities: [...provider.descriptor.capabilities],
    }));
  }
}
