# Deployment and migration gate

## Target

- Environment:
- Version/SHA:
- Services/data stores affected:
- Deployment owner:
- Migration approval owner:

## Preconditions

- [ ] Required tests, lint/typecheck/build passed
- [ ] Code review passed; critical/high findings resolved
- [ ] Security review passed for changed boundaries
- [ ] Secrets/configuration verified without exposing values
- [ ] Backup/PITR and recovery path verified as appropriate
- [ ] Migration is backward-compatible or rollback is defined
- [ ] Staging acceptance used the real route with safe data
- [ ] Monitoring/logging and spending/resource limits are ready

## Execution boundaries

- Approved deploy action:
- Separately approved migration/data action:
- Explicitly prohibited actions:
- Abort conditions:

## Verification and rollback

- Health/smoke scenario:
- User-visible acceptance scenario:
- Metrics/logs to inspect:
- Rollback command/process and owner:
- Final deployed SHA/state:
