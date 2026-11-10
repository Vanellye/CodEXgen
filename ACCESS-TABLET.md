# ERIA — Root Access Tablet

**Status:** shared access-control contract; Pantheon C++11 enforcement is implemented on `olpirt/stride-next`; provider and operating-system enforcement remain adapter-specific.  
**Applies to:** Stride 2, Pons, Secretum, Via, Datorum, Modulus, Pantheon, Framework, Android, Python services, firmware, and future registered domains.

> Read only what the invitation permits. Write only what the invitation names. A path to an object is not permission to use it.

## 1. Meaning of access

ERIA treats access as an operation against a named resource by a named subject under a specific invitation.

- **READ** means observe or retrieve the exact named resource within the granted query boundary.
- **WRITE** means create or change the exact named resource within the granted operation boundary.
- **DELETE**, **EXPORT**, **PUBLISH**, **ROTATE_KEY**, **EXECUTE**, **ACTUATE**, and **ADMINISTER** are separate consequential operations. They are not silently included in generic WRITE.
- **DISCOVER** or dependency resolution may reveal limited metadata; it does not imply READ access to provider contents.

READ and WRITE are independent. Neither implies the other.

## 2. Invitation-bound authority

Every grant must bind:
1. subject / caller identity;
2. exact resource identifier;
3. exact operation;
4. invitation ID and source;
5. immutable source revision or digest;
6. approval status;
7. expiry and revocation state.

A change to any binding field requires re-evaluation. No wildcard grant, ambient authority, inherited provider privilege, or self-issued grant is accepted by this contract.

## 3. Root domain tablet index

| Domain root | Resource boundary | READ | WRITE | Enforcement status |
|---|---|---|---|---|
| `pantheon/` | Module execution and declared resources | Exact resource + operation grant | Exact resource + operation grant; control gate separately applies | C++11 runtime gate implemented in this branch |
| `framework/` | Module contracts, adapters, jobs | Declared inputs only | Declared outputs only | Contract documented; adapters must enforce |
| `app/` | App-private data, UI state, JNI, export | Feature-scoped | Feature-scoped; export separate | Contract documented; Android adapters pending |
| `app/src/main/cpp/include/pons/` | Dependency registrations and resolution | Interface metadata | Host composition only | Pons itself does not authorize provider data |
| `app/src/main/cpp/include/olpirt/` | Configuratio, Secretum, Via, Datorum, Modulus interfaces | Provider-specific | Provider-specific | Interfaces documented; provider guards pending |
| `python/stride_core/` | JOB history, memory, observations, generation | Caller-selected scope | Explicit store/output scope | Contract documented; per-service guards pending |
| `firmware/` | Observations, configuration, device actions | Sensor/read scope | Configuration write scope; actuation separate | Contract documented; board adapter pending |

A directory tablet is a policy record, not an operating-system filesystem ACL. GitHub repository permissions and branch protections are also separate from runtime resource rights.

## 4. Provider rights

| Provider | READ | WRITE | Explicitly not implied |
|---|---|---|---|
| Stride 2 | Read caller-authorized workflow context and state | Mutate named workflow resources | Global memory access, remote dispatch |
| Pons | Inspect registered interface metadata; resolve only host-registered contracts | Bind or clear providers only during trusted host composition | Secret/data access merely by resolving an interface |
| Secretum | Read one exact secret alias | Create, rotate, or delete one exact alias under separate authorization | Enumerating secrets, exporting keys, reading unrelated aliases |
| Via | Subscribe to an exact channel when supported | Publish to an exact channel | Network access, channel administration, arbitrary broadcast |
| Datorum | Query exact database/table/record scope | Insert/update exact record scope | Full database scan, schema migration, deletion, export |
| Modulus | Inspect command metadata | Dispatch one exact registered command | Arbitrary code execution, privilege escalation, shell access |
| Pantheon | Inspect module descriptors and evidence references | Invoke an exact module after access and control gates | OS administrator rights, physical control |
| Framework | Read declared inputs | Write declared outputs | Undeclared side effects |
| Firmware | Read permitted observations | Write approved configuration | Actuation, erase, reset, or firmware update |

## 5. Runtime behavior

The Pantheon access tablet is implemented in:
- `pantheon/include/pantheon/access_tablet.hpp`
- `pantheon/src/access_tablet.cpp`
- `pantheon/include/pantheon/runtime.hpp`
- `pantheon/src/runtime.cpp`

A module declares `accessRequirements()`. The ordinary runtime path refuses modules with declared resource requirements. `executeWithAccess` requires exact matching grants for every declared operation. `executeControlledWithAccess` additionally requires the existing 38/38 evidence gate and owner-approval adapter. One missing grant denies the whole invocation.

This is in-process API-level enforcement. It does not sandbox arbitrary native code, authenticate a grant issuer, or replace OS permissions. Trusted host code must validate invitation provenance, approval identity, revocation, and time before passing grants. Each storage/network/keystore/device adapter must enforce the same decision at its actual boundary.

## 6. Default-deny rules

- Missing, unknown, stale, expired, revoked, unapproved, or mismatched grants deny.
- A READ grant never authorizes WRITE; a WRITE grant never authorizes READ.
- One denied requirement blocks the complete operation.
- Registration, naming, signatures, tags, CI success, and dependency resolution do not grant rights.
- No provider may mint or widen a caller's rights.
- Logs record decision metadata, not secret payloads or credentials.
- Historical data corrections are append-only; historical source records are not silently rewritten.
- Human approval is explicit, scoped, revocable, and separate from evidence validity.

## 7. Acceptance tests

The Pantheon native test target verifies read/write separation, missing grants, exact source binding, expiry, approval, and operation mismatch. Remaining provider adapters must add equivalent positive and negative tests before they may claim enforcement.

## 8. Implementation truth

A tablet is **specified** when its contract is documented, **implemented** when the corresponding runtime boundary consumes it, **tested** when positive and negative tests pass on the exact revision, and **independently verified** only after separate review. Do not promote a documented target to an implemented claim.

No permissions in GitHub, Android, the host OS, cloud accounts, or external systems are changed by this document or by the Pantheon API-level gate.
