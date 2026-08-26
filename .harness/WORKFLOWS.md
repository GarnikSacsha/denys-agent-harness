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

Before implementation, define a commit map for the bounded task. Each planned commit names one coherent outcome, expected paths, and focused verification. The map may change when evidence changes the true boundary, but the handoff must explain the change.

For each stage:

1. state the user-visible outcome and acceptance criteria;
2. write the smallest meaningful test and confirm expected `RED`;
3. implement the minimum coherent slice to reach `GREEN`;
4. refactor safely and update the corresponding contract documents;
5. run the stage's focused verification and proportionate adjacent checks;
6. inspect the exact diff and confirm it contains only the mapped outcome;
7. produce a checkpoint or handoff with TDD evidence;
8. when local commits are authorized, selectively stage and create one descriptive atomic commit for the completed GREEN stage before beginning an independent stage;
9. confirm the remaining worktree still matches the commit map.

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

Commit history should tell the construction story. A commit is a recoverable GREEN checkpoint: do not split mechanical fragments that only work together, do not commit a broken RED state, and do not combine unrelated outcomes into a catch-all commit.

One explicit local-commit authorization for the bounded task permits all commits in its agreed commit map; it is not permission to push or to expand scope. Push, pull request, merge, release, and deployment remain separate gates.

Preserve checkpoint history. Do not squash, amend, rebase, reset, or otherwise rewrite accepted commits without explicit approval. When history is shared or pushed, use a new revert or corrective commit so the previous checkpoints remain reachable.

## Focused implementation

1. Confirm the target and relevant existing behavior.
2. State a short plan.
3. Write or update the smallest meaningful test and confirm expected `RED`.
4. Make the minimum coherent vertical change and confirm `GREEN`.
5. Refactor while keeping relevant tests green.
6. Run proportionate adjacent checks.
7. Inspect the diff.
8. Update existing project context when behavior or decisions changed.
9. Deliver the four-part handoff with TDD evidence or a pre-declared valid exception.

If the work contains several independent stages, repeat steps 3–9 for each stage instead of accumulating one large unreviewable change. When the bounded task has local-commit authorization, commit each completed GREEN stage before starting the next independent stage. Without that authorization, preserve and report the exact selective staging boundaries without committing.

## Diagnosis

1. Start from the user-visible symptom and exact route.
2. Trace the real path until the first proven divergence.
3. Reproduce minimally and safely.
4. Separate root cause, excluded alternatives, and secondary issues.
5. If implementation was requested, create and run a failing regression test before the fix.
6. Apply the minimal fix, confirm `RED → GREEN`, and verify the same route plus adjacent behavior.

## UI review

1. Inspect the actual current interface, viewport, states, and design system.
2. Evaluate hierarchy, density, clarity, language consistency, actions, empty/loading/error states, and mobile behavior.
3. Distinguish functional problems from taste improvements.
4. Propose specific changes in the existing style.
5. Verify visually after implementation when tooling allows.

## Security review gate

Use for commercial projects and any change involving authentication, authorization, customer data, secrets, uploads, payments, external providers, databases, infrastructure, deployment, or production.

1. Read the global and project security contracts, threat model, data inventory, and access matrix.
2. Identify changed trust boundaries, protected assets, actors, entry points, data flows, tools, credentials, network destinations, and side effects.
3. Verify least privilege structurally: the agent and application should lack permissions they do not need.
4. Check tenant/workspace authorization, input validation, output encoding, secret handling, logging, retention, provider disclosure, retry/idempotency, and destructive paths.
5. Confirm local/staging/production separation and that production access is absent unless explicitly authorized.
6. Run available secret, dependency, static-analysis, and focused security tests. Record unavailable checks explicitly.
7. Classify findings as critical, high, medium, or low with evidence and the affected boundary.
8. Block acceptance for unresolved critical/high findings. Record the owner and decision for deferred medium/low findings.

## Code review gate

Run after implementation and relevant tests, before commit, merge, release, or completed-stage handoff.

1. Read the task contract, acceptance criteria, project instructions, architecture contracts, and final diff.
2. Trace the real execution path instead of reviewing filenames or summaries only.
3. Review in this order:
   - correctness and user-visible behavior;
   - error, empty, retry, timeout, concurrency, and partial-failure behavior;
   - authorization, data isolation, secrets, injection, and external side effects;
   - architecture fit, duplication, coupling, replaceability, and migration safety;
   - readability, naming, size, comments, dead code, and unnecessary abstraction;
   - test quality, negative cases, production-path coverage, and false-green risk;
   - observability, cost, latency, resource bounds, and operational rollback.
4. Search specifically for hidden placeholders, hardcoded values, broad exception handling, swallowed errors, unsafe defaults, debug output, secrets, stale flags, and unrelated changes.
5. Report findings first, ordered by severity, with file/path and concrete consequence. State what was reviewed and what was not verified.
6. The author fixes accepted findings in focused changes and reruns relevant checks.
7. Repeat review only for the changed risk area; stop after the agreed acceptance gate is met.

For commercial or high-risk work, the reviewer should be independent from the implementation pass. If only one agent is available, start a fresh review pass with implementation assumptions cleared and review the diff as potentially wrong.

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
