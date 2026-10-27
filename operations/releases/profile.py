#!/usr/bin/env python3
"""Validate the bounded identity-access release profile."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = ROOT / "contracts"
REPOSITORY = "re8ch/identity-gitops"
WORKFLOW = ".github/workflows/static-release.yml"
ENVIRONMENT = "release-executor-identity-access"
AUDIENCE = "https://kube-api.re8ch.com/release-executor-identity-access"
GROUP = "re8ch:release-executor:identity-access"
SIGNER = f"https://github.com/{REPOSITORY}/{WORKFLOW}@refs/heads/main"


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def validate_contract(path: Path) -> dict[str, str]:
    resolved = path.resolve()
    if CONTRACT_ROOT.resolve() not in resolved.parents or resolved.suffix not in {".yaml", ".yml"}:
        raise ValueError("contract must be a YAML file under contracts")
    contract = yaml.safe_load(resolved.read_text())
    spec = contract["spec"]
    if spec.get("authorityDomain") != "identity-access":
        raise ValueError("contract authorityDomain must be identity-access")
    if not contract["metadata"]["name"].startswith("identity-access-"):
        raise ValueError("contract name is outside identity-access")
    expected = {
        "repository": REPOSITORY,
        "workflow": WORKFLOW,
        "ref": "refs/heads/main",
        "environment": ENVIRONMENT,
        "audience": AUDIENCE,
        "signer": SIGNER,
    }
    for field, value in expected.items():
        if spec["provenance"].get(field) != value:
            raise ValueError(f"contract provenance {field} must be {value}")
    source = spec["source"]
    source_path = source.get("path", "")
    if source.get("repository") != REPOSITORY or not source_path.startswith("releases/"):
        raise ValueError("contract source must resolve inside this repository")
    if source.get("renderer") != "kustomize" or source.get("revision") != "github-main-reviewed":
        raise ValueError("identity canary must use the reviewed static Kustomize source")
    return {
        "release-id": contract["metadata"]["name"],
        "namespace": spec["target"]["namespace"],
        "domain": "identity-access",
        "environment": ENVIRONMENT,
        "audience": AUDIENCE,
        "kubernetes-group": GROUP,
        "signer": SIGNER,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    result = validate_contract(args.contract)
    if args.github_output:
        with args.github_output.open("a") as output:
            for key, value in result.items():
                output.write(f"{key}={value}\n")
    else:
        print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
