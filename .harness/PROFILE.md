# Denys working profile

This file contains observed preferences and product defaults. It improves decisions but cannot override `AGENTS.md`, project instructions, or the current request. Confidence labels describe how consistently a pattern has appeared.

## What good looks like

**High confidence.** Denys values a complete, truthful user journey over file count or technical spectacle:

```text
real input → understandable processing → useful result → clear presentation
→ save/next action → verification by Denys or a real user
```

The default product strategy is a narrow but real MVP, followed by real runs, quality improvement, automation, and only then scale.

## Decision style

1. Denys describes the desired user result, often conversationally and through an example.
2. The agent proposes a concrete implementation path.
3. A reversible test is preferred when risk and cost are bounded.
4. Denys reviews the result as a user, including whether it feels generic, chaotic, visually weak, or contextually wrong.
5. Successful behavior is then protected with tests, documentation, a checkpoint, and—after separate approval—staging verification.

Agents should propose and execute inside approved boundaries, but must not silently make product decisions for Denys.

## Communication defaults

- Conversational Russian with Denys; product UI/content uses the language of that product.
- Outcome and feasibility first; internal technical detail second.
- Short progress updates during long work.
- One decisive question at a time only when necessary.
- Ready-to-use text, patch, command, prompt, or handoff rather than vague advice.
- Direct admission of uncertainty plus the exact test needed.
- No condescending explanation of obvious constraints.

## Product preferences

- One real vertical slice before platform breadth.
- User usefulness and technical success reported separately.
- Real/staging evidence over assumptions or demo-only claims.
- Simple replaceable infrastructure until load or operations justify complexity.
- Existing systems changed in place by default.
- Context preserved through current README/REQ/CONTEXT/STATE/DECISIONS or equivalent project documents.
- Internal readiness must not be presented as proof of market demand.

## UI preferences

**Strong default, not an absolute brand rule:**

- calm, professional, clean visual language;
- clear hierarchy and structured information;
- accurate, useful previews and states;
- responsive/mobile behavior treated as a real path;
- minimal decorative noise;
- beauty as part of usability, not a substitute for clarity.

Avoid generic AI dashboards, meaningless gradients or glassmorphism, mixed languages, placeholder actions, visually identical alternatives, and UI that promises nonexistent functionality. Light Apple/Linear-like restraint is a recurring preference, but project branding may justify another direction.

## Learning preferences

- Explain simply using the actual project code.
- Prefer practice over memorization and abstract theory.
- Ask questions one at a time.
- After practice, identify only the real knowledge gaps.
- Prioritize what is required for the nearest goal; defer the rest.

## Architecture taste

- Technology is selected for the task, not for appearance.
- LLM output is grounded, structured, and validated.
- Deterministic code owns facts and permissions.
- Providers remain replaceable when practical.
- Multi-agent orchestration is useful only for independent roles.
- Real-user pilot and real-provider tests matter more than production-style decoration.

## Local, not global

Do not generalize these across all projects:

- Ukrainian or bilingual UI requirements;
- light or dark theme;
- PostgreSQL versus SQLite/JSON;
- Telegram-first interaction;
- multi-agent architecture;
- any single framework or programming language.

The global default is proportionality to stage, existing system, and verified user need.
