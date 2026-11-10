# Android Application — Root Access Tablet

**Status:** policy contract; Android runtime enforcement remains adapter-specific.  
**Applies to:** app-private files, SQLite stores, Android Keystore aliases, JNI calls, and user exports.

- App-private storage does not imply unrestricted access by every feature.
- Secretum reads and writes must be scoped to an exact alias and caller purpose.
- Datorum reads and writes must be scoped to a database and record/query boundary.
- Via publication requires explicit channel-level write authorization.
- JNI/native calls must not elevate Android application permissions.
- Export, backup, deletion, key rotation, and remote transmission require distinct operation-specific review.
- Android platform permissions and app sandbox remain mandatory; a repository policy cannot grant OS permissions.
- Sensitive values must not appear in logs, diagnostics, or access tablets.

This document defines the target. It does not claim the current Android application enforces every rule.
