/**
 * Financial Tunnel composition entry point.
 * The provider contract and explicit registry are implemented in ../financial.
 * External identity and authorization run as an independent service under ./external-profile.
 */
export {
  createDefaultFinancialRegistry,
  ProviderRegistry,
  ProviderRegistryError,
  SimulatorProvider,
} from "../financial/index.ts";
export type * from "../financial/contracts/types.ts";
export type { FinancialProvider } from "../financial/contracts/provider.ts";
