from __future__ import annotations

import importlib

import rrs


def test_runtime_package_imports() -> None:
    assert rrs.__version__ == "0.1.0"


def test_top_level_packages_import() -> None:
    packages = (
        "rrs.domain",
        "rrs.ports",
        "rrs.application",
        "rrs.infrastructure",
        "rrs.integrations",
        "rrs.cli",
        "rrs.bootstrap",
    )

    for package in packages:
        importlib.import_module(package)
