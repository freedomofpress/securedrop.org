"""Fail if any locked package lacks a wheel for a supported Linux architecture.

poetry.lock records every file PyPI lists for each pinned version, so wheel
tags alone answer the question: no network, and any host can check any arch.
Run via `just wheel-check`, or `python -I ci/scripts/wheel-check.py`.
"""

import sys
import tomllib

from pip._vendor.packaging.markers import Marker
from pip._vendor.packaging.tags import compatible_tags, cpython_tags
from pip._vendor.packaging.utils import parse_wheel_filename


# Container arches: amd64 Linux and Intel Macs; arm64 Apple Silicon.
ARCHES = ("x86_64", "aarch64")
PYTHON = (3, 14)  # Keep in step with PYTHON_IMAGE in ci/containers/Containerfile.
GLIBC_MINOR = 41  # Debian trixie.


def supported_tags(arch):
    plats = [f"manylinux_2_{m}_{arch}" for m in range(GLIBC_MINOR, 4, -1)]
    plats += [f"manylinux{v}_{arch}" for v in ("2014", "2010", "1")]
    abi = "cp{}{}".format(*PYTHON)
    return {*cpython_tags(PYTHON, [abi], plats), *compatible_tags(PYTHON, abi, plats)}


def marker_env(arch):
    return {
        "implementation_name": "cpython",
        "os_name": "posix",
        "platform_machine": arch,
        "platform_python_implementation": "CPython",
        "platform_system": "Linux",
        "python_full_version": "{}.{}.0".format(*PYTHON),
        "python_version": "{}.{}".format(*PYTHON),
        "sys_platform": "linux",
    }


def installed_on(pkg, env):
    """Poetry writes markers as one string, or a per-group table of them."""
    markers = pkg.get("markers")
    if markers is None:
        return True
    if isinstance(markers, str):
        markers = {"": markers}
    return any(Marker(m).evaluate(env) for m in markers.values())


def has_wheel(pkg, tags):
    wheels = (f["file"] for f in pkg["files"] if f["file"].endswith(".whl"))
    return any(tags & parse_wheel_filename(w)[3] for w in wheels)


def main(path="poetry.lock"):
    with open(path, "rb") as f:
        packages = tomllib.load(f)["package"]
    missing = [
        (arch, f"{pkg['name']}=={pkg['version']}")
        for arch in ARCHES
        for tags, env in [(supported_tags(arch), marker_env(arch))]
        for pkg in packages
        if installed_on(pkg, env) and not has_wheel(pkg, tags)
    ]
    for arch, spec in missing:
        print(f"{arch}\t{spec}\tno compatible wheel")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
