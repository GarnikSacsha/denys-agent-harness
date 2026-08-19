---
name: verify-change
description: Verify a focused code or product change through the real execution path. Use after implementation, before handoff, when tests are green but user behavior is uncertain, or when reviewing whether a stage is truly complete.
---

# Verify a change

1. Re-read the requested user behavior and changed execution path.
2. Run the smallest targeted check, then adjacent checks proportionate to risk.
3. Inspect the final diff for unrelated files, secrets, runtime data, and accidental behavior.
4. Verify a controlled real or staging scenario only when authorized.
5. Report technical completion and user usefulness separately.
6. Never claim an unrun check passed.
