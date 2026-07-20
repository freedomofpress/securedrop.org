#!/usr/bin/env python3
"""Check that .pre-commit-config.yaml's additional_dependencies pins match package.json.

additional_dependencies in .pre-commit-config.yaml duplicate version pins that
also live in package.json, with no automatic mechanism (e.g. Dependabot) keeping
them in sync. This script fails if they drift apart, so a bump to one is caught
if the other wasn't updated to match.
"""

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent


def load_package_versions() -> dict[str, str]:
    package_json = json.loads((ROOT / "package.json").read_text())
    deps = {
        **package_json.get("dependencies", {}),
        **package_json.get("devDependencies", {}),
    }
    return {name: re.sub(r"^[\^~]", "", version) for name, version in deps.items()}


def load_precommit_pins() -> dict[str, str]:
    config = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text())
    pins = {}
    for repo in config["repos"]:
        for hook in repo.get("hooks", []):
            for dep in hook.get("additional_dependencies", []):
                # rpartition, not split, so scoped packages like
                # "@eslint/js@10.0.1" resolve to ("@eslint/js", "10.0.1")
                name, sep, version = dep.rpartition("@")
                if not sep:
                    continue  # no version pin on this entry; nothing to check
                pins[name] = version
    return pins


def main() -> int:
    package_versions = load_package_versions()
    precommit_pins = load_precommit_pins()

    mismatches = [
        (name, pinned_version, package_versions[name])
        for name, pinned_version in precommit_pins.items()
        if name in package_versions and package_versions[name] != pinned_version
    ]

    if mismatches:
        print("Version mismatches between .pre-commit-config.yaml and package.json:")
        for name, pinned, expected in mismatches:
            print(f"  {name}: pre-commit has {pinned}, package.json has {expected}")
        print("\nUpdate .pre-commit-config.yaml's additional_dependencies to match.")
        return 1

    print("pre-commit additional_dependencies match package.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
