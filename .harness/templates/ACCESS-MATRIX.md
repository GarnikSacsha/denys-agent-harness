# Access matrix

| Actor/identity | Environment | Files/code | Database | Secrets | Network/tools | Deploy/migrate | Approval owner |
|---|---|---|---|---|---|---|---|
| Agent | Local | scoped write | local only | scoped local | allowlist | no | Denys/project owner |
| Agent | Staging | scoped write | none/read-only if approved | scoped staging only | allowlist | approval required | project owner |
| Agent | Production | none by default | none | none | none | no | production owner |

Document application, CI, migration, backup, administrator, support, and external-provider identities below. Grant only required actions and keep credentials separately revocable.
