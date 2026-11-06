"""11_autoresearch_loop regression test."""

from __future__ import annotations


def test_example_11_research_loop_is_deterministic(load_example) -> None:
    module = load_example("11_autoresearch_loop")
    result = module.main()
    assert result["deterministic"] is True
    assert result["prompts_seen"] == 3
    assert len(result["iterations"]) == 3
    # Each iteration consumed one scripted hypothesis and backtested it.
    for iteration in result["iterations"]:
        assert "hypothesis" in iteration
        assert iteration["trades"] >= 0
        float(iteration["total_return"])
