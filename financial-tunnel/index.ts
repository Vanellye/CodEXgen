/**
 * Financial Tunnel composition entry point.
 * The shared provider contract and explicit registry are implemented in ../financial.
 * No PONS services or external provider connections are required.
 */
export {
  createDefaultFinancialRegistry,
  ProviderRegistry,
  ProviderRegistryError,
  SimulatorProvider,
} from "../financial/index.ts";
export type * from "../financial/contracts/types.ts";
export type { FinancialProvider } from "../financial/contracts/provider.ts";
