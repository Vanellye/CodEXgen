# Pantheon NEW Module

**Role:** Consent-based, provenance-preserving introspection and narrative proposal layer.  
**State:** Staged; not wired into Pantheon runtime.

## Contract

NEW accepts a record only when its source is identified, its data is public or a consented privacy-preserving aggregate, its permission basis and purpose are present, the record is minimized, and provenance metadata is available.

NEW emits an **unreviewed narrative proposal**. It does not publish, contact people, monitor private streams, or initiate actions.

## Components

- `NEW.h`: narrow C interface and data contracts.
- `NEW.c`: fail-closed validation and proposal construction.
- `tests/test_NEW.c`: basic contract tests.

## Build and test

```sh
cc -std=c99 -Wall -Wextra -Werror -Ipantheon/NEW pantheon/NEW/NEW.c pantheon/NEW/tests/test_NEW.c -o /tmp/new-test
/tmp/new-test
```

Before runtime integration, review the source adapter and permission model, add privacy and minimization tests, verify provenance and correction-chain behavior, review narrative outputs for unsupported claims, and obtain human approval for the exact integration scope.

No source connector, crawler, account access, or autonomous publication is included.
