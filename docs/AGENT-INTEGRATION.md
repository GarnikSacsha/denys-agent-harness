# Agent integration: static preflight and runtime handshake

## Scope

The Harness entry points are `AGENTS.md` (Codex), `GEMINI.md`, `CLAUDE.md`, and `AI.md` (generic). `.harness/START-HERE.md` routes additional context. These are instructions, **not a sandbox or an enforceable authorization boundary**.

## Before starting a project

1. Work in the intended project repository, not a similarly named directory.
2. Bootstrap a new project using `scripts/bootstrap-project.ps1 -ProjectPath <project>` on Windows. The script preserves existing instruction files and directories unless `-Force` was explicitly requested. Check diffs before using `-Force`. Source and destination must be separate, existing filesystem directories: identical or ancestor/descendant paths are rejected before writes. Symlinks and junctions in the source/destination ancestry or managed trees are rejected, including with `-Force`. Missing required sources are also rejected before writes. This is not a transactional copy: an I/O failure during copying can still leave a partial destination; inspect it before retrying.
3. Run the static preflight from the Harness root:

   ```powershell
   py -m scripts.check_agent_entry --project "C:\path\to\project" --agent all
   ```

   Use `--agent codex`, `gemini`, `claude`, or `generic` to check only one adapter, and `--json` for a machine-readable report.
4. The result `static_ready` verifies readable, nonempty entry files, exact adapter references outside fenced examples/HTML comments, local Markdown file references in the context router, and every discovered skill. References are resolved relative to the router and must stay inside the project. Skills must be readable UTF-8 files with closed frontmatter containing unique `name` and `description` fields. The supported lightweight frontmatter format uses unquoted, nonempty single-line values; `name` is a lowercase hyphen-separated identifier. Quoted/block values, YAML collections and additional metadata fields are not supported by this validator. It **does not prove** instruction semantics, the intended Git root, or that a running agent loaded or obeyed those rules. `runtime_loading_verified` is deliberately always `false`.

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

`.github/workflows/harness-ci.yml` runs the existing Harness structural validator, Python integration tests, and the static preflight on Ubuntu and Windows. Actions are pinned to full commit IDs. Windows regression tests invoke installed Windows PowerShell and PowerShell 7 interpreters, checking Unicode content, paths with spaces/brackets, preservation of all generated Markdown files on repeat bootstrap, refusal before writes for overlapping paths or missing sources, and junction rejection. The smoke test additionally checks the bootstrapped project's preflight and only cleans a directory it successfully created. The cleanup collision regression uses an isolated injected creation failure.

Run `py -m unittest discover -s tests -p "test_*.py" -v` for the regressions. Windows bootstrap tests are explicitly skipped on other operating systems; the separate smoke test requires `python` on PATH. No test should bootstrap into an existing user project.

CI does **not** run Codex, Gemini, or Claude. It does not exercise their actual model runtimes, establish permissions, or prove their adherence to the policy. Those require a live handshake and, later, behavioral evaluation tests.
