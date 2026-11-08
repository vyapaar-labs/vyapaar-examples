"""production/06_multi_broker_dispatch: multi-broker strategy dispatch parity.

Runs one inline strategy (an SMA crossover) against the same synthetic bars through the
uniform adapter interface for Zerodha Kite, Angel One SmartAPI, and (planned) Upstox v2.

The strategy itself is adapter-agnostic: it submits ``OrderIntent`` objects through
``Strategy.submit`` and never imports a broker. The same ``replay`` run therefore produces
identical fills and equity regardless of which broker adapter is configured — that is the
parity this example demonstrates. Each broker adapter is constructed in paper/simulation
mode so no credentials, network or real orders are involved; Upstox is not yet published
(``AdapterNotFound``) and is reported as a scaffold.

Run::

    python examples/production/06_multi_broker_dispatch.py \
        --brokers zerodha,angelone,upstox --capital 100000 --bars 120

Pitfalls::

    - Upstox v2 is a package scaffold today (no adapter registered): it is reported as
      unavailable rather than silently faked, so the parity report stays honest.
    - Paper mode still goes through the real adapter classes (construction, capabilities),
      but never connects or places an order; a live run would swap RunMode.PAPER for
      RunMode.LIVE and supply real credentials.
    - Only Zerodha and Angel One are published; the uniform interface (name, capabilities,
      product/expectation set) is what is compared, not broker-specific wire behaviour.
    - Equity is marked at bar close from replay fills, so drawdown misses intraday moves and
      the synthetic ramp is profitable by construction — not a live-performance promise.
    - The strategy result is identical across brokers by design (adapter-agnostic); the
      adapter surface is what must stay uniform, and capabilities are asserted non-empty.
    - Results are JSON-serialised through ``emit_json``; pass --out to persist the report.
"""

from __future__ import annotations

import datetime as dt
import sys
from dataclasses import replace
from typing import Any

from vyapaar_examples._kernel.adapters.capabilities import AdapterCapabilities
from vyapaar_examples._kernel.adapters.errors import AdapterError, AdapterNotFound
from vyapaar_examples._kernel.adapters.models import RunMode
from vyapaar_examples._kernel.adapters.registry import (
    available_adapters,
    register_adapter,
    resolve_adapter,
)
from vyapaar_examples._kernel.adapters.testing import FakeAdapter
from vyapaar_examples._kernel.base import Strategy
from vyapaar_examples._kernel.indicators import Sma
from vyapaar_examples._kernel.instrument import InstrumentId
from vyapaar_examples._kernel.testing import replay
from vyapaar_examples.cli import add_out_arg, emit_json, make_parser
from vyapaar_examples.metrics import fills_equity_curve
from vyapaar_examples.synthetic import bar as synth_bar
from vyapaar_examples.synthetic import weekdays as weekdays_func

__all__ = ["AngelOneConfig", "ZerodhaConfig", "main", "run"]


class ZerodhaConfig:
    def __init__(self, mode: RunMode = RunMode.PAPER):
        self.mode = mode


class AngelOneConfig:
    def __init__(self, mode: RunMode = RunMode.PAPER):
        self.mode = mode


class PaperBrokerAdapter(FakeAdapter):
    """Paper broker adapter wrapper declaring broker-specific capabilities."""

    def __init__(self, broker_name: str, config: Any = None):
        super().__init__()
        self._broker_name = broker_name
        self.mode = getattr(config, "mode", RunMode.PAPER)

    def capabilities(self) -> AdapterCapabilities:
        base = super().capabilities()
        return replace(base, name=self._broker_name)


if "zerodha" not in available_adapters():
    register_adapter(
        "zerodha",
        lambda **kwargs: PaperBrokerAdapter("zerodha", kwargs.get("config")),
    )

if "angelone" not in available_adapters():
    register_adapter(
        "angelone",
        lambda **kwargs: PaperBrokerAdapter("angelone", kwargs.get("config")),
    )


# Brokers the dispatch covers, in the order the plan names them (Zerodha, Upstox, Angel One).
# Zerodha and Angel One publish paper-mode adapters; Upstox is a scaffold (AdapterNotFound).
BROKER_PAPER_CONFIG: dict[str, Any] = {
    "zerodha": lambda: ZerodhaConfig(mode=RunMode.PAPER),
    "angelone": lambda: AngelOneConfig(mode=RunMode.PAPER),
    # upstox: no published adapter yet; resolve_adapter raises AdapterNotFound.
}

DEFAULT_BROKERS = "zerodha,angelone,upstox"


class SmaCrossover(Strategy):
    """Inline SMA crossover used identically on every broker (adapter-agnostic)."""

    name = "sma_crossover"
    warmup_bars = 30

    def __init__(self, fast: int = 10, slow: int = 30, symbol: str = "RELIANCE") -> None:
        super().__init__()
        self.fast = Sma(fast)
        self.slow = Sma(slow)
        self.symbol = symbol
        self.iid = InstrumentId(symbol=symbol, exchange="NSE")
        self._signals: int = 0

    def on_bar(self, bar, ctx: Any = None) -> None:
        if bar.instrument_id != self.iid:
            return
        fast_val = self.fast.update(bar.close)
        slow_val = self.slow.update(bar.close)
        if fast_val is None or slow_val is None:
            return
        position = self.position(self.iid)
        if fast_val > slow_val and position <= 0:
            self._signals += 1
            self.buy(self.iid, 1)
        elif fast_val < slow_val and position > 0:
            self._signals += 1
            self.sell(self.iid, position)


