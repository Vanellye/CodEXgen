export type AccountKind = "asset" | "liability" | "equity" | "income" | "expense";
export interface Account { id: string; name: string; kind: AccountKind; currency: string; }
export interface Line { accountId: string; debitMinor: number; creditMinor: number; }
export interface JournalEntry { id: string; memo: string; currency: string; lines: readonly Line[]; createdAt: string; source: string; }
export interface Ledger { accounts: ReadonlyMap<string, Account>; entries: readonly JournalEntry[]; }

export function createLedger(accounts: Account[] = []): Ledger {
  const map = new Map<string, Account>();
  for (const account of accounts) {
    if (map.has(account.id)) throw new Error(`Duplicate account: ${account.id}`);
    map.set(account.id, Object.freeze({ ...account }));
  }
  return Object.freeze({ accounts: map, entries: Object.freeze([]) });
}

export function postEntry(ledger: Ledger, entry: JournalEntry): Ledger {
  if (ledger.entries.some((item) => item.id === entry.id)) throw new Error("Duplicate journal entry id");
  if (entry.lines.length < 2) throw new Error("A journal entry requires at least two lines");
  let debits = 0, credits = 0;
  for (const line of entry.lines) {
    if (!ledger.accounts.has(line.accountId)) throw new Error(`Unknown account: ${line.accountId}`);
    if (!Number.isSafeInteger(line.debitMinor) || !Number.isSafeInteger(line.creditMinor) ||
        line.debitMinor < 0 || line.creditMinor < 0 || (line.debitMinor > 0 && line.creditMinor > 0)) {
      throw new Error("Journal amounts must be non-negative integer minor units; each line is debit or credit");
    }
    debits += line.debitMinor; credits += line.creditMinor;
  }
  if (debits <= 0 || debits !== credits) throw new Error("Journal entry is not balanced");
  const frozen = Object.freeze({ ...entry, lines: Object.freeze(entry.lines.map((line) => Object.freeze({ ...line }))) });
  return Object.freeze({ accounts: ledger.accounts, entries: Object.freeze([...ledger.entries, frozen]) });
}

export function accountBalance(ledger: Ledger, accountId: string): number {
  const account = ledger.accounts.get(accountId);
  if (!account) throw new Error(`Unknown account: ${accountId}`);
  return ledger.entries.flatMap((entry) => entry.lines)
    .filter((line) => line.accountId === accountId)
    .reduce((sum, line) => sum + line.debitMinor - line.creditMinor, 0);
}
