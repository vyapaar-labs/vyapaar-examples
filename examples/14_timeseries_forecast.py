"""14 — Time-series forecasting with the Theta method.

Mirrors ``vyapaar-agent-forecast``'s default ``ThetaForecaster``: fit a linear
trend, build the θ=2 line, smooth it with simple exponential smoothing, fit a
drift line on the second half of the series, and combine the two for an
``h``-step forecast with a symmetric prediction interval. Everything except the
normal quantile is exact ``Decimal``.

Pitfalls::
    - Forecast ≠ edge: a point forecast and its interval are a probability
      statement about the fitted process, not a promise about the market.
    - Stationarity: Theta assumes the detrended process is mean-reverting; on
      regime-changing Indian indices the drift estimate can lag reality.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from vyapaar_examples import SampleInstruments, synthetic_bars
from vyapaar_examples.quant import ols, std_dev

DECIMAL_8 = Decimal("0.00000001")
ALPHA = Decimal("0.5")


@dataclass(frozen=True, slots=True)
class ThetaFit:
    """A fitted Theta model (the crate's fitted-state mirror)."""

    ses_level: Decimal
    drift_intercept: Decimal
    drift_slope: Decimal
    n: int
    resid_std: Decimal


def _ses(series: list[Decimal], alpha: Decimal) -> Decimal:
    """Final smoothed level of a series under simple exponential smoothing."""
    level = series[0]
    for value in series[1:]:
        level = alpha * value + (Decimal(1) - alpha) * level
    return level


def fit_theta(prices: list[Decimal]) -> ThetaFit:
    """Fit the Theta model (requires at least 3 observations, like the crate)."""
    n = len(prices)
    if n < 3:
        raise ValueError("theta needs at least 3 observations")
    times = [Decimal(i) for i in range(n)]
    design = [[Decimal(1), t] for t in times]

    intercept, slope = ols(design, prices)
    theta_line = [y + slope * Decimal(i) for i, y in enumerate(prices)]
    ses_level = _ses(theta_line, ALPHA)

    half = n // 2
    half_design = [[Decimal(1), t] for t in times[half:]]
    drift_intercept, drift_slope = ols(half_design, prices[half:])

    residuals = [y - (intercept + slope * Decimal(i)) for i, y in enumerate(prices)]
    return ThetaFit(
        ses_level=ses_level,
        drift_intercept=drift_intercept,
        drift_slope=drift_slope,
        n=n,
        resid_std=std_dev(residuals),
    )


def forecast(fit: ThetaFit, horizon: int) -> list[Decimal]:
    """Produce ``horizon`` step-ahead point forecasts."""
    if horizon <= 0:
        raise ValueError("horizon must be at least 1")
    return [
        ALPHA * fit.ses_level
        + ALPHA * (fit.drift_intercept + fit.drift_slope * Decimal(fit.n - 1 + step))
        for step in range(horizon)
    ]


def prediction_interval(
    point: list[Decimal], resid_std: Decimal, pct: Decimal
) -> tuple[list[Decimal], list[Decimal]]:
    """Two-sided normal interval around each point forecast.

    Half-width grows with the forecast step (``z * sigma_hat * sqrt(step + 1)``), matching
    the crate's interval builder.
    """
    z = _normal_quantile((Decimal(1) + pct) / Decimal(2))
    lower = [value - z * resid_std * Decimal(step + 1).sqrt() for step, value in enumerate(point)]
    upper = [value + z * resid_std * Decimal(step + 1).sqrt() for step, value in enumerate(point)]
    return lower, upper


def _normal_quantile(p: Decimal) -> Decimal:
    """``z`` such that ``Φ(z) = p``, by bisection over ``math.erf``."""
    if not Decimal(0) < p < Decimal(1):
        raise ValueError("probability must lie strictly inside (0, 1)")
    target = float(p)
    lo, hi = -6.0, 6.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        cdf = 0.5 * (1.0 + math.erf(mid / math.sqrt(2.0)))
        if cdf < target:
            lo = mid
        else:
            hi = mid
    return Decimal(str(0.5 * (lo + hi))).quantize(DECIMAL_8, rounding=ROUND_HALF_UP)


def main() -> dict[str, object]:
    instrument = SampleInstruments.NIFTY50
    bars = synthetic_bars(instrument.value, days=120, seed=11)
    prices = [bar.close for bar in bars]

    fit = fit_theta(prices)
    horizon = 10
    point = forecast(fit, horizon)
    lower, upper = prediction_interval(point, fit.resid_std, Decimal("0.80"))

    return {
        "instrument": instrument.value,
        "observations": len(prices),
        "horizon": horizon,
        "last_price": str(prices[-1]),
        "point_forecast": [str(value) for value in point],
        "interval_lower": [str(value) for value in lower],
        "interval_upper": [str(value) for value in upper],
        "interval_contains_point": all(
            lo <= p <= hi for lo, p, hi in zip(lower, point, upper, strict=True)
        ),
        "all_decimal": all(isinstance(value, Decimal) for value in point + lower + upper),
    }


if __name__ == "__main__":
    print(main())
