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

## Safety and permissions

- Secrets/runtime files excluded from Git: `[patterns]`
- Sensitive actions: `[actions]`
- Project-specific approval gates: `[gates]`
- Never modify casually: `[paths/systems]`

## Definition of done

- The requested user behavior works through the real path.
- Relevant checks pass, or failures are reported exactly.
- User usefulness is evaluated separately from technical completion.
- No unrelated files, secrets, or runtime data changed.
- Existing context documents match the verified state.
- Final handoff follows the global four-part format.
