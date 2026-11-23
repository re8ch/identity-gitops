from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def migration_sql():
    objects = yaml.safe_load_all(
        (ROOT / "clusters/re8ch/billing-runtime-authority-migrations.yaml").read_text()
    )
    config = next(
        item
        for item in objects
        if item.get("kind") == "ConfigMap"
        and item["metadata"]["name"]
        == "supabase-billing-tool-publication-authority-v1"
    )
    return config["data"]["migration.sql"]


def test_ready_installations_derive_active_org_and_require_every_ready_state():
    sql = migration_sql()
    function = sql.split(
        "create or replace function bifurcate_api.list_ready_tool_installations()",
        1,
    )[1].split("create table if not exists bifurcate.usage_events", 1)[0]

    assert "security definer" in function
    assert "select org_ref into v_active_org_ref from billing.current_identity_org_context()" in function
    assert "p_active_org_ref" not in function
    assert "i.installed_org_ref=v_active_org_ref" in function
    assert "p.lifecycle='published'" in function
    assert "r.lifecycle='published'" in function
    assert "a.state='active'" in function
    assert "i.state='installed'" in function
    assert "b.state='ready'" in function


def test_ready_installations_return_only_non_secret_metadata_and_bounded_grant():
    sql = migration_sql()
    signature = sql.split(
        "create or replace function bifurcate_api.list_ready_tool_installations()",
        1,
    )[1].split("language plpgsql", 1)[0]

    for forbidden in ("definition jsonb", "tool_ref", "provider_audience", "allowed_scopes", "credential"):
        assert forbidden not in signature.lower()
    assert "revision_definition_sha256 text" in signature
    assert (
        "grant execute on function bifurcate_api.list_ready_tool_installations() "
        "to billing_commerce_runtime"
    ) in sql.replace("\n", " ")
    assert "grant execute on function bifurcate_api.list_ready_tool_installations() to authenticated" not in sql.replace("\n", " ")
