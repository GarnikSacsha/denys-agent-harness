# Denys Agent Harness

Portable operating rules for AI coding agents working with Denys across different local repositories.

This repository is a lightweight harness: instructions, context routing, workflows, templates, and validation. It is not a separate agent runtime and does not require Temporal, Docker, an MCP server, or a database.

## What it does

- gives every agent the same working contract;
- separates mandatory rules from personal preferences and historical patterns;
- forces read-first orientation before edits;
- keeps product decisions with Denys;
- defines permission and safety boundaries;
- standardizes planning, verification, progress checkpoints, and handoffs;
- defines a proportionate documentation-first workflow and atomic stage boundaries for deliberate project construction;
- provides a commercial-project security constitution and independent code-review quality gate;
- works with Codex, Gemini CLI/Antigravity, Claude Code, and generic file-aware agents.

## Repository map

```text
AGENTS.md                         Canonical mandatory contract
GEMINI.md                         Gemini entry point
CLAUDE.md                         Claude entry point
AI.md                             Generic-agent entry point
.harness/START-HERE.md            Context router
.harness/PROFILE.md               Observed preferences and product taste
.harness/POLICIES.md              Detailed safety, money, LLM, and release rules
.harness/SECURITY.md              Enforceable commercial security baseline
.harness/CODE-QUALITY.md          AI-generated code quality and review standard
.harness/WORKFLOWS.md             Standard task workflows
.harness/PROJECT-PATTERNS.md      Reusable lessons from previous projects
.harness/templates/               Files copied into a project
.agents/skills/                   Reusable open-format agent skills
scripts/validate_harness.py       Structural validator
scripts/bootstrap-project.ps1     Windows project bootstrap helper
```

## Recommended use

### Option A — keep this repository beside your projects

Give an agent the absolute path to this repository and say:

```text
Before working, read <PATH>\AGENTS.md and follow its startup protocol.
The current repository's own AGENTS.md and current request have higher priority
where explicitly stated. Do not edit anything until orientation is complete.
```

This works with any agent that can read local files, but the instruction must be included when starting a new chat.

### Option B — copy the entry files into each project

Copy the project template to the repository root as `AGENTS.md`, fill its placeholders, and keep this Harness available at a stable local path. For Gemini and Claude, also copy the matching adapter if automatic loading is desired.

On Windows, run from the Harness directory:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap-project.ps1 -ProjectPath "C:\path\to\project"
```

The script never overwrites existing instruction files unless `-Force` is explicitly supplied.

### Option C — global agent configuration

- Codex: keep the canonical personal rules at `~/.codex/AGENTS.md`.
- Gemini: keep a `~/.gemini/GEMINI.md` adapter that references this Harness.
- Claude Code: keep a `~/.claude/CLAUDE.md` adapter that references this Harness.

Absolute local imports are tool-specific. Repository-level entry files remain the most portable option.

## First run in a project

Ask the agent:

```text
Read the applicable Harness and project instructions. Work in orientation mode only:
find the real repository root, inspect Git state, identify entry points and real commands,
compare documentation with code, and report the current architecture and risks.
Do not modify files. End with the smallest useful next vertical slice.
```

## Validate the Harness

```powershell
py -m scripts.validate_harness
```

or:

```bash
python -m scripts.validate_harness
```

## Source priority

When sources conflict, use this order:

1. Denys's current direct request.
2. The closest project-level instructions and latest accepted project decision.
3. The canonical `AGENTS.md` in this Harness.
4. Current code, tests, runtime behavior, and active project documents.
5. `.harness/PROFILE.md` and project patterns.
6. Historical notes and hypotheses.

The profile provides context, not permission.
