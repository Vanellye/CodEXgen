import type {
  AccountBalance,
  FinancialAccount,
  FinancialCapability,
  FinancialTransaction,
  ProviderDescriptor,
  ReconciliationSnapshot,
  SimulationReceipt,
  TransferDraft,
  TransferPreview,
} from "./types.ts;

export interface FinancialProvider {
  readonly descriptor: ProviderDescriptor;

  listAccounts(): Promise<readonly FinancialAccount[]>;
  getBalance(accountId: string): Promise<AccountBalance>;
  listTransactions(accountId: string): Promise<readonly FinancialTransaction[]>;
  createTransferPreview(draft: TransferDraft): Promise<TransferPreview>;

  /** Simulation-only operation. This method must never call an external provider. */
  simulateTransfer(previewId: string): Promise<SimulationReceipt>;

  getReconciliationSnapshot(): Promise<ReconciliationSnapshot>;
}

export function hasCapabilities(
  provider: FinancialProvider,
  required: readonly FinancialCapability[],
): boolean {
  const available = new Set(provider.descriptor.capabilities);
  return required.every((capability) => available.has(capability));
}
