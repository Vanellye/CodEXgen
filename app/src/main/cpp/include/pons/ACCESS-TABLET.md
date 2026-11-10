# Pons — Provider Access Tablet

**Status:** provider-boundary policy contract.  
**Applies to:** the Pons dependency container and interfaces it resolves.

Pons resolves interfaces; it does not itself authorize access to provider data.

| Pons behavior | Policy |
|---|---|
| `contains<Interface>()` | Metadata inspection only; does not expose provider data |
| `resolve<Interface>()` | Dependency acquisition, not a data-read grant |
| `bind<Interface>()` | Host-controlled composition setup; never callable as a user-data write grant |
| `clear()` | Destructive container mutation; host lifecycle operation only |

The resolved interface must enforce its own read/write checks. Secretum, Via, Datorum, and Modulus must not treat successful resolution as permission to read secrets, publish events, mutate records, or dispatch commands.

Pons currently has no access-tablet parameter in its public API. Do not claim enforcement at the container layer until the adapter is implemented and tested. The header's C++ language requirements must also be reconciled with the C++11 native build before it is linked into that target.
