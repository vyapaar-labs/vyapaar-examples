"""Vyapaar-examples — learning-path helpers and shared ported harness for the numbered examples.

Deterministic, offline helpers for the numbered example scripts: synthetic
Decimal-paise bar generation, minimal indicators, performance metrics, a simple
bar-by-bar backtester, walk-forward optimization, and a scripted fake LLM.
"""

from __future__ import annotations

from vyapaar_examples._compat import VYAAPAAR_AVAILABLE
from vyapaar_examples.backtest import Backtest, BacktestResult
from vyapaar_examples.data import Bar, SampleInstruments, synthetic_bars, trending_bars
from vyapaar_examples.fake_llm import ScriptedFakeLlm
from vyapaar_examples.metrics import PerformanceMetrics, Trade, compute_metrics
from vyapaar_examples.sdk import RSI, SMA
from vyapaar_examples.walkforward import walk_forward_optimize, walk_forward_windows

__version__ = "0.1.0"

__all__ = [
    "RSI",
    "SMA",
    "VYAAPAAR_AVAILABLE",
    "Backtest",
    "BacktestResult",
    "Bar",
    "PerformanceMetrics",
    "SampleInstruments",
    "ScriptedFakeLlm",
    "Trade",
    "__version__",
    "compute_metrics",
    "synthetic_bars",
    "trending_bars",
    "walk_forward_optimize",
    "walk_forward_windows",
]
