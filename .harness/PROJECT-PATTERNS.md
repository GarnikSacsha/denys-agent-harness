# Reusable project patterns

Use this file for planning and analogy, not as current project truth.

## Common AI pipeline

Repeated across classifier, assistant, analysis, and support projects:

```text
unstructured input
→ bounded model role
→ strict structured output
→ deterministic validation
→ clear user result
→ fallback or classified error
```

## Common product loop

```text
real user context
→ narrow primary path
→ real-person acceptance
→ observed problem
→ minimal improvement
→ repeated acceptance
```

## Common construction loop

For new products and major subsystems:

```text
documentation contract
→ reviewed decisions and boundaries
→ minimal foundation
→ one verified vertical slice
→ atomic stage checkpoint or authorized commit
→ next independent slice
```

The documentation contract is proportional. Complex products may need separate scope, flows, roles, data, API, security, UI, and decision documents. Small changes may need only a short task contract and acceptance criteria.

## Common architecture lessons

- Separate acquisition/evidence, policy, ranking, personalization, and presentation when those stages have different truth sources.
- Keep external providers behind services.
- Avoid huge all-in-one entry files as a project grows.
- Continue batch processing after isolated item failures when the product contract allows it; report partial failure honestly.
- Use confirmation before financial records, messages, or other sensitive writes.
- Keep UI language and business domain internally consistent.
- Use benchmarks before freezing prompts, schemas, ranking, or automating at scale.

## Common anti-patterns

- allowing the model to decide unspoken product direction;
- broad platform architecture before one real scenario;
- metadata-only processing presented as media understanding;
- beautiful cards hiding unavailable results;
- duplicated agents doing the same work;
- tests that never exercise the deployed route;
- returning to legacy code because it is easier to understand;
- confusing internal implementation readiness with market validation.
