# Pantheon contract validation and runtime boundary

## Governing authorization contract

Pantheon is governed by the repository-wide [ĎÏÎ§Ŝ authorization-and-patch gate](../docs/DISCS-AUTHORIZATION-AND-PATCH-GATE.md) and [application matrix](../docs/DISCS-REPOSITORY-WIDE-APPLICATION.md). The same non-inheritance rules apply to every Pantheon C contract, Android adapter, and future native binding: a valid envelope or detected trigger is not permission to execute, mutate, publish, or transmit.

## Contract test suite

Run from the repository root:

```sh
bash pantheon/run-contract-tests.sh
```

The script compiles each standalone C99 contract with `-Wall -Wextra -Werror`
and runs its test program. It includes DO, factual logic, NEW, FaCADE,
THOUGHT_TOTT, Z_TO_A, RHYTHMATIC_REMEDY, I_INJECT, Walla Drop-Out,
Walla Regurgitation, and Y bypass. It does not claim that these modules have
been composed into one native executable; they remain independently testable
contracts with deliberately separate responsibilities.

## Android runtime boundary

`app/src/main/java/com/vanellye/eria/pantheon/PantheonRuntimeGate.kt`
adapts the existing `DataEnvelopeValidator` to the Android app. It can only
return a hold or a review-ready record. It has no action executor and always
reports `actionTaken=false`.

The upstream authorization fields remain assertions supplied by the caller;
this adapter does not cryptographically authenticate an approver, validate
legal consent, or prove source truth. `REVIEW_READY` means only that the
envelope passed the local structural checks, declared scope matched exactly,
and the caller recorded human-review confirmation. A separate human decision
and separately reviewed adapter are required before any consequential action.

## Explicitly not integrated

The C modules are not yet built as an Android native library and are not
invoked through JNI. No wallet, network, file, Git, hardware, publishing,
or process-execution adapter is enabled by the Pantheon runtime gate. Native binding requires a separately
reviewed NDK/CMake integration and ABI tests. This change intentionally
establishes a safe Android review boundary without pretending that C contract
formatters are cryptographic authorization services.

The repository also contains a separate Git bridge with remote and local
side-effecting methods. Those methods are **not yet enforced by a ĎÏÎ§Ŝ
operation-specific approval object**; see the application matrix. The presence
of this Pantheon gate must not be interpreted as a gate around unrelated
adapters.
