# Harness context router

Read `../AGENTS.md` first. It is the mandatory operating contract.

Then route by task:

| Task | Read next |
|---|---|
| Small focused code change | Project instructions; relevant code/tests; `WORKFLOWS.md` → Focused implementation |
| Bug diagnosis | `WORKFLOWS.md` → Diagnosis; relevant code/logs/tests |
| New product or feature planning | `PROFILE.md`; `PROJECT-PATTERNS.md`; project requirements |
| Architecture or new dependency | `PROFILE.md`; `POLICIES.md`; current architecture and evidence |
| Commercial project, sensitive data, auth, database, secrets, or production | `SECURITY.md`; project `SECURITY.md`, threat model, data inventory, and access matrix |
| Implementation or code review | `CODE-QUALITY.md`; `WORKFLOWS.md` → Code review gate; relevant diff/tests/contracts |
| LLM/tool-calling work | `POLICIES.md` → LLM, tools, evidence, money |
| UI/UX work | `PROFILE.md` → Product and visual preferences; current design system |
| Release/staging/production | `POLICIES.md` → Release and external actions; project deployment docs |
| New chat or agent handoff | `WORKFLOWS.md` → Checkpoint and handoff |
| New repository setup | `templates/AGENTS.project.template.md`; `templates/TASK.md`; security templates when the project is commercial or handles sensitive data |

## Context rules

- Do not load every file by default.
- Read the profile only when personal preferences affect a decision.
- Read project patterns only when planning or comparing a similar solution.
- Prefer current project facts over historical patterns.
- If uncertain whether a preference is global or project-specific, treat it as project-specific and ask only if the decision is material.
- Record durable project decisions in the project, not only in chat history.
