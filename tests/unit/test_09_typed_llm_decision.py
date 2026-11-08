"""tests/unit/test_09_typed_llm_decision: typed LLM decision invariants and demo."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_PATH = (
    Path(__file__).resolve().parents[2] / "examples" / "ai_research" / "09_typed_llm_decision.py"
)


@pytest.fixture(scope="module")
def example():
    spec = importlib.util.spec_from_file_location("typed_llm_decision", _PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_executes_successfully(example) -> None:
    res = example.run()
    assert res["status"] == "success"
    assert res["sized_quantity"] == 40.0
    assert res["vetoed"] is True
    assert res["increase_rejected"] is True
    assert res["fail_closed"] is True
    assert res["protective_exit_overridden"] is True
    assert len(res["records"]) == 2


def test_main_writes_same_json_to_out(example, tmp_path) -> None:
    out = tmp_path / "decisions.json"
    assert example.main(["--out", str(out)]) == 0
    assert out.is_file()
    data = json.loads(out.read_text())
    assert data["status"] == "success"
    assert len(data["records"]) == 2


def test_main_happy_path_returns_zero(example) -> None:
    assert example.main([]) == 0
