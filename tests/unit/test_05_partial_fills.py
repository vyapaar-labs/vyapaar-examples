"""05_partial_fills regression test."""

from __future__ import annotations


def test_example_05_fills_in_slices_until_complete(load_example) -> None:
    module = load_example("05_partial_fills")
    result = module.main()
    assert result["requested"] == "100"
    assert result["status"] == "complete"
    assert result["filled"] == "100"
    assert result["remaining"] == "0"
    assert result["completed"] is True
