from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "clusters/re8ch/litellm-userhub-oauth.yaml"


def test_litellm_client_is_confidential_and_secret_backed():
    config_map, job = list(yaml.safe_load_all(SOURCE.read_text()))
    sql = config_map["data"]["clients.sql"]

    assert "'confidential'" in sql
    assert "'client_secret_basic'" in sql
    assert "https://litellm.service.re8ch.com/sso/callback" in sql
    assert "42c43a54-39d4-523b-b76f-2045b9a7311a" in sql
    assert "client_secret_hash = excluded.client_secret_hash" in sql
    assert "litellm-gotrue-sso" in SOURCE.read_text()
    assert "client-secret" in SOURCE.read_text()
    assert job["spec"]["template"]["spec"]["automountServiceAccountToken"] is False
    assert "dex" not in SOURCE.read_text().lower()
