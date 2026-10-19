# Agent integration: static preflight and runtime handshake

## Scope

The Harness entry points are `AGENTS.md` (Codex), `GEMINI.md`, `CLAUDE.md`, and `AI.md` (generic). `.harness/START-HERE.md` routes additional context. These are instructions, **not a sandbox or an enforceable authorization boundary**.

## Before starting a project

1. Work in the intended project repository, not a similarly named directory.
2. Bootstrap a new project using `scripts/bootstrap-project.ps1 -ProjectPath <project>` on Windows. The script preserves existing instruction files and directories unless `-Force` was explicitly requested. Check diffs before using `-Force`.
3. Run the static preflight from the Harness root:

   ```powershell
   py -m scripts.check_agent_entry --project "C:\path\to\project" --agent all
   ```

   Use `--agent codex`, `gemini`, `claude`, or `generic` to check only one adapter, and `--json` for a machine-readable report.
4. The result `static_ready` verifies the required files, adapter references, context router, and skill presence. It **does not prove** a running agent loaded or obeyed those rules. `runtime_loading_verified` is deliberately always `false`.

## Runtime handshake in the actual agent session

Start a **read-only** session in the real project root. Before making edits, ask the agent to:

- report its actual repository root, working directory, and Git branch;
- name exactly which instruction files it read, with their resolved paths;
- identify the applicable mandatory contract and task-specific context router file;
- identify one permission boundary from the loaded contract and a skill available in the project;
- disclose any read failure, unsupported import, stale path, or ambiguity rather than claiming the Harness loaded.

For Gemini CLI, inspect `/memory show` when supported and compare the loaded context with the reported files. For Codex and Claude Code, use their available context inspection or file-read evidence, where supported. Never assume the agent follows `@./AGENTS.md` just because it appears in an adapter file.

**Acceptance:** static preflight passes, and the live agent gives verifiable evidence of loading the correct files. If a live agent cannot access the files, runtime integration is `NOT VERIFIED` / `BLOCKED`, regardless of a green CI result.

## CI coverage and limits

`.github/workflows/harness-ci.yml` runs the existing Harness structural validator, Python integration tests, and the static preflight on Ubuntu and Windows; Windows also bootstraps an isolated disposable project and verifies a repeat bootstrap does not overwrite an existing adapter customization.

CI does **not** run Codex, Gemini, or Claude. It does not exercise their actual model runtimes, establish permissions, or prove their adherence to the policy. Those require a live handshake and, later, behavioral evaluation tests.
