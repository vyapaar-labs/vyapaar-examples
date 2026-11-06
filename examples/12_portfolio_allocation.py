"""12 — Portfolio allocation: mean-variance and risk parity.

Mirrors ``vyapaar-ledger-allocation``'s Phase 1 engine: an exact-Decimal
Markowitz tangency portfolio and an equal-risk-contribution risk-parity
allocation over a synthetic three-name universe, with an optional per-name
weight bound projected by iterative clip-and-renormalize. Every number is a
``Decimal``; the Rust crate is the canonical engine and this script walks the
same math for learning.

Pitfalls::
    - Garbage-in-garbage-out: the optimizer is only as good as its return and
      covariance estimates. Markowitz magnifies estimation error into extreme
      corner weights — always sanity-check the input moments.
    - Long-only reality: unconstrained mean-variance can produce short
      positions; Indian retail accounts are effectively long-only, so weight
      bounds are not optional in production.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from vyapaar_examples import Bar, SampleInstruments, synthetic_bars
from vyapaar_examples.quant import covariance_matrix, mean, returns, solve_linear_system

EPS = Decimal("1e-9")
ANNUALIZATION = Decimal(252)
UNIVERSE = [SampleInstruments.NIFTY50, SampleInstruments.BANKNIFTY, SampleInstruments.RELIANCE]


@dataclass(frozen=True, slots=True)
class AllocationResult:
    """The auditable output of one allocation objective."""

    weights: list[Decimal]
    sums_to_one: bool
    respects_bounds: bool


def _annualized_moments(
    bars_by_instrument: list[list[Bar]],
) -> tuple[list[Decimal], list[list[Decimal]]]:
    """Daily price panels → annualized expected returns and covariance."""
    panels = [returns([bar.close for bar in bars]) for bars in bars_by_instrument]
    mean_daily = [mean(panel) for panel in panels]
    cov_daily = covariance_matrix([list(col) for col in zip(*panels, strict=True)])
    means_annual = [value * ANNUALIZATION for value in mean_daily]
    cov_annual = [[value * ANNUALIZATION for value in row] for row in cov_daily]
    return means_annual, cov_annual


def mean_variance(
    expected_returns: list[Decimal],
    covariance: list[list[Decimal]],
    risk_free_rate: Decimal,
) -> list[Decimal]:
    """Tangency portfolio ``w ∝ Σ⁻¹(μ - r_f)``, normalized to sum to 1."""
    rhs = [mu - risk_free_rate for mu in expected_returns]
    weights = solve_linear_system(covariance, rhs)
    total = sum(weights, Decimal(0))
    if total == 0:
        raise ValueError("singular covariance produced a zero-weight portfolio")
    return [w / total for w in weights]


def risk_parity(covariance: list[list[Decimal]]) -> list[Decimal]:
    """Equal risk contribution via damped fixed-point iteration.

    Mirrors the Rust engine's iteration on ``wᵢ(Σw)ᵢ = const`` with the
    undamped map known to 2-cycle, hence the ``alpha = 0.5`` damping.
    """
    n = len(covariance)
    weights = [Decimal(1) / Decimal(n)] * n
    for _ in range(512):
        sigma_w = [sum(c * w for c, w in zip(row, weights, strict=True)) for row in covariance]
        if any(value <= 0 for value in sigma_w):
            raise ValueError("covariance is not positive-definite")
        recip = [Decimal(1) / value for value in sigma_w]
        beta = sum(recip, Decimal(0))
        target = [value / beta for value in recip]
        next_weights = [w + (t - w) / Decimal(2) for w, t in zip(weights, target, strict=True)]
        if max(abs(t - w) for w, t in zip(weights, target, strict=True)) <= EPS:
            return next_weights
        weights = next_weights
    return weights


def apply_bounds(weights: list[Decimal], bounds: list[tuple[Decimal, Decimal]]) -> list[Decimal]:
    """Iterative clip-and-renormalize into per-name boxes, keeping ``Σw = 1``.

    Mirrors ``vyapaar-ledger-allocation``'s documented Phase-1 projection:
    clip each weight to its ``[min, max]`` box, then re-scale the weights that
    are still strictly inside their bounds so the portfolio re-sums to 1.
    """
    result = list(weights)
    n = len(result)
    for _ in range(n + 4):
        result = [min(max(w, lo), hi) for w, (lo, hi) in zip(result, bounds, strict=True)]
        if abs(sum(result, Decimal(0)) - Decimal(1)) <= EPS:
            return result
        free_sum = sum(
            w for w, (lo, hi) in zip(result, bounds, strict=True) if w > lo + EPS and w < hi - EPS
        )
        if free_sum <= EPS:
            raise ValueError("cannot re-normalize weights to sum to 1 within bounds")
        pinned = sum(result, Decimal(0)) - free_sum
        factor = (Decimal(1) - pinned) / free_sum
        result = [
            w * factor if w > lo + EPS and w < hi - EPS else w
            for w, (lo, hi) in zip(result, bounds, strict=True)
        ]
    raise ValueError("clip-and-renormalize did not converge")


def _check(
    weights: list[Decimal], bounds: list[tuple[Decimal, Decimal]] | None
) -> AllocationResult:
    sums_to_one = abs(sum(weights, Decimal(0)) - Decimal(1)) <= EPS
    respects = True
    if bounds is not None:
        respects = all(
            lo - EPS <= w <= hi + EPS for w, (lo, hi) in zip(weights, bounds, strict=True)
        )
    return AllocationResult(weights=weights, sums_to_one=sums_to_one, respects_bounds=respects)


def main() -> dict[str, object]:
    as_of = datetime(2024, 6, 28, tzinfo=UTC)
    bars_by_instrument = [
        synthetic_bars(instrument.value, days=120, seed=index + 1)
        for index, instrument in enumerate(UNIVERSE)
    ]
    expected_returns, covariance = _annualized_moments(bars_by_instrument)

    risk_free_rate = Decimal("0.05")
    mv = _check(mean_variance(expected_returns, covariance, risk_free_rate), None)
    rp = _check(risk_parity(covariance), None)

    # RELIANCE capped at 30% — a plausible single-name concentration limit.
    bounds = [
        (Decimal(0), Decimal(1)),
        (Decimal(0), Decimal(1)),
        (Decimal(0), Decimal("0.30")),
    ]
    rp_bounded = _check(apply_bounds(rp.weights, bounds), bounds)

    return {
        "as_of": as_of.isoformat(),
        "universe_size": len(UNIVERSE),
        "universe": [instrument.value for instrument in UNIVERSE],
        "expected_returns": [str(value) for value in expected_returns],
        "mean_variance_weights": [str(value) for value in mv.weights],
        "risk_parity_weights": [str(value) for value in rp.weights],
        "risk_parity_bounded_weights": [str(value) for value in rp_bounded.weights],
        "mv_sums_to_one": mv.sums_to_one,
        "rp_sums_to_one": rp.sums_to_one,
        "bounded_sums_to_one": rp_bounded.sums_to_one,
        "bounded_respects_cap": rp_bounded.respects_bounds,
        "bounded_weights_differ": rp_bounded.weights != rp.weights,
        "all_decimal": all(
            isinstance(value, Decimal) for value in mv.weights + rp.weights + rp_bounded.weights
        ),
    }


if __name__ == "__main__":
    print(main())
