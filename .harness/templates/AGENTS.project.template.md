# Project operating instructions

## Project outcome

[One or two sentences describing the real user result.]

## Current stage and scope

- Stage: [prototype / MVP / pilot / production]
- In scope: [current product boundary]
- Out of scope: [explicit exclusions]

## Stack and runtime

- Language/framework: [actual stack]
- Supported language/runtime versions: [for example Python 3.13 / Node 24 / JDK 21]
- Comment and documentation language: [Ukrainian by default; record an approved project override]
- Persistence: [actual storage]
- External providers: [actual integrations]
- Deployment target: [if applicable]
- Supported local environment: [Windows/PowerShell, WSL, etc.]

## Repository map

- Entry points: `[paths]`
- Application/domain code: `[paths]`
- UI: `[paths]`
- Tests: `[paths]`
- Configuration: `[paths]`
- Documentation/state: `[paths]`

## Real commands

```text
Install: [command]
Develop: [command]
Format/check format: [command]
Lint/static analysis: [command]
Typecheck/compile: [command]
Targeted test: [command]
Full relevant tests: [command]
Build/package: [command]
```

Do not guess missing commands. Inspect project configuration and record verified commands.

## Architecture and conventions

- Identifiers and machine-readable contracts: `English` unless explicitly overridden.
- Explanatory comments/docstrings/Javadoc/TSDoc: `Ukrainian` by default; explain reasons and invariants, not syntax.
- Formatter: [existing project tool or approved new-project default]
- Linter/static analysis: [existing project tools]
- Typecheck/compile: [existing project command]
- Test framework: [existing project framework]
- [Important boundaries and data flow.]
- [Patterns to reuse.]
- [Files or contracts that require special care.]
- [Current source of truth for requirements and decisions.]

## Delivery stages

- Documentation contract: `[required docs and approval state]`
- Current vertical slice: `[one coherent user-visible outcome]`
- Acceptance criteria: `[observable checks]`
- Commit map: `[ordered coherent outcomes, expected paths, and focused verification]`
- Local-commit authorization: `[not granted / granted for this bounded task]`
- Push authorization: `[not granted / explicitly granted]`

When local commits are authorized, every completed verified GREEN stage ends in one selective atomic commit before the next independent stage. Keep code, focused tests, migrations, and directly corresponding documentation together when they form one behavior; separate independently useful or reversible outcomes. Never use file count as the boundary, commit a knowingly broken RED state, or rewrite accepted checkpoint history without explicit approval.

For a new or materially uncertain project, complete the proportionate documentation contract before broad implementation. For small maintenance work, keep this section compact.

## Safety and permissions

- Secrets/runtime files excluded from Git: `[patterns]`
- Sensitive actions: `[actions]`
- Project-specific approval gates: `[gates]`
- Never modify casually: `[paths/systems]`
- Production credentials available to agents: `no` unless explicitly documented and approved
- Allowed network destinations: `[deny by default; list exceptions]`
- Database roles available during agent work: `[none / local / staging read-only]`
- Required security documents: `[SECURITY / THREAT-MODEL / DATA-INVENTORY / ACCESS-MATRIX]`

## Review gates

- Self-review required after implementation: `yes`
- Independent review required for: `[commercial / auth / data / database / payment / deployment / broad change]`
- Blocking severities: `critical, high`
- Required automated checks: `[tests / lint / typecheck / build / secret scan / dependency scan / SAST]`
- Merge/deploy approval owner: `[person or role]`

## Definition of done

- The requested user behavior works through the real path.
- Relevant checks pass, or failures are reported exactly.
- User usefulness is evaluated separately from technical completion.
- No unrelated files, secrets, or runtime data changed.
- Existing context documents match the verified state.
- Independent stages are not mixed into one unreviewable change.
- Security and code-review gates required by risk have passed or blockers are reported.
- Final handoff follows the global four-part format.
