# Driveway DSL

Supports project and ledger declarations, account definitions, valuation rules, and review workflows.

```driveway
project "AshLedger"

ledger "primary":
    currency USD
    mode double_entry
    immutable true

account "wallet":
    type asset
    source ash_wallet
    network avalanche

account "rewards":
    type liability
    unit POINT

rule "points_value":
    1 POINT = 1 USD
    valuation_only true

workflow "reconcile":
    read accounts
    verify entries
    check balances
    require approval before posting
```

The final approval statement is a policy declaration, not an authorization token. Any future posting feature must independently obtain transaction-specific human approval.

The incomplete token "requireles" is rejected. Use "require approval before posting".

The rule 1 POINT = 1 USD is a Driveway valuation only. It does not promise redemption, move money, or override a provider's actual terms. Wallet account declarations do not connect to a live provider.
