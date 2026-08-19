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

## New product or major subsystem

Use this workflow when uncertainty, scope, roles, integrations, security, or reversal cost makes immediate coding risky. Skip or compress sections that do not materially apply.

### Phase 0 — documentation contract

1. Create or update the project instruction file and identify the current sources of truth.
2. Define the product outcome, narrow MVP, non-goals, roles, permissions, and primary user journeys.
3. Define important states, failure behavior, data ownership, external integrations, and acceptance criteria.
4. Document the minimum useful architecture, data model, API contracts, security model, and UI direction.
5. Record consequential choices and rejected alternatives in decision records.
6. Review the documents together for contradictions, hidden product decisions, missing failure states, and unsupported complexity.
7. Mark remaining unknowns and the exact evidence or decision required to resolve each one.

Phase 0 is documentation-only when agreed as such. Do not create application code, install dependencies, or provision infrastructure during it.

The phase is complete when the documents are sufficient to guide the next vertical slice without making major product decisions silently during implementation. Completeness does not mean predicting the whole future product.

### Phase 1 — minimal foundation

1. Create only the repository structure and foundations required by the accepted first slice.
2. Add project-local instructions for materially different areas such as backend and frontend when needed.
3. Establish configuration and secret boundaries, a minimal health path, and the smallest relevant test foundation.
4. Verify the foundation before adding product breadth.

### Phase 2 — vertical delivery

For each stage:

1. state the user-visible outcome and acceptance criteria;
2. implement one coherent slice;
3. add focused tests and update the corresponding contract documents;
4. run proportionate verification and inspect the diff;
5. produce a checkpoint or handoff;
6. when explicitly authorized, create one descriptive atomic commit for that completed stage before beginning an independent stage.

Example history:

```text
docs: establish project rules and MVP scope
docs: define roles and user flows
docs: define database and API contracts
docs: define security baseline
chore: add minimal project scaffold
feat(backend): add application foundation
feat: deliver first end-to-end user path
```

Commit history should tell the construction story. Do not split mechanical fragments that only work together, and do not combine unrelated outcomes into a catch-all commit.

## Focused implementation

1. Confirm the target and relevant existing behavior.
2. State a short plan.
3. Make the smallest coherent vertical change.
4. Add or update focused tests where useful.
5. Run proportionate checks.
6. Inspect the diff.
7. Update existing project context when behavior or decisions changed.
8. Deliver the four-part handoff.

If the work contains several independent stages, repeat steps 3–8 for each stage instead of accumulating one large unreviewable change. Commit each completed stage only when the current authorization explicitly includes commits.

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
