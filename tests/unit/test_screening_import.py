"""`import vyapaar_examples.screening` must work without the optional vyapaar-data extra."""

from __future__ import annotations

import importlib

import pytest


def test_screening_package_imports_without_honba_data() -> None:
    mod = importlib.import_module("vyapaar_examples.screening")
    assert callable(mod.screen_mutual_funds)


def test_screen_mutual_funds_reports_missing_extra_clearly() -> None:
    try:
        import honba_data  # noqa: F401
    except ModuleNotFoundError:
        from vyapaar_examples.screening import screen_mutual_funds

        with pytest.raises(ModuleNotFoundError, match="mutual-funds"):
            screen_mutual_funds()
    else:
        pytest.skip("honba_data installed; missing-extra path not reachable")
