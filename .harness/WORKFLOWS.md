# Standard workflows

## Read-only orientation

1. Resolve the real repository root, branch, worktree, and uncommitted changes.
2. Read project instructions and the files closest to the requested behavior.
3. Identify entry points, data flow, persistence, integrations, tests, and real commands.
4. Compare documents with code and observable behavior.
5. Report architecture, proven facts, risks, and the smallest useful next vertical slice.
6. Do not create scaffolding or edit files.

## Feature planning

1. Describe the user-visible outcome.
2. Define the narrow first end-to-end scenario.
3. Record in-scope, out-of-scope, states, errors, data, and acceptance criteria.
4. Inspect the current architecture and identify the smallest fitting change.
5. Separate product decisions requiring Denys from implementation decisions the agent can make.
6. Define verification before implementation.

## Focused implementation

1. Confirm the target and relevant existing behavior.
2. State a short plan.
3. Make the smallest coherent vertical change.
4. Add or update focused tests where useful.
5. Run proportionate checks.
6. Inspect the diff.
7. Update existing project context when behavior or decisions changed.
8. Deliver the four-part handoff.

## Diagnosis

1. Start from the user-visible symptom and exact route.
2. Trace the real path until the first proven divergence.
3. Reproduce minimally and safely.
4. Separate root cause, excluded alternatives, and secondary issues.
5. If implementation was requested, create a regression test and minimal fix.
6. Verify the same route plus adjacent behavior.

## UI review

1. Inspect the actual current interface, viewport, states, and design system.
2. Evaluate hierarchy, density, clarity, language consistency, actions, empty/loading/error states, and mobile behavior.
3. Distinguish functional problems from taste improvements.
4. Propose specific changes in the existing style.
5. Verify visually after implementation when tooling allows.

## Checkpoint and handoff

For long work, maintain:

```text
Goal
Current repository/worktree/branch
User-visible state
Proven facts
Accepted decisions
Changed files
Checks and results
Uncommitted state
Risks/unknowns
Exact next step
```

For a new chat, include ports, runtime/deployment state, configuration requirements, and commands needed to continue.

## Harness improvement loop

Update the Harness only when:

- the same agent mistake repeats;
- the same review feedback repeats;
- agents repeatedly read the wrong files;
- a critical rule needs deterministic enforcement;
- a workflow is repeatedly reconstructed.

Prefer a test, lint rule, script, or permission control over adding another paragraph when technical enforcement is possible.
