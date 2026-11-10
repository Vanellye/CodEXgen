# Firmware — Root Access Tablet

**Status:** policy contract; no board-specific permission enforcement is implied.  
**Applies to:** observation sources, local storage, communications, configuration, and actuator adapters.

- Sensor/observation reads are distinct from configuration writes.
- Firmware configuration writes require a device-local, authenticated, scoped grant.
- Network send, firmware update, erase, reset, and actuator commands are distinct operations; generic write permission does not authorize them.
- Loss of authorization, clock trust, or policy evidence must enter the documented safe state.
- No tablet grants physical actuation by itself.
- Board, boot chain, secure storage, and hardware interlocks must independently enforce platform-specific rights.

This document is not a firmware implementation or safety certification.
