# Driveway DSL (starter grammar)

This starter parser supports project and ledger declarations, basic account/rule/workflow sections, and intentionally rejects unknown statements.

```driveway
project "AshLedger"
ledger "primary":
currency USD
mode double_entry
immutable true

accounts:
- cash Cash asset USD
- points Rewards liability POINT

rules:
- 1 POINT = 1 USD
- valuation_only true

workflow "reconcile":
- read accounts
- compare provider snapshot
- require human approval before posting
```

The DSL is a configuration language, not an authorization system. The runtime must validate every instruction independently.
