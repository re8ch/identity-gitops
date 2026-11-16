# RE8CH Identity GitOps

Desired-state authority for RE8CH identity guardrails and reviewed identity-access releases. Product-owned User Hub and application authentication releases remain in their product repositories.

## Collaboration

```text
Project → parent Issue → Issue → branch/worktree → signed commits → PR
        → checks → runtime evidence → Project status
```

Use [the Project context template](.github/PROJECT_CONTEXT_TEMPLATE.md). Standard views are `List`, `Status`, and `Timeline`.

## Repository map

- `clusters/re8ch/`: production desired state
- `contracts/`: immutable release contracts
- `operations/releases/`: compilation, publication, reconciliation, and observation
- `policies/`: repository authority rules
- `releases/`: accepted release state
- `schemas/`: release contracts
- `tests/`: authority and delivery verification
- `docs/`: durable contracts and narrative indexes

Runtime observations, Kubernetes output, incident timelines, and migration stories belong in Issues, Discussions, the Wiki, or observability systems. Start at [Runtime context](docs/RUNTIME-CONTEXT.md).

The bounded cloud SSA executor is the delivery writer. Signed commits, pull requests, and passing checks carry reviewed intent.
