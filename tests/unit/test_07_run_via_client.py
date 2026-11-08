"""backtesting/07_run_via_client: smoke test for the run-service client example.

``vyapaar.client`` is not on the wheel yet (gap
``0004-vyapaar-wheel-display-universes-client``), so the example degrades to a clear
error at ``main()`` time instead of raising ``ImportError`` at import time; this test
exercises exactly that degrade-gracefully contract (D7).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_PATH = Path(__file__).resolve().parents[2] / "examples" / "backtesting" / "07_run_via_client.py"


@pytest.fixture(scope="module")
def example():
    spec = importlib.util.spec_from_file_location("run_via_client", _PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_module_imports_cleanly(example):
    assert hasattr(example, "main")
    assert hasattr(example, "run_inproc")
    assert hasattr(example, "run_http")


def test_main_requires_data_dir(example):
    with pytest.raises(SystemExit):
        example.main([])


def test_main_reports_missing_client_surface(example, capsys):
    code = example.main(["--data-dir", "."])
    assert code == 1
    err = capsys.readouterr().err
    assert "vyapaar.client" in err
    assert "0004" in err
