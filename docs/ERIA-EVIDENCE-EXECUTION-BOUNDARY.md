# ERIA Evidence and Execution Boundary

## Purpose

This proposal adds an offline evidence verifier and a Bash adapter. It records whether a supplied evidence bundle satisfies ERIA's declared requirements for a named action and exact source commit. It does **not** perform, trigger, authorize by itself, or prove the real-world completion of that action.

Related governance work:
- [PR #61 — Human approval gate and bounded auto-development](https://github.com/Vanellye/CodEXgen/pull/61)
- [PR #63 — ASH-backed manifest fusion and Bash bridge](https://github.com/Vanellye/CodEXgen/pull/63)

This branch is based on original anchor commit `0b134ed2770c789e42e850ea7be4228c4514b989`. It is a separate proposal; it does not merge either related PR.

## Action classes

The verifier recognizes `ci`, `merge`, `deployment`, `release`, `external_dispatch`, `hardware_activation`, and `biological_intervention`.

- CI requires a successful conclusion tied to the exact workflow commit SHA.
- Merge requires an explicit merged state and a full merge commit SHA.
- Deployment requires success, environment, and a deployed SHA equal to the subject SHA.
- Release requires a published state and a release tag.
- External dispatch requires a dispatch event ID and destination.
- Hardware activation requires a device identifier and independent attestation reference.
- Biological intervention requires a protocol ID/version, ethics approval reference, and attestation reference.
- Every consequential action requires a human approval record bound to the exact action and subject SHA. The approver must differ from the recorded actor.

## Run locally

```bash
python3 -m unittest discover -s eria/evidence-execution-boundary/tests -v
bash -n eria/evidence-execution-boundary/verify_evidence.sh
bash eria/evidence-execution-boundary/verify_evidence.sh evidence-record.json FULL_40_CHARACTER_COMMIT_SHA
```

A successful result means only that the supplied JSON passes these local structural and policy checks. It is not a command to proceed.

## Trust limitations

The issuer, actor, approval identity, source URL, and event identifiers are supplied data. This implementation does not call GitHub or other providers, verify cryptographic signatures, authenticate a human, inspect a device, verify an ethics board, or independently confirm an event. A policy issuer allowlist is a configuration filter, not cryptographic provenance. Production use must add trusted provider verification and authenticated reviewer/device attestations before treating records as proof.

A successful verifier result must never be interpreted as authorization to execute. Evidence acceptance and action authorization are separate decisions.

## Hard boundary

The verifier and shell adapter are read-only. They do not:
- merge branches, deploy, publish releases, or create tags;
- send webhooks, dispatch events, or contact external destinations;
- extract secrets or credentials;
- execute commands embedded in evidence;
- activate hardware or interact with biological systems;
- modify repository refs, files, or remote state.

Missing, malformed, stale, mismatched, or untrusted evidence fails closed. There is no force/bypass flag. Human review remains external and explicit.

## Review checklist

- [ ] Inspect the schema, verifier, policy, tests, and Bash adapter.
- [ ] Run the local test commands above.
- [ ] Confirm CI on the exact final PR head.
- [ ] Independently verify upstream evidence authenticity before any operational reliance.
- [ ] Obtain human approval for this exact PR diff before merge.

Draft only. No merge, release, deployment, external dispatch, hardware activation, or biological intervention is authorized or performed by this PR.
