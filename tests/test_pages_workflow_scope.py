from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEPLOY_PAGES_SHA = "d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e"
STATIC_CONTEXT_PATHS = (
    "site/**",
    "README.md",
    "AGENTS.md",
    "docs/CROSS-ORG-CONTEXT.md",
    ".github/ISSUE_TEMPLATE/**",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/PROJECT_CONTEXT_TEMPLATE.md",
    ".github/workflows/pages.yml",
)


def test_pages_uses_verified_deploy_action_and_static_scope():
    workflow = (ROOT / ".github/workflows/pages.yml").read_text()

    assert f"actions/deploy-pages@{DEPLOY_PAGES_SHA}" in workflow
    assert 'paths: ["site/**", ".github/workflows/pages.yml"]' in workflow


def test_main_validation_ignores_only_static_context_paths():
    workflow = (ROOT / ".github/workflows/validate.yml").read_text()

    assert "pull_request:" in workflow
    assert "paths-ignore:" in workflow
    for path in STATIC_CONTEXT_PATHS:
        assert f"- {path}" in workflow

    for runtime_path in ("clusters/**", "contracts/**", "releases/**", "policies/**"):
        assert runtime_path not in STATIC_CONTEXT_PATHS


def test_runtime_reconcile_has_no_push_trigger():
    workflow = (ROOT / ".github/workflows/identity-access-reconcile.yml").read_text()
    event_block = workflow.split("permissions:", 1)[0]

    assert "schedule:" in event_block
    assert "workflow_dispatch:" in event_block
    assert "push:" not in event_block
