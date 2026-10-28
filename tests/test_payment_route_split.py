from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]


def test_static_billing_uses_database_domains_and_external_payment_uses_api_domain():
    docs = [
        item
        for item in yaml.safe_load_all(
            (ROOT / "clusters/re8ch/payments-authority-resources.yaml").read_text()
        )
        if item and item.get("kind") == "HTTPRoute"
    ]
    routes = {item["metadata"]["name"]: item for item in docs}

    for access, hostname in (("ro", "db-ro.re8ch.com"), ("rw", "db-rw.re8ch.com")):
        route = routes[f"re8ch-payment-registry-db-{access}"]
        assert route["spec"]["hostnames"] == [hostname]
        assert route["spec"]["rules"] == [{
            "backendRefs": [{"name": "nuclio-payment-registry-api", "port": 8080}],
            "matches": [{"path": {"type": "PathPrefix", "value": "/payment/v1"}}],
        }]

    external = routes["re8ch-payment-registry-auth-center"]
    assert external["spec"]["hostnames"] == ["api.re8ch.com"]
    assert external["spec"]["rules"][0]["matches"] == [
        {"path": {"type": "PathPrefix", "value": "/payment"}}
    ]
