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
    assert {identity(obj): obj for obj in source} == {identity(obj): obj for obj in target}
    assert len(target) == count
    assert not {'Secret', 'Role', 'RoleBinding', 'Job'} & {obj['kind'] for obj in target}
    contract = yaml.safe_load((ROOT / f'contracts/identity-access-domain-{namespace}.yaml').read_text())['spec']
    assert contract['authorization']['fieldManager'] == transfer['fieldManager']
    assert contract['authorization']['forceConflictObjects'] == []
    assert contract['authorization']['requireExisting'] is True
    assert contract['lifecycle']['prune'] is False
