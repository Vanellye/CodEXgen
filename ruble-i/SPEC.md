# ₽.ı Language Specification — v0.1

## 1. Purpose

Ruble-I (₽.ı) describes deterministic ledger simulations and provenance-bearing evidence. It separates value accounts and balances; allowances and their time windows; currency/token exchange quotes; science and source-code interpretation records; and audit history and authorization evidence.

The language is not a bank, wallet, exchange, mint, custody service, or payment network.

## 2. Lexical and numeric rules

- Source files use UTF-8 and the .rubi suffix.
- Identifiers are ASCII letters, digits, underscore, and hyphen.
- Currency identifiers are explicit ISO-4217 codes in this prototype; token symbols use a separately declared TOKEN asset class.
- All amounts are positive integer minor units. Floating-point amounts are forbidden.
- Rates are rational integers: numerator / denominator. Decimal floats are forbidden.
- Timestamps are RFC 3339 UTC.
- Every transaction and evidence object has a unique ID.

## 3. Initial grammar

    PROGRAM       := MODE DECLARATION*
    MODE          := SIMULATE
    DECLARATION   := ACCOUNT | ALLOWANCE | TRANSFER | QUOTE | EXCHANGE | EVIDENCE
    ACCOUNT       := ACCOUNT ID ASSET INTEGER
    ALLOWANCE     := ALLOWANCE ID FROM ID TO ID INTEGER ASSET EVERY PERIOD
    TRANSFER      := TRANSFER ID FROM ID TO ID INTEGER ASSET PURPOSE STRING
    QUOTE         := QUOTE ID ASSET TO ASSET RATE INTEGER / INTEGER AT TIMESTAMP EXPIRES TIMESTAMP SOURCE STRING
    EXCHANGE      := EXCHANGE ID FROM ID TO ID INTEGER ASSET USING ID
    EVIDENCE      := EVIDENCE ID KIND STRING SOURCE STRING DIGEST HEX64 AT TIMESTAMP

Comments begin with #. The parser accepts the canonical line-oriented form shown in the example.

## 4. Semantics

- An account is denominated in exactly one asset. No implicit cross-currency balance is allowed.
- Transfers debit and credit the same asset and must be fully funded.
- An allowance moves a bounded amount from its source account to its destination account when the declared period is evaluated. It is not a transfer instruction to a provider.
- A quote is evidence of a conversion rate, not a guarantee of execution. Exchange requires matching quote assets and a non-expired quote.
- Conversion uses integer arithmetic and a declared floor-rounding rule. Remainders are recorded; they are never silently redistributed.
- A token is a distinct ledger asset. Token minting/issuance is not part of v0.1. No external token is created.
- Every state-changing simulation event appends a hash-chained record. Corrections are new compensating events.
- Scientific datasets, code interpretations, and benchmark records live in an evidence namespace and never alter balances.
- Future hourly payload allocation is represented as a period-scoped allowance with an explicit cap and source. It cannot imply an unbounded recurring grant.

## 5. Authorization migration

PONS and comparable legacy authorization implementations are marked RETIRED_FOR_NEW_RUBLI_GRANTS only after a separately reviewed migration. Their original commits, signatures, decisions, revocations, and evidence references remain in the historical index.

A historical approval is not a Ruble-I permission. New privileged operations require a new, independent authorization contract bound to the exact operation, accounts, asset, amount, fee ceiling, expiry, nonce, and policy version. Missing or unverifiable evidence means HOLD.

## 6. Non-goals and prohibitions

- No live bank or payment API.
- No wallet key handling, token minting, or exchange order placement.
- No automatic account acquisition, beneficiary discovery, or account ownership inference.
- No bypass of account protections, sanctions screening, fraud checks, or human confirmation.
- No deletion or rewriting of historical audit records.
- No claim of quantum speedup without measured reproducible evidence.

## 7. Determinism and acceptance

Given identical source, initial balances, quote evidence, and clock input, the simulator must produce byte-identical event payloads and the same final balances. Tests must cover insufficient funds, duplicate IDs, mismatched assets, expired quotes, invalid rates, overflow, and hash-chain tampering.