from pathlib import Path
import yaml
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'operations/releases'))
import compile_domain


def test_mail_no_longer_has_dispatchable_identity_contract():
    assert not (ROOT / 'contracts/identity-access-domain-mail-system.yaml').exists()
    assert compile_domain.classify({'apiVersion': 'apps/v1', 'kind': 'Deployment', 'metadata': {'name': 'stalwart-webmail', 'namespace': 'mail-system'}}, set()) == 'transferred-to-agent-runtime'
    access = list(yaml.safe_load_all((ROOT / 'operations/releases/domain-access.yaml').read_text()))
    mail = [obj for obj in access if obj['metadata']['namespace'] == 'mail-system']
    assert len(mail) == 1
    assert mail[0]['kind'] == 'Role'
    assert all(rule['verbs'] == ['get'] for rule in mail[0]['rules'])
    assert any('ssa-state-identity-access-domain-mail-system' in rule['resourceNames'] for rule in mail[0]['rules'])
