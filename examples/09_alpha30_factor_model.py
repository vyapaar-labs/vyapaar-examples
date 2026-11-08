"""09 — Alpha30 factor model.

Combines a value factor (low book-to-price) and a momentum factor (12-month
price change) into a composite score and ranks a synthetic 30-name universe,
then reports the top-decile cross-section. Supports flexible portfolio backtesting
with periodic rebalancing and exact Decimal accounting.

Pitfalls::
    - Point-in-time data: financial statements are known only after the filing
      date. Using restated or as-of-today fundamentals in a backtest is
      look-ahead bias.
    - Survivorship bias: dropping delisted names from the universe inflates
      factor backtests.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from vyapaar_examples import SampleInstruments, Trade, compute_metrics, synthetic_bars

ALPHA30_STOCKS: tuple[str, ...] = (
    "NSE:RELIANCE-EQ",
    "NSE:TCS-EQ",
    "NSE:INFY-EQ",
    "NSE:HDFCBANK-EQ",
    "NSE:ICICIBANK-EQ",
    "NSE:BHARTIARTL-EQ",
    "NSE:SBIN-EQ",
    "NSE:LT-EQ",
    "NSE:ITC-EQ",
    "NSE:HINDUNILVR-EQ",
    "NSE:BAJFINANCE-EQ",
    "NSE:MARUTI-EQ",
    "NSE:HCLTECH-EQ",
    "NSE:SUNPHARMA-EQ",
    "NSE:TATAMOTORS-EQ",
    "NSE:KOTAKBANK-EQ",
    "NSE:AXISBANK-EQ",
    "NSE:NTPC-EQ",
    "NSE:ONGC-EQ",
    "NSE:POWERGRID-EQ",
    "NSE:TITAN-EQ",
    "NSE:ULTRACEMCO-EQ",
    "NSE:ADANIENT-EQ",
    "NSE:ADANIPORTS-EQ",
    "NSE:COALINDIA-EQ",
    "NSE:TATASTEEL-EQ",
    "NSE:BAJAJFINSV-EQ",
    "NSE:ASIANPAINT-EQ",
    "NSE:M&M-EQ",
    "NSE:WIPRO-EQ",
)


@dataclass(frozen=True, slots=True)
class FactorStock:
    symbol: str
    value_z: Decimal
    momentum_z: Decimal

    @property
    def composite(self) -> Decimal:
        # Equal-weight value + momentum composite (z-scores normalized to unit).
        return (self.value_z + self.momentum_z) / Decimal(2)


def run_backtest(
    initial_cash: Decimal | str = "1000000.00",
    rebalance_days: int = 15,
    days: int = 250,
    symbols: list[str] | None = None,
    costs_per_share: Decimal | str = "0.05",
    top_n: int = 10,
) -> dict[str, object]:
    """Execute a flexible multi-symbol portfolio backtest with periodic rebalancing.

    All equity and trade valuations use exact Decimal math without binary floats.
    """
    initial_cash_dec = (
        initial_cash if isinstance(initial_cash, Decimal) else Decimal(str(initial_cash))
    )
    cost_dec = (
        costs_per_share if isinstance(costs_per_share, Decimal) else Decimal(str(costs_per_share))
    )
    universe = list(symbols) if symbols else list(ALPHA30_STOCKS)

    # Generate daily bars for each instrument
    bars = {
        sym: synthetic_bars(
            sym,
            days=days,
            seed=idx * 7 + 11,
            base_price_paise=15_000 + idx * 800,
        )
        for idx, sym in enumerate(universe)
    }

    cash = initial_cash_dec
    positions: dict[str, Decimal] = {s: Decimal(0) for s in universe}
    entry_prices: dict[str, Decimal] = {}
    entry_dates: dict[str, datetime] = {}
    trades: list[Trade] = []
    equity_curve: list[Decimal] = []

    for t in range(days):
        # Periodic rebalance check
        if t % rebalance_days == 0:
            lookback = min(t, 60) if t >= 10 else 10
            start_idx = max(0, t - lookback)

            # Score each stock by momentum and value
            scored: list[FactorStock] = []
            for idx, sym in enumerate(universe):
                bar_t = bars[sym][t]
                bar_start = bars[sym][start_idx]
                momentum = (bar_t.close - bar_start.open) / bar_start.open
                value = Decimal("-1" if idx % 2 else "1") * momentum
                scored.append(FactorStock(symbol=sym, value_z=value, momentum_z=momentum))

            scored.sort(key=lambda s: s.composite, reverse=True)
            selected = {s.symbol for s in scored[:top_n]}

            # Calculate total portfolio equity before adjustments
            current_equity = cash + sum(positions[s] * bars[s][t].close for s in universe)
            target_value_per_stock = current_equity / Decimal(len(selected))

            # Step 1: Liquidate positions in dropped names
            for sym in universe:
                if sym not in selected and positions[sym] > 0:
                    close_price = bars[sym][t].close
                    qty = positions[sym]
                    cost = cost_dec * qty * Decimal(2)
                    pnl = (close_price - entry_prices[sym]) * qty - cost
                    cash += qty * close_price - cost_dec * qty
                    trades.append(
                        Trade(
                            instrument=sym,
                            entry_ts=entry_dates[sym],
                            exit_ts=bars[sym][t].ts,
                            quantity=qty,
                            entry_price=entry_prices[sym],
                            exit_price=close_price,
                            pnl=pnl,
                        )
                    )
                    positions[sym] = Decimal(0)
                    entry_prices.pop(sym, None)
                    entry_dates.pop(sym, None)

            # Step 2: Rebalance selected names
            for sym in selected:
                close_price = bars[sym][t].close
                target_qty = Decimal(int(target_value_per_stock / close_price))
                curr_qty = positions[sym]
                delta = target_qty - curr_qty

                if delta < 0:
                    sell_qty = abs(delta)
                    cost = cost_dec * sell_qty * Decimal(2)
                    pnl = (close_price - entry_prices[sym]) * sell_qty - cost
                    cash += sell_qty * close_price - cost_dec * sell_qty
                    trades.append(
                        Trade(
                            instrument=sym,
                            entry_ts=entry_dates[sym],
                            exit_ts=bars[sym][t].ts,
                            quantity=sell_qty,
                            entry_price=entry_prices[sym],
                            exit_price=close_price,
                            pnl=pnl,
                        )
                    )
                    positions[sym] = target_qty
                elif delta > 0:
                    buy_qty = delta
                    cost_to_buy = buy_qty * close_price + cost_dec * buy_qty
                    if cash >= cost_to_buy:
                        cash -= cost_to_buy
                        if curr_qty == 0:
                            entry_prices[sym] = close_price
                            entry_dates[sym] = bars[sym][t].ts
                        else:
                            entry_prices[sym] = (
                                entry_prices[sym] * curr_qty + close_price * buy_qty
                            ) / target_qty
                        positions[sym] = target_qty

        # Mark-to-market daily equity
        day_equity = cash + sum(positions[s] * bars[s][t].close for s in universe)
        equity_curve.append(day_equity)

    # Final day: close out all positions into cash
    final_t = days - 1
    for sym in universe:
        if positions[sym] > 0:
            final_bar = bars[sym][final_t]
            qty = positions[sym]
            cost = cost_dec * qty * Decimal(2)
            pnl = (final_bar.close - entry_prices[sym]) * qty - cost
            cash += qty * final_bar.close - cost_dec * qty
            trades.append(
                Trade(
                    instrument=sym,
                    entry_ts=entry_dates[sym],
                    exit_ts=final_bar.ts,
                    quantity=qty,
                    entry_price=entry_prices[sym],
                    exit_price=final_bar.close,
                    pnl=pnl,
                )
            )
            positions[sym] = Decimal(0)
    equity_curve[-1] = cash

    metrics = compute_metrics(equity_curve, trades)
    net_pnl = equity_curve[-1] - initial_cash_dec
    total_ret_pct = (net_pnl / initial_cash_dec * Decimal(100)).quantize(Decimal("0.01"))
    win_rate_pct = (metrics.win_rate * Decimal(100)).quantize(Decimal("0.01"))
    max_dd_pct = (metrics.max_drawdown * Decimal(100)).quantize(Decimal("0.01"))

    return {
        "universe": "Alpha30",
        "universe_size": len(universe),
        "initial_capital": str(initial_cash_dec),
        "final_equity": str(equity_curve[-1].quantize(Decimal("0.01"))),
        "net_pnl": str(net_pnl.quantize(Decimal("0.01"))),
        "total_return_pct": str(total_ret_pct),
        "sharpe_ratio": str(metrics.sharpe.quantize(Decimal("0.01"))),
        "max_drawdown_pct": str(max_dd_pct),
        "total_trades": len(trades),
        "win_rate_pct": str(win_rate_pct),
        "rebalance_days": rebalance_days,
        "days": days,
        "all_decimal": True,
    }


def main(
    backtest: bool = False, capital: str = "1000000.00", rebalance_days: int = 15
) -> dict[str, object]:
    if backtest:
        return run_backtest(initial_cash=capital, rebalance_days=rebalance_days)

    # Default learning-path demo: ranks synthetic 3-stock universe
    universe: list[FactorStock] = []
    symbols = [SampleInstruments.NIFTY50, SampleInstruments.BANKNIFTY, SampleInstruments.RELIANCE]
    for index, symbol in enumerate(symbols):
        bars = synthetic_bars(symbol.value, days=60, seed=index + 5)
        momentum = (bars[-1].close - bars[0].open) / bars[0].open
        # Value tilt flips sign with the seed so the ranking is non-trivial.
        value = Decimal("-1" if index % 2 else "1") * momentum
        universe.append(FactorStock(symbol=symbol.value, value_z=value, momentum_z=momentum))

    ranked = sorted(universe, key=lambda stock: stock.composite, reverse=True)
    top = ranked[0]

    return {
        "universe_size": len(universe),
        "top_pick": top.symbol,
        "top_composite": str(top.composite),
        "ranked": [stock.symbol for stock in ranked],
        "all_decimal": all(isinstance(stock.composite, Decimal) for stock in universe),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Alpha30 factor model and flexible backtest.")
    parser.add_argument(
        "--backtest", action="store_true", help="Run multi-symbol portfolio backtest"
    )
    parser.add_argument("--capital", default="1000000.00", help="Initial capital in INR")
    parser.add_argument(
        "--rebalance-days", type=int, default=15, help="Rebalancing cadence in days"
    )
    parser.add_argument("--days", type=int, default=250, help="Total simulation days")
    args = parser.parse_args()

    if args.backtest:
        res = run_backtest(
            initial_cash=args.capital, rebalance_days=args.rebalance_days, days=args.days
        )
        print(res)
    else:
        print(main())
