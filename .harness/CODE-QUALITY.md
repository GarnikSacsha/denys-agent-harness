# AI-generated code quality standard

AI-generated code is untrusted implementation until it has been understood, tested, reviewed, and accepted through the real project path.

## Quality definition

Good code must be:

- correct for the stated user behavior;
- safe at trust and data boundaries;
- understandable by the next engineer without chat history;
- proportionate to the current stage;
- testable through meaningful public behavior;
- operable with useful logs, bounded failure, and rollback;
- consistent with the existing architecture and conventions;
- free of unnecessary dependencies, abstraction, duplication, and speculative scale.

Passing tests alone does not prove these properties.

## Authoring rules

- Trace the existing path before editing and preserve current contracts unless change is intentional.
- Use TDD for behavior-changing code. The required cycle is `RED → GREEN → REFACTOR`:
  1. express one observable behavior in the smallest meaningful test;
  2. run the test before implementation and confirm it fails for the intended reason;
  3. add the minimum implementation required to pass;
  4. run the target test and confirm it passes;
  5. refactor for clarity without changing behavior and keep relevant tests green.
- A test that fails because of syntax, import, fixture, environment, or unrelated setup error is not valid `RED`. The failure must demonstrate the missing or incorrect behavior.
- Do not weaken an assertion, delete a test, over-mock the path, or change expected behavior merely to obtain `GREEN`.
- Record the target test command and observed RED/GREEN result. If the red run cannot be preserved in logs, report the command and exact expected failure honestly.
- Implement one coherent vertical outcome at a time.
- Keep deterministic facts, permissions, state, arithmetic, limits, and writes in deterministic code.
- Use explicit types and schemas at system boundaries.
- Prefer small named functions/modules with one clear responsibility over large mixed files.
- Handle expected errors deliberately. Do not use broad catch-all behavior that hides failure.
- Bound network calls with timeouts, retries, backoff, cancellation, size limits, and classified errors as appropriate.
- Avoid hardcoded secrets, environment-specific URLs, magic business values, silent fallbacks, debug output, fake success, and placeholder behavior presented as complete.
- Comments explain non-obvious reasons, invariants, or risk; they do not narrate obvious syntax.
- Update existing documentation when a contract, decision, command, or deployed behavior changes.

## Language and comment conventions

- Keep programmatic identifiers and machine-readable contracts in English unless the current project explicitly defines another convention.
- Use Ukrainian for explanatory comments, docstrings, Javadoc, and TSDoc by default when working with Denys.
- A closer project instruction or an established repository/team convention may override the comment language. Do not mix languages arbitrarily inside one project.
- Comment the reason, invariant, business rule, compatibility constraint, risk, or non-obvious failure behavior. Do not restate the next line of code.
- Prefer one or two precise lines near the affected boundary. Move longer reasoning to a decision record or project documentation and link it when useful.
- Public API documentation follows the project's consumer and publication language; do not silently translate an established external contract.

Good:

```python
# Не активуємо працівника автоматично:
# адміністратор має окремо підтвердити Activation.
membership.status = MembershipStatus.PENDING
```

Avoid:

```python
# Встановлюємо статус membership у pending.
membership.status = MembershipStatus.PENDING
```

## Language-specific quality baseline

Use the existing project toolchain first. The examples below are accepted defaults for a new project, not permission to add dependencies without approval.

### Python

- Use the configured formatter and linter; Ruff is the preferred new-project default when no standard exists.
- Use explicit type annotations at public and system boundaries.
- Run the configured type checker, such as mypy or Pyright, when present or approved.
- Use pytest for behavior-focused tests unless the project already has another established framework.

### TypeScript and JavaScript

- Reuse the configured formatter and ESLint rules.
- Prefer TypeScript strict mode for new production code when the approved stack includes TypeScript.
- Keep runtime validation at untrusted boundaries; compile-time types do not validate external data.
- Use the project's established test runner and avoid introducing a second overlapping framework.

### Java

