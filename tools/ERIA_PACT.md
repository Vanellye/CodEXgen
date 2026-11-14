# ERIA-PACT — PONS Authorized Change Transaction Language

ERIA-PACT/1 is a small declarative language, not a shell or general-purpose scripting interface.

## Program form

    APPLY PATCH <patch-grant-id>
    COMMIT MESSAGE "<commit message>"
    PUSH BRANCH "<feature-branch>" EXPECT "<40-character-remote-sha>"
    MERGE PR <number> METHOD "<merge|squash|rebase>" EXPECT "<40-character-pr-head-sha>"
    DEPLOY WORKFLOW "<allowlisted-workflow-id>" REF "<feature-branch>"

The first operation is required. Later operations are optional but ordered. PUSH requires COMMIT; MERGE requires PUSH; DEPLOY requires MERGE. Unknown statements, duplicates, and arbitrary commands are rejected.

## Authorization and execution

The source proposal grant authorizes patch preparation. A second human grant authorizes the exact patch hash. A PACT request then hashes the entire program and canonical execution plan, binding it to the patch grant, repository, branch, HEAD, and exact paths. A human must enter AUTHORIZE EXECUTION plus the first 12 hexadecimal characters of the plan hash. Each operation receives its own PONS capability within that exact transaction.

APPLY performs git apply --check and then applies only the stored patch bytes. COMMIT stages only approved paths. PUSH verifies the expected remote SHA and uses a normal non-force push. MERGE checks PR identity, branch, head SHA, and prohibits main/master targets. DEPLOY dispatches only workflow IDs explicitly allowlisted in ~/.eria/executor-policy.json; GitHub environment protections still apply.

Remote operations require ERIA_GITHUB_REPOSITORY=owner/repository and GITHUB_TOKEN. Never store tokens in source or SQLite.

Default deployment policy:

    {"allow_deployments": false, "allowed_deployment_workflows": []}

The operations are sequential, not globally atomic. If a later step fails, earlier successful steps are not automatically rolled back. Every result is recorded in append-only PACT history. No force push, reset, clean, checkout, arbitrary shell, or main/master write is supported.
