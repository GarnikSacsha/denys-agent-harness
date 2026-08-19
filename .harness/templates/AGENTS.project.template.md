# Project operating instructions

## Project outcome

[One or two sentences describing the real user result.]

## Current stage and scope

- Stage: [prototype / MVP / pilot / production]
- In scope: [current product boundary]
- Out of scope: [explicit exclusions]

## Stack and runtime

- Language/framework: [actual stack]
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
Targeted test: [command]
Full test: [command]
Lint/typecheck: [command]
Build: [command]
```

Do not guess missing commands. Inspect project configuration and record verified commands.

## Architecture and conventions

- [Important boundaries and data flow.]
- [Patterns to reuse.]
- [Files or contracts that require special care.]
- [Current source of truth for requirements and decisions.]

## Delivery stages

- Documentation contract: `[required docs and approval state]`
- Current vertical slice: `[one coherent user-visible outcome]`
- Acceptance criteria: `[observable checks]`
- Intended commit boundary: `[files/outcome that belong together]`

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
