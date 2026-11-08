"""tests/unit/test_polyrepo_decoupling.py: polyrepo dependency decoupling.

Verifies the vyapaar-examples package does not depend on fragile relative filesystem paths
(``../vyapaar-*``) into sibling checkouts.

This is the contract that lets examples run against installed distributions:
``import vyapaar_examples`` resolves cleanly without relative ``../`` sibling paths.
"""

from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples"

_FRAGILE_SYS_PATH = re.compile(r"\.\./(vyapaar|honba)-[A-Za-z0-9_-]+")
_FRAGILE_SPEC = re.compile(r"spec_from_file_location\([^)]*\.\./(vyapaar|honba)-[A-Za-z0-9_-]+")


def _example_scripts() -> list[Path]:
    return sorted(p for p in EXAMPLES.glob("*/[0-9][0-9]_*.py") if p.is_file())


def test_vyapaar_examples_imports_cleanly() -> None:
    """vyapaar_examples package imports cleanly."""
    importlib.import_module("vyapaar_examples")


def test_vyapaar_packages_import_or_gap_0006() -> None:
    """Installed vyapaar packages import cleanly; skip wheel if absent (gap 0006)."""
    try:
        importlib.import_module("vyapaar")
    except ModuleNotFoundError:
        pytest.skip("vyapaar wheel absent (gap 0006); in-repo fallback active")


def test_pyproject_does_not_rely_on_fragile_sibling_path() -> None:
    """pyproject.toml must not reference fragile ../ sibling paths."""
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "../vyapaar-" not in pyproject, "pyproject.toml references a fragile ../vyapaar-* path"
    assert "../honba-" not in pyproject, "pyproject.toml references a fragile ../honba-* path"


def test_no_example_mutates_sys_path_with_sibling_checkout() -> None:
    """No numbered example script injects a sibling checkout into ``sys.path``."""
    violations: list[str] = []
    for script in _example_scripts():
        text = script.read_text(encoding="utf-8")
        for line in text.splitlines():
            if "sys.path" in line and _FRAGILE_SYS_PATH.search(line):
                violations.append(script.relative_to(ROOT).as_posix())
                break
        if _FRAGILE_SPEC.search(text):
            violations.append(script.relative_to(ROOT).as_posix())
    assert not violations, (
        "examples mutate sys.path or load modules from a sibling checkout: "
        + ", ".join(sorted(set(violations)))
    )


def test_example_modules_load_via_installed_packages_only() -> None:
    """Loading example modules resolves vyapaar_examples without relative checkout paths."""
    import importlib.util

    original_path = list(sys.path)
    try:
        for script in _example_scripts()[:5]:
            mod_name = f"_decoupling_probe_{script.stem}"
            spec = importlib.util.spec_from_file_location(mod_name, script)
            assert spec is not None and spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = module
            spec.loader.exec_module(module)
            for entry in sys.path:
                assert "../vyapaar-" not in entry, f"{script.name} added {entry!r} to sys.path"
                assert "../honba-" not in entry, f"{script.name} added {entry!r} to sys.path"
            del sys.modules[mod_name]
    finally:
        sys.path[:] = original_path
