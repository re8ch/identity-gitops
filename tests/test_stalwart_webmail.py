from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


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
