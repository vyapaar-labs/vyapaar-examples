"""13 — Options pricing: Black-Scholes, Greeks, implied volatility.

Mirrors ``vyapaar-market-pricing``'s ``BlackScholesModel``: closed-form fair
value, the five Greeks, and implied volatility by root-finding over the pricing
formula, for a synthetic NFO NIFTY option.

Pitfalls::
    - f64 exception (documented): Black-Scholes needs the normal CDF, ``exp``,
      and ``ln``. Like the Rust pricing crate, this example computes in
      ``math`` floats internally and rounds every result to ``Decimal`` at the
      boundary — prices and strikes never leave the example as floats.
    - Volatility smile: a single flat volatility is wrong for real index
      options; quoted implied volatilities differ by strike and expiry.
    - Day counts: time to expiry is calendar days / 365; exchanges and
      clearinghouses use their own day-count conventions.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from vyapaar_examples import SampleInstruments

INSTRUMENT = SampleInstruments.NIFTY50
SYMBOL = "NFO:NIFTY"
DECIMAL_8 = Decimal("0.00000001")


@dataclass(frozen=True, slots=True)
class Greeks:
    """Fair value plus the five Greeks, all ``Decimal`` at the boundary."""

    price: Decimal
    delta: Decimal
    gamma: Decimal
    theta: Decimal
    vega: Decimal
    rho: Decimal


def _to_decimal(value: float) -> Decimal:
    """Round an ``f64`` working value into an 8-decimal ``Decimal``."""
    return Decimal(str(value)).quantize(DECIMAL_8, rounding=ROUND_HALF_UP)


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _d1_d2(
    spot: float,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    dividend_yield: float,
    volatility: float,
) -> tuple[float, float]:
    sqrt_t = math.sqrt(time_to_expiry)
    d1 = (
        math.log(spot / strike)
        + (risk_free_rate - dividend_yield + 0.5 * volatility * volatility) * time_to_expiry
    ) / (volatility * sqrt_t)
    return d1, d1 - volatility * sqrt_t


def _bs_price_f64(
    spot: float,
    strike: float,
    time_to_expiry: float,
    risk_free_rate: float,
    dividend_yield: float,
    volatility: float,
    is_call: bool,
) -> float:
    d1, d2 = _d1_d2(spot, strike, time_to_expiry, risk_free_rate, dividend_yield, volatility)
    if is_call:
        return spot * math.exp(-dividend_yield * time_to_expiry) * _norm_cdf(d1) - (
            strike * math.exp(-risk_free_rate * time_to_expiry) * _norm_cdf(d2)
        )
    return strike * math.exp(-risk_free_rate * time_to_expiry) * _norm_cdf(-d2) - (
        spot * math.exp(-dividend_yield * time_to_expiry) * _norm_cdf(-d1)
    )


def black_scholes(
    spot: Decimal,
    strike: Decimal,
    time_to_expiry: Decimal,
    risk_free_rate: Decimal,
    dividend_yield: Decimal,
    volatility: Decimal,
    is_call: bool,
) -> Decimal:
    """Fair value of a European option (``Decimal`` boundary, ``f64`` internals)."""
    if spot <= 0 or strike <= 0 or time_to_expiry <= 0 or volatility <= 0:
        raise ValueError("spot, strike, time-to-expiry, and volatility must be positive")
    fair = _bs_price_f64(
        float(spot),
        float(strike),
        float(time_to_expiry),
        float(risk_free_rate),
        float(dividend_yield),
        float(volatility),
        is_call,
    )
    return _to_decimal(fair)


def greeks(
    spot: Decimal,
    strike: Decimal,
    time_to_expiry: Decimal,
    risk_free_rate: Decimal,
    dividend_yield: Decimal,
    volatility: Decimal,
    is_call: bool,
) -> Greeks:
    """Fair value plus delta/gamma/theta/vega/rho (the Rust crate's conventions)."""
    if spot <= 0 or strike <= 0 or time_to_expiry <= 0 or volatility <= 0:
        raise ValueError("spot, strike, time-to-expiry, and volatility must be positive")
    s = float(spot)
    k = float(strike)
    t = float(time_to_expiry)
    r = float(risk_free_rate)
    q = float(dividend_yield)
    sigma = float(volatility)
    d1, d2 = _d1_d2(s, k, t, r, q, sigma)
    sqrt_t = math.sqrt(t)
    pdf_d1 = _norm_pdf(d1)
    nd1 = _norm_cdf(d1)
    nd2 = _norm_cdf(d2)

    price = _bs_price_f64(s, k, t, r, q, sigma, is_call)
    gamma = math.exp(-q * t) * pdf_d1 / (s * sigma * sqrt_t)
    vega = s * math.exp(-q * t) * pdf_d1 * sqrt_t
    if is_call:
        delta = math.exp(-q * t) * nd1
        theta = (
            -math.exp(-q * t) * s * pdf_d1 * sigma / (2.0 * sqrt_t)
            - r * k * math.exp(-r * t) * nd2
            + q * s * math.exp(-q * t) * nd1
        )
        rho = k * t * math.exp(-r * t) * nd2
    else:
        delta = math.exp(-q * t) * (nd1 - 1.0)
        theta = (
            -math.exp(-q * t) * s * pdf_d1 * sigma / (2.0 * sqrt_t)
            + r * k * math.exp(-r * t) * _norm_cdf(-d2)
            - q * s * math.exp(-q * t) * _norm_cdf(-d1)
        )
        rho = -k * t * math.exp(-r * t) * _norm_cdf(-d2)

    return Greeks(
        price=_to_decimal(price),
        delta=_to_decimal(delta),
        gamma=_to_decimal(gamma),
        theta=_to_decimal(theta),
        vega=_to_decimal(vega),
        rho=_to_decimal(rho),
    )


def implied_volatility(
    spot: Decimal,
    strike: Decimal,
    time_to_expiry: Decimal,
    risk_free_rate: Decimal,
    dividend_yield: Decimal,
    volatility: Decimal,
    target_price: Decimal,
    is_call: bool,
) -> Decimal:
    """Recover the volatility that reproduces ``target_price`` by bisection."""
    if target_price <= 0:
        raise ValueError("target_price must be strictly positive")
    s = float(spot)
    k = float(strike)
    t = float(time_to_expiry)
    r = float(risk_free_rate)
    q = float(dividend_yield)
    target = float(target_price)

    # Price is monotone increasing in volatility — bisection over the domain.
    lo, hi = 1e-4, 5.0
    if target < _bs_price_f64(s, k, t, r, q, lo, is_call) or target > _bs_price_f64(
        s, k, t, r, q, hi, is_call
    ):
        raise ValueError("target_price is outside the achievable range")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        price = _bs_price_f64(s, k, t, r, q, mid, is_call)
        if abs(price - target) < 1e-9:
            return _to_decimal(mid)
        if price < target:
            lo = mid
        else:
            hi = mid
    raise ValueError("implied-volatility solver did not converge")


def main() -> dict[str, object]:
    # A synthetic NFO weekly: spot near strike, 30 days to expiry, 7% rate.
    spot = Decimal("24950.00")
    strike = Decimal("25000.00")
    time_to_expiry = Decimal(30) / Decimal(365)
    risk_free_rate = Decimal("0.07")
    dividend_yield = Decimal("0.00")
    volatility = Decimal("0.20")

    call = greeks(spot, strike, time_to_expiry, risk_free_rate, dividend_yield, volatility, True)
    put = greeks(spot, strike, time_to_expiry, risk_free_rate, dividend_yield, volatility, False)

    # IV round-trip: recover the 20% volatility from the computed call price.
    iv = implied_volatility(
        spot, strike, time_to_expiry, risk_free_rate, dividend_yield, volatility, call.price, True
    )

    return {
        "symbol": SYMBOL,
        "underlying": INSTRUMENT.value,
        "spot": str(spot),
        "strike": str(strike),
        "call": _greeks_dict(call),
        "put": _greeks_dict(put),
        "implied_volatility": str(iv),
        "iv_recovered": abs(iv - volatility) <= Decimal("0.001"),
        "call_gt_put": call.price > put.price,
        "delta_call_positive": call.delta > 0,
        "delta_put_negative": put.delta < 0,
        "gamma_positive": call.gamma > 0 and put.gamma > 0,
        "all_decimal": all(
            isinstance(value, Decimal)
            for value in (
                call.price,
                call.delta,
                call.gamma,
                call.theta,
                call.vega,
                call.rho,
                put.price,
                put.delta,
                put.gamma,
                put.theta,
                put.vega,
                put.rho,
                iv,
            )
        ),
    }


def _greeks_dict(value: Greeks) -> dict[str, str]:
    return {
        "price": str(value.price),
        "delta": str(value.delta),
        "gamma": str(value.gamma),
        "theta": str(value.theta),
        "vega": str(value.vega),
        "rho": str(value.rho),
    }


if __name__ == "__main__":
    print(main())
