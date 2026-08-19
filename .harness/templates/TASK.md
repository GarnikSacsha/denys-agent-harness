# Task contract

## User-visible goal

[What becomes possible for the user?]

## Scope

- In scope:
- Out of scope:

## Current evidence

- Known facts:
- Assumptions to verify:
- Relevant paths:

## Permissions

- Local edits: [allowed/not allowed]
- New dependencies: [allowed/approval required]
- Paid calls: [allowed with cap/approval required]
- Commit/push/PR/deploy: [explicit status]

## Acceptance criteria

- [ ] Real end-to-end behavior
- [ ] Error/empty/loading state as relevant
- [ ] Targeted verification
- [ ] TDD evidence recorded for behavior-changing code (`RED → GREEN → REFACTOR`)
- [ ] Any TDD exception was declared before implementation with alternative verification
- [ ] Diff review
- [ ] Documentation/checkpoint updated if needed
- [ ] Security review completed when the change crosses a protected boundary
- [ ] Self-review completed; independent review completed when required by risk
- [ ] Critical/high review findings resolved

## Security and review boundary

- Data classification involved: [public / internal / confidential / restricted / none]
- Environments touched: [local / staging / production]
- Credentials available: [none / scoped local / scoped staging / other explicitly approved]
- External destinations: [none / allowlisted list]
- Database effects: [none / read / scoped writes / migration]
- Independent reviewer: [not required / agent or person]

## TDD contract

- Behavior under test:
- Target test path/name:
- RED command and expected failure:
- GREEN command and result:
- REFACTOR/adjacent checks:
- Exception, if valid and declared before implementation:

## Budget and stopping

- Maximum repair cycles without new evidence: 3
- External spending cap: $0 unless explicitly changed
- Stop for product decisions, permission expansion, or scope conflict
