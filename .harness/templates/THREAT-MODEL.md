# Threat model

## System and trust boundaries

[Actors, components, data stores, external providers, entry points, and privileged operations.]

## Threats

| Asset/boundary | Threat or misuse case | Impact | Existing control | Verification | Residual risk/owner |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## Required abuse cases

- Cross-tenant/object access
- Prompt injection through user, repository, web, media, or provider content
- Secret disclosure through output, logs, Git, errors, or tools
- SSRF/unsafe upload/oversized content
- Privilege escalation or tool argument manipulation
- Destructive or duplicated write through retry/concurrency
- Production access from development or agent environment
- Dependency/supply-chain compromise
- Data retention or deletion failure

## Review trigger

Update when a trust boundary, provider, data class, authentication model, privileged tool, deployment topology, or production workflow changes.