- Follow the repository's Maven or Gradle structure, supported JDK version, package conventions, and build lifecycle.
- Reuse the configured formatter and static-analysis stack, such as Spotless, Google Java Format, Checkstyle, PMD, SpotBugs, or Error Prone. Do not enable several overlapping tools merely for appearance.
- Prefer explicit domain types, constructor injection, narrow interfaces, immutable data where practical, and clear package boundaries.
- Use JUnit 5 for new tests when no established project framework conflicts; reuse the project's assertion, mocking, and integration-test conventions.
- Compile and run the relevant Maven or Gradle verification lifecycle rather than claiming success from isolated IDE checks.
- For database or external-service integration behavior, use the project's approved real dependency or containerized test boundary; do not replace meaningful integration coverage with broad mocks.

### Required quality sequence

For every supported language, determine and record real project commands for:

```text
format
lint or static analysis
typecheck or compile
targeted tests
relevant full tests
final diff review
```

Run only the commands relevant to the change, but report every required check that was not executed and why.

## Test quality

Tests should prove behavior, not implementation trivia.

Use a risk-proportionate set of:

- focused unit tests for deterministic logic;
- contract/schema tests at boundaries;
- integration tests for database/provider adapters;
- authorization and cross-tenant denial tests;
- negative tests for malformed input, timeout, partial failure, retry, and unavailable dependencies;
- regression tests for fixed bugs;
- one real-path end-to-end or staging acceptance scenario when needed to judge usefulness.

Reject false-green tests that mock away the production route, assert only that no exception occurred, duplicate implementation logic, or freeze incorrect behavior.

### TDD exceptions

An exception must be stated before implementation and is limited to work where a meaningful automated test cannot reasonably lead the change:

- documentation-only edits;
- a time-boxed research spike whose output is evidence, not production behavior;
- external platform configuration without a testable local or staging contract;
- purely visual adjustment with no changed logic, where screenshot or viewport review is the acceptance method;
- emergency containment, followed by a regression test before the fix is considered complete whenever technically possible.

"The change is small," "the code is obvious," or "tests take longer" are not exceptions. If code behavior changes and a test harness is missing, adding the smallest suitable harness is part of the task unless it requires an unapproved architectural expansion.

## Review independence

The implementing agent performs self-review, but self-review is not independent evidence.

Require an independent reviewer or fresh separated review pass for:

- commercial delivery;
- authentication, authorization, secrets, payments, customer data, uploads, database, migrations, infrastructure, deployment, and production;
- broad refactors or architectural changes;
- concurrency, retries, queues, background jobs, caching, and data lifecycle;
- large or difficult-to-reason-about diffs.

The reviewer begins from the task, contracts, and diff, not the author's claim that the change works.

## Finding severity

| Severity | Meaning | Gate |
|---|---|---|
| Critical | credible data loss, secret exposure, auth bypass, remote compromise, destructive production effect | block immediately |
| High | likely correctness/security failure on an important path or missing control before release | block acceptance |
| Medium | maintainability, resilience, test, performance, or edge-case risk needing an explicit decision | fix or record owner/rationale |
| Low | limited improvement with low present risk | may defer explicitly |

Review findings include file/path, evidence, consequence, and minimal correction. Avoid style-only noise unless it materially affects clarity or maintenance.

## Review output

A review ends with:

```text
Scope reviewed
Checks and evidence examined
Findings ordered by severity
Unverified areas
Required fixes before acceptance
Deferred items with owner/rationale
Final gate: pass / pass with recorded debt / blocked
```

No findings does not mean "perfect." It means no actionable issue was found within the stated scope and evidence.

## Acceptance gate

A material stage is complete only when:

1. acceptance criteria are met through the real path;
2. TDD evidence exists for behavior-changing code, or a valid pre-declared exception and alternative verification are recorded;
3. relevant automated and manual checks passed;
4. final diff contains no unrelated changes, secrets, or runtime data;
5. required security review passed;
6. critical/high findings are resolved;
7. documentation and handoff match the verified state;
8. remaining unknowns and debt are explicit.
