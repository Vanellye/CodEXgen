# JGit 3.7.1 compatibility checkpoint

## Immutable origin

The Git Freedom Bridge carries this immutable source-history checkpoint:

`f63e166e11aee325fe0ea8504672f19134d2768b`

The checkpoint is a Git commit identity and must remain unchanged. New work descends from it; it is never rewritten to the numeric JGit version.

## Dependency alignment

The Android app declares:

`org.eclipse.jgit:org.eclipse.jgit:3.7.1.201504261725-r`

This is the exact JGit 3.7.1 artifact already used by `GitFreedomBridge`. The compatibility version and origin SHA are recorded in `GitFreedomBridge.JGIT_VERSION` and `GitFreedomBridge.ORIGIN_CHECKPOINT_SHA`. The Gradle dependency remains the source of the actual library bytes.

## Shared capability access

Android components in the CodEXgen process should obtain the bridge through:

```java
GitFreedomBridge bridge = GitFreedomBridge.shared(context);
```

This provides one process-wide instance so session authorization and local repository configuration are consistently shared across app components. Pantheon modules can request the capability through their Android adapter instead of constructing competing bridge instances.

This does **not** make the bridge globally available to unrelated Android apps, arbitrary devices, or every process in the operating system. Cross-process or cross-device access requires a separately designed authenticated service boundary, explicit user consent, and narrowly scoped permissions.

## Authorization and safety

- The shared instance does not itself authorize an operation.
- Remote operations continue to require an unlocked user token and the existing HTTPS platform gate.
- Existing branch checks, clean-worktree checks, selected-file review, and fast-forward-only pull behavior remain in force.
- No force-push, base-branch mutation, automatic merge, background remote access, or credential broadcast is added.
- JGit 3.7.1 is a legacy dependency. Keep network exposure limited and plan a reviewed upgrade; the version pin is for compatibility, not a claim of current security support.

## Preservation rule

Every subsequent integration commit must retain the complete ancestry from the origin checkpoint. Additive commits are preferred. Do not rewrite the checkpoint or discard intervening work.
