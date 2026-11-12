# Pantheon DO.c relief gate

`DO.c` is a small C99 authorization boundary for Pantheon adapters.

- Missing approval is a hold, not an implicit yes.
- Approval must match the requested scope exactly.
- Dry-run reports intent without changing state.
- The opposite action is printed as an **UNDO proposal** only.
- This helper never executes commands, mutates Git, writes files, or controls hardware.
- A separate adapter must implement execution, logging, verification, and rollback.

## Self-test

Compile and run with:

```sh
cc -std=c99 -Wall -Wextra -Werror -DDO_C_SELF_TEST DO.c -o do-self-test
./do-self-test
```

This is a standalone Pantheon component. It is not yet wired into a Pantheon runtime entry point because no such C/C++ entry point was found in the inspected `main` tree. Integration must be performed at the actual adapter boundary and tested there.
