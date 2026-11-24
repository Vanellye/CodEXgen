import type { FinancialProvider } from "../contracts/provider.ts";
import type {
  AccountBalance,
  FinancialAccount,
  FinancialTransaction,
  ProviderDescriptor,
  ReconciliationSnapshot,
  SimulationReceipt,
  TransferDraft,
  TransferPreview,
} from "../contracts/types.ts";

const SCALE = 8n;
const SCALE_FACTOR = 10n ** SCALE;
const PREVIEW_TTL_MS = 5 * 60 * 1000;

function toUnits(money: { amount: string; currency: string }): bigint {
  if (!/^(0|[1-9][0-9]*)(\.[0-9]{1,8})?$/.test(money.amount)) {
    throw new Error("Money amount must be a non-negative decimal string with at most 8 fractional digits.");
  }
  const [whole, fraction = ""] = money.amount.split(".");
  return BigInt(whole) * SCALE_FACTOR + BigInt(fraction.padEnd(Number(SCALE), "0"));
}

function fromUnits(units: bigint, currency: string): { amount: string; currency: string } {
  if (units < 0n) throw new Error("Money amount cannot be negative.");
  const whole = units / SCALE_FACTOR;
  const fraction = (units % SCALE_FACTOR).toString().padStart(Number(SCALE), "0").replace(/0+$/, "");
  return { amount: fraction ? `${whole}.${fraction}` : whole.toString(), currency };
}

function clone<T>(value: T): T {
  return structuredClone(value);
}

