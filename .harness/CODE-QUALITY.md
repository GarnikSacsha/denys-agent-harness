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
- Implement one coherent vertical outcome at a time.
- Keep deterministic facts, permissions, state, arithmetic, limits, and writes in deterministic code.
- Use explicit types and schemas at system boundaries.
- Prefer small named functions/modules with one clear responsibility over large mixed files.
- Handle expected errors deliberately. Do not use broad catch-all behavior that hides failure.
- Bound network calls with timeouts, retries, backoff, cancellation, size limits, and classified errors as appropriate.
- Avoid hardcoded secrets, environment-specific URLs, magic business values, silent fallbacks, debug output, fake success, and placeholder behavior presented as complete.
- Comments explain non-obvious reasons, invariants, or risk; they do not narrate obvious syntax.
- Update existing documentation when a contract, decision, command, or deployed behavior changes.

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
2. relevant automated and manual checks passed;
3. final diff contains no unrelated changes, secrets, or runtime data;
4. required security review passed;
5. critical/high findings are resolved;
6. documentation and handoff match the verified state;
7. remaining unknowns and debt are explicit.
