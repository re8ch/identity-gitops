import hashlib
import json
from pathlib import Path
import yaml
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('namespace,count', [('payments', 28), ('supabase-pg-re8ch', 1)])
def test_transfer_uses_accepted_payload_without_new_routes_or_jobs(namespace, count):
    transfer = json.loads((ROOT / 'operations/releases/authority-transfers.json').read_text())[namespace]
    original = (ROOT / transfer['sourcePath']).read_bytes()
    assert 'sha256:' + hashlib.sha256(original).hexdigest() == transfer['sourceDigest']
    source = list(yaml.safe_load_all(original))
    target = list(yaml.safe_load_all((ROOT / f'releases/identity-access-domain-{namespace}/resources.yaml').read_text()))
    identity = lambda obj: (obj['apiVersion'], obj['kind'], obj['metadata']['namespace'], obj['metadata']['name'])
    source_objects = {identity(obj): obj for obj in source}
    target_objects = {identity(obj): obj for obj in target}
    assert source_objects.keys() == target_objects.keys()
    read_routes = {'commerce-db-ro': ('/commerce/v1', 'commerce-api'),
                   'payment-postgrest-ro': ('/payment/v1', 'nuclio-payment-registry-api')}
    for key, original in source_objects.items():
        current = target_objects[key]
        assert current == original
        if namespace == 'payments' and key[1] == 'HTTPRoute' and key[3] in read_routes:
            prefix, service = read_routes[key[3]]
            assert current['spec']['rules'][0]['backendRefs'] == [{'name': service, 'port': 8080}]
            assert {match['method'] for match in current['spec']['rules'][0]['matches']} == {'GET', 'HEAD', 'OPTIONS'}
            assert all(match['path'] == {'type': 'PathPrefix', 'value': prefix}
                       for match in current['spec']['rules'][0]['matches'])
        elif namespace == 'payments' and key[1] == 'HTTPRoute' and key[3] == 'payment-postgrest-rw':
            assert current['spec']['rules'][0]['backendRefs'] == [{'name': 'nuclio-payment-registry-api', 'port': 8080}]
            matches = current['spec']['rules'][0]['matches']
            assert {(match['method'], match['path']['value']) for match in matches} == {
                (method, '/payment/v1/credits/' + suffix)
                for method in ('POST', 'OPTIONS')
                for suffix in ('wallets', 'services', 'service-prices')
            }
            assert all(match['path']['type'] == 'Exact' for match in matches)
    assert len(target) == count
    assert not {'Secret', 'Role', 'RoleBinding', 'Job'} & {obj['kind'] for obj in target}
    contract = yaml.safe_load((ROOT / f'contracts/identity-access-domain-{namespace}.yaml').read_text())['spec']
    assert contract['authorization']['fieldManager'] == transfer['fieldManager']
    assert contract['authorization']['forceConflictObjects'] == []
    assert contract['authorization']['requireExisting'] is True
    assert contract['lifecycle']['prune'] is False
