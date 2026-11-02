"""Fail if any locked package lacks a wheel for a supported Linux architecture.

poetry.lock records every file PyPI lists for each pinned version, so wheel
tags alone answer the question: no network, and any host can check any arch.
No shebang, deliberately: run it via `just check-wheels`, so the interpreter and
glibc are the image's. A newer host glibc would accept wheels the image can't load.
"""

import os
import sys
import tomllib

from packaging.markers import Marker
from packaging.tags import compatible_tags, cpython_tags
from packaging.utils import parse_wheel_filename


# Image arches: x86_64 for servers and Intel Macs, aarch64 for Apple Silicon.
ARCHES = ("x86_64", "aarch64")
PYTHON = sys.version_info[:2]
# The newest manylinux_2_N this glibc can load; 2_5 (manylinux1) is the floor.
GLIBC_MINOR = int(os.confstr("CS_GNU_LIBC_VERSION").rpartition(".")[2])


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
    for wheel in wheels:
        *_, wheel_tags = parse_wheel_filename(wheel)
        if tags & wheel_tags:
            return True
    return False


def main(path="poetry.lock"):
    with open(path, "rb") as f:
        packages = tomllib.load(f)["package"]
    missing = False
    for arch in ARCHES:
        tags, env = supported_tags(arch), marker_env(arch)
        for pkg in packages:
            if installed_on(pkg, env) and not has_wheel(pkg, tags):
                print(f"{arch}\t{pkg['name']}=={pkg['version']}\tno compatible wheel")
                missing = True
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
