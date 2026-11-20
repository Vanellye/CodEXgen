# Cross-provider bridge and mirror projection

## Mirror branch
The branch `mirror/ruble-i-v4-baseline` is a Git branch projection of the v4 baseline commit. It preserves the existing tree and history ancestry; it is not a separately synchronized full mirror of all refs, forks, LFS objects, issues, secrets, or provider data. Never mirror credentials, private keys, access tokens, or personal financial data into Git.

## Hybrid allowance flow
1. Import balance evidence separately from each connected provider.
2. Validate source, account reference, currency, observation time, freshness, ownership/verification state, and evidence reference.
3. Compute available amount after explicit reserves.
4. Cap the shared pool at the lower of configured pool cap, rolling-period cap, and verified available funds.
5. Deduct already allocated/used amounts.
6. Apply per-beneficiary period cap, per-transfer cap, and requested amount.
7. Emit a deterministic, expiring proposal digest.
8. Require an independent signature for the exact proposal and policy before recording an allocation grant.

## Provider isolation
The bridge normalizes transfer intent metadata only. Wise and Plaid retain separate credentials, scopes, account verification, rail eligibility, recipient checks, transfer lifecycle, webhook keys, and reconciliation. Provider balance data is not transferable permission and is never merged into a fictional single account.

## Scheduled allocation
The policy template declares scheduled allocation, but no schedule, amounts, beneficiaries, or provider credentials are configured. Scheduling may prepare proposals; it must not automatically approve or submit them.

## Launch mode
`PREPARE_ONLY`. The live submit gate remains false. Production activation requires a separate reviewed change after every launch gate has independently passed.
