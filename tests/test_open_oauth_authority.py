from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_open_oauth_route_is_post_only_and_exact():
    route = yaml.safe_load((ROOT / "clusters/re8ch/open-oauth-route.yaml").read_text())
    assert route["spec"]["hostnames"] == ["open.service.re8ch.com"]
    expected = {
        "/oauth-applications/v1/register": "/rpc/create_oauth_application",
        "/oauth-applications/v1/list": "/rpc/my_oauth_applications",
        "/oauth-applications/v1/lifecycle": "/rpc/set_oauth_application_lifecycle",
        "/oauth-applications/v1/rotate-secret": "/rpc/rotate_oauth_application_secret",
    }
    observed = {}
    for rule in route["spec"]["rules"]:
        match = rule["matches"][0]
        assert match == {"method": "POST", "path": {"type": "Exact", "value": match["path"]["value"]}}
        assert rule["backendRefs"] == [{"name": "supabase-identity-rest", "port": 3000}]
        observed[match["path"]["value"]] = rule["filters"][0]["urlRewrite"]["path"]["replaceFullPath"]
    assert observed == expected


def test_oauth_migration_authority_is_single_versioned_source():
    config, job = list(yaml.safe_load_all(
        (ROOT / "clusters/re8ch/oauth-application-runtime.yaml").read_text()
    ))
    assert config["metadata"]["name"] == "supabase-oauth-application-runtime-v1"
    assert job["metadata"]["name"] == config["metadata"]["name"]
    assert job["spec"]["template"]["spec"]["volumes"][0]["configMap"]["name"] == config["metadata"]["name"]
    assert "@sha256:" in job["spec"]["template"]["spec"]["containers"][0]["image"]
    migration = config["data"]["migration.sql"]
    for function in ("create_oauth_application", "my_oauth_applications",
                     "set_oauth_application_lifecycle", "rotate_oauth_application_secret"):
        assert f"api.{function}" in migration
    assert "grant execute" in migration and "to authenticated" in migration
    assert "alter function core.active_oauth_org(uuid) owner to supabase_admin" in migration
    assert "grant execute on function core.active_oauth_org(uuid) to supabase_auth_admin" in migration
    assert "alter function api.create_oauth_application(text,jsonb,text,text,text) owner to supabase_auth_admin" in migration


def test_litellm_uses_open_oauth_instead_of_a_static_client_seed():
    kustomization = (ROOT / "clusters/re8ch/kustomization.yaml").read_text()
    assert "litellm-userhub-oauth.yaml" not in kustomization
    assert not (ROOT / "clusters/re8ch/litellm-userhub-oauth.yaml").exists()


def test_static_release_contains_route_and_configmap_without_duplicate_job():
    resources = list(yaml.safe_load_all(
        (ROOT / "releases/identity-access-domain-supabase-identity/resources.yaml").read_text()
    ))
    identities = {(item["kind"], item["metadata"]["name"]) for item in resources}
    assert ("HTTPRoute", "supabase-identity-open-oauth") in identities
    assert ("ConfigMap", "supabase-oauth-application-runtime-v1") in identities
    assert ("Job", "supabase-oauth-application-runtime-v1") not in identities
    cohort = yaml.safe_load((ROOT / "operations/releases/domain-cohort.json").read_text())
    assert {item["identity"] for item in cohort["deferred"]} >= {
        "batch/Job/supabase-identity/supabase-oauth-application-runtime-v1"
    }


def test_identity_release_can_create_reviewed_runtime_objects():
    contract = yaml.safe_load((ROOT / "contracts/identity-access-domain-supabase-identity.yaml").read_text())
    authorization = contract["spec"]["authorization"]
    assert authorization["requireExisting"] is False
    assert "supabase-oauth-application-runtime-v1" in authorization["objectNames"]


def test_identity_executor_can_create_only_named_reviewed_objects():
    documents = list(yaml.safe_load_all((ROOT / "operations/releases/domain-access.yaml").read_text()))
    role = next(item for item in documents if item["kind"] == "Role"
                and item["metadata"]["name"] == "identity-access-domain-supabase-identity")
    named_configmaps = next(rule for rule in role["rules"] if rule["apiGroups"] == [""]
                            and rule["resources"] == ["configmaps"] and "resourceNames" in rule)
    create_configmaps = next(rule for rule in role["rules"] if rule["apiGroups"] == [""]
                             and rule["resources"] == ["configmaps"] and rule["verbs"] == ["create"])
    assert "supabase-oauth-application-runtime-v1" in named_configmaps["resourceNames"]
    assert "resourceNames" not in create_configmaps


def test_open_oauth_has_an_exact_non_pruning_release_contract():
    contract = yaml.safe_load((ROOT / "contracts/identity-access-openoauth-runtime.yaml").read_text())
    assert contract["spec"]["authorization"] == {
        "fieldManager": "re8ch-release/identity-access-openoauth-runtime",
        "resources": ["core/ConfigMap"],
        "objectNames": ["supabase-oauth-application-runtime-v1"],
        "allowClusterScoped": False,
        "requireExisting": True,
    }
    assert contract["spec"]["lifecycle"]["prune"] is False
