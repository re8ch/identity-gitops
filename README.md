# RE8CH Identity GitOps

Private desired-state authority for RE8CH identity platform guardrails. User Hub and application auth runtime releases remain product-owned.

## Cloud release artifact reuse

`static-release` defaults to `mode=publish` for a reviewed change. Use
`mode=reconcile` with `execute=true` to replay the target's healthy accepted OCI
digest without recompiling or publishing. Replays verify the original signer,
inventory and contract; blocked or suspended releases are rejected. Agent owner
migration requires an initial publication with the new canonical signer before
accepted-artifact replay can be used. State writes use optimistic concurrency.

Public pull request checks use GitHub-hosted workers. Private preparation can use
the restricted R640 fallback. Validation supersedes obsolete runs; deployment
runs remain serialized. No local Docker daemon is required by these workflows.