async function sha256(value: string): Promise<string> {
  if (!globalThis.crypto?.subtle) {
    throw new Error("Web Crypto SHA-256 is required to create an immutable transfer preview.");
  }
  const bytes = new TextEncoder().encode(value);
  const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

interface StoredPreview {
  value: TransferPreview;
  consumed: boolean;
}

export class SimulatorProvider implements FinancialProvider {
  readonly descriptor: ProviderDescriptor = Object.freeze({
    id: "internal_simulator",
    displayName: "ERIA In-Memory Financial Simulator",
    mode: "SIMULATION_ONLY",
    capabilities: Object.freeze([
      "accounts.read",
      "balances.read",
      "transactions.read",
      "transfers.preview",
      "transfers.simulate",
      "reconciliation.read",
    ] as const),
  });

  readonly #accounts: FinancialAccount[] = [
    {
      id: "sim-checking-usd",
      providerId: "internal_simulator",
      name: "Synthetic Checking",
      type: "checking",
      currency: "USD",
      status: "open",
    },
    {
      id: "sim-wallet-usd",
      providerId: "internal_simulator",
      name: "Synthetic Wallet",
      type: "wallet",
      currency: "USD",
      status: "open",
    },
  ];

  readonly #balances = new Map<string, bigint>([
    ["sim-checking-usd", toUnits({ amount: "10000.00", currency: "USD" })],
    ["sim-wallet-usd", toUnits({ amount: "2500.00", currency: "USD" })],
  ]);

  readonly #transactions: FinancialTransaction[] = [];
  readonly #previews = new Map<string, StoredPreview>();

  async listAccounts(): Promise<readonly FinancialAccount[]> {
    return clone(this.#accounts);
  }

  async getBalance(accountId: string): Promise<AccountBalance> {
    const account = this.#requireOpenAccount(accountId);
    const units = this.#balances.get(accountId);
    if (units === undefined) throw new Error(`No simulated balance for account ${accountId}.`);
    const amount = fromUnits(units, account.currency);
    return {
      accountId,
      available: amount,
      ledger: clone(amount),
      asOf: new Date().toISOString(),
    };
  }

  async listTransactions(accountId: string): Promise<readonly FinancialTransaction[]> {
    this.#requireOpenAccount(accountId);
    return clone(this.#transactions.filter((transaction) => transaction.accountId === accountId));
  }

  async createTransferPreview(draft: TransferDraft): Promise<TransferPreview> {
    const source = this.#requireOpenAccount(draft.sourceAccountId);
    const destination = this.#requireOpenAccount(draft.destinationAccountId);
    if (source.id === destination.id) throw new Error("Source and destination accounts must differ.");
    if (source.currency !== destination.currency || source.currency !== draft.amount.currency) {
      throw new Error("Simulator transfers require matching account and amount currencies.");
    }
    const amount = toUnits(draft.amount);
    if (amount <= 0n) throw new Error("Transfer amount must be greater than zero.");
    const available = this.#balances.get(source.id) ?? 0n;
    const feeUnits = 0n;
    if (available < amount + feeUnits) throw new Error("Insufficient simulated funds.");

    const normalizedDraft: TransferDraft = {
      sourceAccountId: source.id,
      destinationAccountId: destination.id,
      amount: fromUnits(amount, source.currency),
      ...(draft.memo ? { memo: draft.memo.trim().slice(0, 140) } : {}),
    };
    const fee = fromUnits(feeUnits, source.currency);
    const totalDebit = fromUnits(amount + feeUnits, source.currency);
    const expiresAt = new Date(Date.now() + PREVIEW_TTL_MS).toISOString();
    const id = globalThis.crypto.randomUUID();
    const payload = {
      id,
      providerId: this.descriptor.id,
      mode: "SIMULATION_ONLY" as const,
      draft: normalizedDraft,
      fee,
      totalDebit,
      expiresAt,
      status: "PREVIEW" as const,
    };
    const preview: TransferPreview = { ...payload, digest: await sha256(JSON.stringify(payload)) };
    this.#previews.set(id, { value: preview, consumed: false });
    return clone(preview);
  }

  async simulateTransfer(previewId: string): Promise<SimulationReceipt> {
    const stored = this.#previews.get(previewId);
    if (!stored) throw new Error("Unknown simulated transfer preview.");
    if (stored.consumed) throw new Error("Transfer preview has already been consumed.");
    if (Date.parse(stored.value.expiresAt) <= Date.now()) throw new Error("Transfer preview has expired.");

    const { draft } = stored.value;
    const source = this.#requireOpenAccount(draft.sourceAccountId);
    const destination = this.#requireOpenAccount(draft.destinationAccountId);
    const amount = toUnits(draft.amount);
    const sourceBalance = this.#balances.get(source.id) ?? 0n;
    const destinationBalance = this.#balances.get(destination.id) ?? 0n;
    if (sourceBalance < amount) throw new Error("Insufficient simulated funds at execution time.");

    // This mutates only this adapter's in-memory synthetic ledger.
    stored.consumed = true;
    this.#balances.set(source.id, sourceBalance - amount);
    this.#balances.set(destination.id, destinationBalance + amount);
    const createdAt = new Date().toISOString();
    const transferId = globalThis.crypto.randomUUID();
    this.#transactions.push(
      {
        id: `${transferId}-debit`,
        providerId: this.descriptor.id,
        accountId: source.id,
        direction: "debit",
        amount: clone(draft.amount),
        status: "posted",
        description: draft.memo || `Simulated transfer to ${destination.name}`,
        createdAt,
        simulated: true,
      },
      {
        id: `${transferId}-credit`,
        providerId: this.descriptor.id,
        accountId: destination.id,
        direction: "credit",
        amount: clone(draft.amount),
        status: "posted",
        description: draft.memo || `Simulated transfer from ${source.name}`,
        createdAt,
        simulated: true,
      },
    );

    return {
      id: transferId,
      previewId,
      providerId: this.descriptor.id,
      mode: "SIMULATION_ONLY",
      status: "SIMULATED",
      simulated: true,
      createdAt,
    };
  }

  async getReconciliationSnapshot(): Promise<ReconciliationSnapshot> {
    return {
      providerId: this.descriptor.id,
      mode: "SIMULATION_ONLY",
      accountCount: this.#accounts.length,
      transactionCount: this.#transactions.length,
      generatedAt: new Date().toISOString(),
    };
  }

  #requireOpenAccount(accountId: string): FinancialAccount {
    const account = this.#accounts.find((candidate) => candidate.id === accountId);
    if (!account) throw new Error(`Unknown simulated account: ${accountId}`);
    if (account.status !== "open") throw new Error(`Account is not open: ${accountId}`);
    return account;
  }
}
