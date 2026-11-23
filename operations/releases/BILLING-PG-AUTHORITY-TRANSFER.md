# Billing and PG authority transfer

Billing/Auth/PG belong to identity-access. These two releases import the exact
rendered objects from previously accepted service-backend releases:

| Target | Previous accepted build | Objects |
| --- | --- | --- |
| identity-access-domain-payments | run 39891607412 / 4830d8216742524ebeb3be8bbeb6c4cb8c8b9b28 | 28, including six Deployments |
| identity-access-domain-supabase-pg-re8ch | run 40553229634 / 6f3f7e49bbed2896be7f7b7a98f9e23f8c96d26e | one Deployment, supabase-rest |

The current main Billing projection has 32 objects and route changes. They are
not part of this transfer. The transferred source retains the reviewed 28-object
inventory; tests compare every object against that bounded source. Immutable
product image pins may advance through a dedicated Identity PR when the product
publisher has already applied the same digest and owns that field. This shares
the matching SSA value without using force or taking publisher ownership. The
historical studio database bootstrap Job is not imported or replayed. Namespace,
credentials, PVCs and old SSA field managers are preserved; force and prune are
disabled.

The Bifurcate tool-publication and organization-cluster-binding migrations are
different: they are new, idempotent schema migrations against `re8ch_billing`,
not a replay of the historical studio bootstrap. This repository is the
existing authority for `supabase-pg-re8ch`, so its native Flux root creates the
two one-shot Jobs and their exact supporting objects. The static release
compiler intentionally classifies Jobs as `one-shot-job-platform-owned`; it
therefore adopts the ConfigMaps, ServiceAccount, and CiliumNetworkPolicy into
the protected `identity-access-domain-supabase-pg-re8ch` contract while leaving
Job execution to the existing native controller. Do not copy these migrations
into commerce-billing or another static domain to work around that boundary.

`authority-transfers.json` binds previous digest, repository and source commit.
The new repository signs a new authority envelope without rebuilding product
images or charts. Old accepted states remain untouched audit evidence; target
states start empty and must pass real execution and health validation.

Before execution, the platform must verify the previous accepted digests,
compare desired/live resource contents (especially Billing routes), capture and
recheck every resource UID, and confirm workload health. Stop old main publish
and replay dispatches; reduce all old matching Roles to exact get-only audit
access, verify effective old-group write denial, then grant target exact access.
Do not infer single-writer safety from workflow filtering alone.

After the protected no-force execution, independently verify accepted health,
unchanged workload UIDs and old-group write denial. If the first attempt fails,
keep its result and old audit state. Revoke target write permissions before
restoring old reviewed permissions. Never enable both writers or trust the old
repository's artifact as though it carried an identity repository signature.
