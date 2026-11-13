/*
 * ERIA / Pantheon DO.c — authorization and recovery gate
 *
 * Scope: standalone C99 policy helper. This file does not execute shell
 * commands, mutate files, write Git refs, or actuate external systems.
 *
 * "DO" requires an explicit, scope-matching approval.
 * The opposite is printed as a proposed "UNDO" plan; it is never executed.
 */

#include <stdio.h>
#include <string.h>

typedef enum {
    DO_DENIED = 0,
    DO_APPROVED = 1
} DoDecision;

typedef struct {
    const char *action;
    const char *scope;
    const char *approval_scope;
    int approval_present;
    int dry_run;
} DoRequest;

static int nonempty(const char *value) {
    return value != NULL && value[0] != '\0';
}

DoDecision do_authorize(const DoRequest *request) {
    if (request == NULL) return DO_DENIED;
    if (!nonempty(request->action) || !nonempty(request->scope))
        return DO_DENIED;
    if (!request->approval_present) return DO_DENIED;
    if (!nonempty(request->approval_scope)) return DO_DENIED;
    if (strcmp(request->scope, request->approval_scope) != 0)
        return DO_DENIED;
    return DO_APPROVED;
}

/*
 * Print the inverse as a human-reviewable proposal only.
 * Callers must supply a verified recovery description; this function
 * deliberately does not infer or run a destructive inverse operation.
 */
void do_print_opposite(const char *action, const char *recovery_plan) {
    if (!nonempty(action) || !nonempty(recovery_plan)) {
        puts("UNDO: unavailable — recovery plan not supplied.");
        return;
    }
    printf("UNDO proposal for [%s]: %s\n", action, recovery_plan);
    puts("Status: NOT EXECUTED; requires separate human approval.");
}

/* Returns 0 only when the request is authorized. */
int do_relief(const DoRequest *request) {
    if (request == NULL) {
        puts("HOLD: missing request; no action taken.");
        return 1;
    }

    if (request->dry_run) {
        printf("DRY-RUN: would evaluate action [%s] in scope [%s].\n",
               nonempty(request->action) ? request->action : "(missing)",
               nonempty(request->scope) ? request->scope : "(missing)");
        puts("No state change performed.");
        return 0;
    }

    if (do_authorize(request) != DO_APPROVED) {
        puts("HOLD: approval absent, invalid, or outside requested scope.");
        puts("No state change performed.");
        return 1;
    }

    puts("APPROVED: authorization gate passed for the declared scope.");
    puts("Execution remains the responsibility of a separately reviewed adapter.");
    return 0;
}

#ifdef DO_C_SELF_TEST
int main(void) {
    DoRequest missing = {"publish", "main", NULL, 0, 0};
    DoRequest wrong_scope = {"publish", "main", "feature", 1, 0};
    DoRequest approved = {"review", "pantheon", "pantheon", 1, 0};

    if (do_authorize(&missing) != DO_DENIED) return 1;
    if (do_authorize(&wrong_scope) != DO_DENIED) return 2;
    if (do_authorize(&approved) != DO_APPROVED) return 3;

    do_relief(&missing);
    do_print_opposite("publish", "restore the recorded prior commit by reviewed revert");
    return 0;
}
#endif
