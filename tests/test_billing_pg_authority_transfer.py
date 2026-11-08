import hashlib
import json
from pathlib import Path
import yaml
import pytest

ROOT = Path(__file__).resolve().parents[1]
HYPERSWITCH_RETIREMENTS = {
    ('apps/v1', 'Deployment', 'payments', 'hyperswitch-web'),
    ('v1', 'ConfigMap', 'payments', 'hyperswitch-superposition-schema'),
    ('v1', 'ConfigMap', 'payments', 'hyperswitch-superposition-seed'),
    ('v1', 'Service', 'payments', 'hyperswitch-web'),
    ('gateway.networking.k8s.io/v1', 'HTTPRoute', 'payments', 'hyperswitch-control-center-public'),
    ('gateway.networking.k8s.io/v1', 'HTTPRoute', 'payments', 'hyperswitch-router-public'),
    ('gateway.networking.k8s.io/v1', 'HTTPRoute', 'payments', 'hyperswitch-web-public'),
}


@pytest.mark.parametrize('namespace,count', [('payments', 21), ('supabase-pg-re8ch', 1)])
def test_transfer_uses_accepted_payload_without_new_routes_or_jobs(namespace, count):
    transfer = json.loads((ROOT / 'operations/releases/authority-transfers.json').read_text())[namespace]
    original = (ROOT / transfer['sourcePath']).read_bytes()
    assert 'sha256:' + hashlib.sha256(original).hexdigest() == transfer['sourceDigest']
    source = list(yaml.safe_load_all(original))
    target = list(yaml.safe_load_all((ROOT / f'releases/identity-access-domain-{namespace}/resources.yaml').read_text()))
    identity = lambda obj: (obj['apiVersion'], obj['kind'], obj['metadata']['namespace'], obj['metadata']['name'])
    source_objects = {identity(obj): obj for obj in source}
    target_objects = {identity(obj): obj for obj in target}
    expected = set(source_objects) - (HYPERSWITCH_RETIREMENTS if namespace == 'payments' else set())
    assert target_objects.keys() == expected
    read_routes = {'commerce-db-ro': ('/commerce/v1', 'commerce-api'),
                   'payment-postgrest-ro': ('/payment/v1', 'nuclio-payment-registry-api')}
    for key, original in source_objects.items():
        if key not in expected:
            continue
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
    if namespace == 'payments':
        assert contract['lifecycle']['prune'] is True
        assert set(contract['lifecycle']['deletionAllowlist']) == {
            ('core' if api == 'v1' else api.split('/')[0]) + f'/{kind}/{ns}/{name}'
            for api,kind,ns,name in HYPERSWITCH_RETIREMENTS
        }
        assert 'hyperswitch-superposition-local-key' in contract['authorization']['objectNames']
        assert all('PersistentVolumeClaim' not in item for item in contract['lifecycle']['deletionAllowlist'])
    else:
        assert contract['lifecycle']['prune'] is False
