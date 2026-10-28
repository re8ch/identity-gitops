# Billing and PG authority transfer

Billing/Auth/PG belong to identity-access. These two releases import the exact
rendered objects from previously accepted service-backend releases:

| Target | Previous accepted build | Objects |
| --- | --- | --- |
| identity-access-domain-payments | run 39891607412 / 4830d8216742524ebeb3be8bbeb6c4cb8c8b9b28 | 30, including six Deployments and two reviewed database-domain payment routes |
| identity-access-domain-supabase-pg-re8ch | run 40553229634 / 6f3f7e49bbed2896be7f7b7a98f9e23f8c96d26e | one Deployment, supabase-rest |

The initial transfer imported 28 objects. The current reviewed authority payload
adds only the missing `db-ro.re8ch.com/payment/v1` and
`db-rw.re8ch.com/payment/v1` routes so static billing reads and writes retain
their database-domain boundary; external recharge remains on `api.re8ch.com`.
Tests compare every published object against the digest-bound authority source.
The historical studio database bootstrap Job is not imported or replayed.
Namespace, credentials, PVCs and old SSA field managers are preserved; force
and prune are disabled.

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
