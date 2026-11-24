export type ExecutionMode = "SIMULATION_ONLY";

export type FinancialCapability =
  | "accounts.read"
  | "balances.read"
  | "transactions.read"
  | "transfers.preview"
  | "transfers.simulate"
  | "reconciliation.read";

export interface Money {
  /** Decimal string; never use binary floating-point for monetary values. */
  amount: string;
  /** ISO 4217 currency code. */
  currency: string;
}

export interface ProviderDescriptor {
  id: string;
  displayName: string;
  mode: ExecutionMode;
  capabilities: readonly FinancialCapability[];
}

export interface FinancialAccount {
  id: string;
  providerId: string;
  name: string;
  type: "checking" | "savings" | "wallet" | "clearing";
  currency: string;
  status: "open" | "restricted" | "closed";
}

export interface AccountBalance {
  accountId: string;
  available: Money;
  ledger: Money;
  asOf: string;
}

export interface FinancialTransaction {
  id: string;
  providerId: string;
  accountId: string;
  direction: "debit" | "credit";
  amount: Money;
  status: "posted" | "pending";
  description: string;
  createdAt: string;
  simulated: true;
}

export interface TransferDraft {
  sourceAccountId: string;
  destinationAccountId: string;
  amount: Money;
  memo?: string;
}

export interface TransferPreview {
  id: string;
  providerId: string;
  mode: ExecutionMode;
  draft: TransferDraft;
  fee: Money;
  totalDebit: Money;
  expiresAt: string;
  /** SHA-256 of the canonical preview payload. */
  digest: string;
  status: "PREVIEW";
}

export interface SimulationReceipt {
  id: string;
  previewId: string;
  providerId: string;
  mode: ExecutionMode;
  status: "SIMULATED";
  simulated: true;
  createdAt: string;
}

export interface ReconciliationSnapshot {
  providerId: string;
  mode: ExecutionMode;
  accountCount: number;
  transactionCount: number;
  generatedAt: string;
}
