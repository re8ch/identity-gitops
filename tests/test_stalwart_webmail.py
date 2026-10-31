from pathlib import Path
import json

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_stalwart_userhub_broker_trusts_auth_hub_resource_token():
    documents = [
        item
        for item in yaml.safe_load_all(
            (ROOT / "clusters/re8ch/stalwart-userhub-oauth.yaml").read_text()
        )
        if item
    ]
    plan = next(
        item
        for item in documents
        if item["kind"] == "ConfigMap"
        and item["metadata"]["namespace"] == "mail-system"
        and item["metadata"]["name"] == "stalwart-userhub-oauth-plan-v1"
    )
    directory = json.loads(plan["data"]["plan.ndjson"].splitlines()[0])
    broker = directory["value"]["re8ch-enterprise-sso"]
    assert broker["issuerUrl"] == "https://auth.re8ch.com"
    assert broker["acceptedAudiences"] == {"stalwart-webui": True}
    assert broker["unscopedTokens"] == "interoperable"
    assert "requireAudience" not in broker
    assert "requireScopes" not in broker

    job = next(
        item
        for item in documents
        if item["kind"] == "Job"
        and item["metadata"]["name"] == "stalwart-userhub-oauth-v7"
    )
    plan_volume = next(
        item for item in job["spec"]["template"]["spec"]["volumes"]
        if item["name"] == "plan"
    )
    assert plan_volume["configMap"]["name"] == plan["metadata"]["name"]
    cli_volume = next(
        item for item in job["spec"]["template"]["spec"]["volumes"]
        if item["name"] == "cli"
    )
    assert cli_volume["image"]["reference"] == (
        "ghcr.io/stalwartlabs/cli@"
        "sha256:5b70732cb69cdab3ff0894c501544cf0bfa180fa75bcd0eeba4eebe04c1064e1"
    )


def test_webmail_uses_resilient_dns_for_oauth_and_jmap():
    documents = [
        item
        for item in yaml.safe_load_all(
            (ROOT / "clusters/re8ch/resources.yaml").read_text()
        )
        if item
    ]
    deployment = next(
        item
        for item in documents
        if item["kind"] == "Deployment"
        and item["metadata"].get("namespace") == "mail-system"
        and item["metadata"]["name"] == "stalwart-webmail"
    )
    pod = deployment["spec"]["template"]["spec"]
    environment = {
        item["name"]: item.get("value")
        for item in pod["containers"][0]["env"]
    }

    assert pod["dnsPolicy"] == "None"
    assert pod["dnsConfig"] == {
        "nameservers": ["1.1.1.1", "1.0.0.1"],
        "options": [{"name": "ndots", "value": "1"}],
    }
    assert environment["OAUTH_ISSUER_URL"] == "https://db-rw.re8ch.com/auth/v1"
    assert environment["OAUTH_CLIENT_ID"] == "705c1168-43d8-4ec3-980a-0327a59c7fc6"
    assert environment["JMAP_SERVER_URL"] == "https://id.re8ch.com"
