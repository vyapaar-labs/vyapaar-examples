"""Shared fixtures: load numbered example modules by file path."""

from __future__ import annotations

import importlib.util
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = ROOT / "examples"


@pytest.fixture
def load_example() -> Callable[[str], ModuleType]:
    """Load an ``examples/NN_name.py`` module via file location (digit names
    cannot use ``import``)."""
    cache: dict[str, ModuleType] = {}

    def _load(name: str) -> ModuleType:
        if name in cache:
            return cache[name]
        path = EXAMPLES_DIR / f"{name}.py"
        if not path.exists():
            raise FileNotFoundError(f"example not found: {path}")
        spec = importlib.util.spec_from_file_location(f"examples.{name}", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        cache[name] = module
        return module

    return _load
