from __future__ import annotations

import importlib.util
from pathlib import Path


def test_mutual_funds_03_imports() -> None:
    path = (
        Path(__file__).resolve().parents[2]
        / "examples"
        / "mutual_funds"
        / "03_category_analysis.py"
    )
    spec = importlib.util.spec_from_file_location("mutual_funds_03_check", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module is not None