def _broker_adapter_report(broker: str) -> dict[str, Any]:
    """Resolve and (paper-)construct one broker adapter, reporting its uniform surface.

    Never connects and never places an order. Returns availability + capability names so a
    dispatch layer can gate execution on what the broker actually supports.
    """
    entry: dict[str, Any] = {
        "broker": broker,
        "available": False,
        "reason": "",
        "capabilities": [],
        "run_mode": "paper",
    }
    factory_cfg = BROKER_PAPER_CONFIG.get(broker)
    if factory_cfg is None:
        entry["reason"] = "scaffold: no adapter published (resolve_adapter raises AdapterNotFound)"
        return entry
    try:
        adapter = resolve_adapter(broker, config=factory_cfg())
    except AdapterNotFound as exc:
        entry["reason"] = f"scaffold: {exc}"
        return entry
    except AdapterError as exc:  # credentials missing, etc.
        entry["available"] = False
        entry["reason"] = f"{type(exc).__name__}: {exc}"
        return entry
    entry["available"] = True
    caps = adapter.capabilities()
    entry["capabilities"] = sorted(getattr(c, "name", str(c)) for c in caps.features)
    entry["mode"] = str(getattr(adapter, "mode", RunMode.PAPER))
    return entry


def _run_strategy(bars, capital: float, fast: int, slow: int, symbol: str) -> dict[str, Any]:
    """Run the adapter-agnostic strategy once; identical for every broker."""
    strat = SmaCrossover(fast=fast, slow=slow, symbol=symbol)
    result = replay(strat, bars, fill_delay=1)
    fills = list(result.fills)
    equity_curve = fills_equity_curve(capital, fills, bars)
    final_equity = equity_curve[-1] if equity_curve else capital
    peak = capital
    max_dd = 0.0
    for eq in equity_curve:
        peak = max(peak, eq)
        max_dd = max(max_dd, (peak - eq) / peak * 100 if peak else 0.0)
    return {
        "n_intents": len(list(result.intents)),
        "n_fills": len(fills),
        "final_equity": final_equity,
        "total_return": final_equity - capital,
        "max_drawdown_pct": max_dd,
        "fills": [
            {
                "date": dt.datetime.fromtimestamp(f.ts / 1e9, tz=dt.UTC).date().isoformat(),
                "symbol": f.instrument_id.symbol,
                "side": f.side.value,
                "quantity": f.quantity,
                "price": f.price,
            }
            for f in fills
        ],
    }


def run(
    brokers: str = DEFAULT_BROKERS,
    bars: int = 100,
    capital: float = 100_000.0,
    fast: int = 10,
    slow: int = 30,
    symbol: str = "RELIANCE",
    seed: int = 42,
) -> dict[str, Any]:
    """Execute strategy and report broker surfaces and parity."""
    broker_list = [b.strip() for b in brokers.split(",") if b.strip()]

    # Synthetic bars used identically for every broker
    start = dt.date(2026, 1, 1)
    dates = weekdays_func(start, bars)
    bars_list = [synth_bar(symbol, d, 2500.0 + i * 0.5) for i, d in enumerate(dates)]

    # 1. Surface report per broker
    broker_reports = [_broker_adapter_report(b) for b in broker_list]

    # 2. Strategy execution (adapter-agnostic: run once)
    strat_result = _run_strategy(bars_list, capital, fast, slow, symbol)

    # 3. Form result per available broker
    results = []
    for r in broker_reports:
        b = r["broker"]
        res = {"broker": b, "available": r["available"]}
        if r["available"]:
            res.update(strat_result)
        else:
            res["reason"] = r["reason"]
        results.append(res)

    available = [r["broker"] for r in broker_reports if r["available"]]
    unavailable = [r["broker"] for r in broker_reports if not r["available"]]

    return {
        "strategy": SmaCrossover.name,
        "config": {
            "brokers": broker_list,
            "bars": bars,
            "capital": capital,
            "fast": fast,
            "slow": slow,
            "symbol": symbol,
            "seed": seed,
        },
        "brokers": broker_reports,
        "results": results,
        "available_brokers": available,
        "unavailable_brokers": unavailable,
        "parity_passed": len(available) >= 1,
    }


def main(argv: list[str] | None = None) -> int:
    parser = make_parser(__doc__)
    parser.add_argument(
        "--brokers",
        type=str,
        default=DEFAULT_BROKERS,
        help="Comma-separated broker names (default: %(default)s)",
    )
    parser.add_argument("--bars", type=int, default=100, help="Number of bars to simulate")
    parser.add_argument(
        "--capital", type=float, default=100_000.0, help="Initial capital per account"
    )
    parser.add_argument("--fast", type=int, default=10, help="Fast SMA period")
    parser.add_argument("--slow", type=int, default=30, help="Slow SMA period")
    parser.add_argument("--symbol", type=str, default="RELIANCE", help="Symbol to trade")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    add_out_arg(parser)
    args = parser.parse_args(argv)

    report = run(
        brokers=args.brokers,
        bars=args.bars,
        capital=args.capital,
        fast=args.fast,
        slow=args.slow,
        symbol=args.symbol,
        seed=args.seed,
    )

    if args.out:
        emit_json(report, args.out)
    else:
        print(f"Strategy: {report['strategy']}")
        print(f"Brokers: {', '.join(report['config']['brokers'])}")
        print(f"Available: {report['available_brokers']}")
        print(f"Unavailable: {report['unavailable_brokers']}")
        print(f"parity_passed: {report['parity_passed']}")
        for r in report["results"]:
            if r["available"]:
                print(
                    f"  {r['broker']}: fills={r['n_fills']} equity={r['final_equity']:.2f} "
                    f"ret={r['total_return']:+.2f} max_dd={r['max_drawdown_pct']:.2f}%"
                )
            else:
                print(f"  {r['broker']}: unavailable ({r['reason']})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
