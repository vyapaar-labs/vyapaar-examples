def test_vyapaar_examples_import():
    import vyapaar_examples

    assert vyapaar_examples.__version__ == "0.1.0"
    assert vyapaar_examples.Backtest is not None
    assert vyapaar_examples.ScriptedFakeLlm is not None
