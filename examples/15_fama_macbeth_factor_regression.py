"""15 — Factor regressions: Fama-MacBeth two-pass.

Mirrors ``vyapaar-agent-panel``'s Fama-MacBeth procedure: first-pass
time-series betas of each asset on the factor returns, second-pass
cross-sectional risk premia per period, and t-stats from the time-series
standard errors of the per-period premia. All arithmetic is exact ``Decimal``
via the shared quant helpers.

Pitfalls::
    - Errors-in-variables: the second-pass regressors are estimated betas, not
      observed values; the classic Fama-MacBeth t-stats understate this. The
      Shanken correction exists for a reason.
    - Identification: you need more periods than factors and more assets than
      factors (``T > K + 1`` and ``N > K + 1``) or both passes are
      rank-deficient.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from decimal import Decimal

from vyapaar_examples.quant import mean, ols, std_dev


@dataclass(frozen=True, slots=True)
class FamaMacBethResult:
    """Betas, risk premia, and t-stats (the crate's result mirror)."""

    betas: list[list[Decimal]]
    alphas: list[Decimal]
    lambda_hat: list[Decimal]
    t_stats: list[Decimal]
    mean_abs_alpha: Decimal
    n_periods: int
    n_assets: int
    n_factors: int


def fama_macbeth(
    returns_panel: list[list[Decimal]],
    factor_returns: list[list[Decimal]],
) -> FamaMacBethResult:
    """Two-pass Fama-MacBeth regression.

    ``returns_panel`` is ``T x N`` (rows = periods, columns = assets);
    ``factor_returns`` is ``T x K``.
    """
    t = len(returns_panel)
    if t == 0:
        raise ValueError("returns panel is empty")
    n = len(returns_panel[0])
    k = len(factor_returns[0])
    if len(factor_returns) != t:
        raise ValueError("returns and factor returns must have the same periods")
    if t <= k + 1 or n <= k + 1:
        raise ValueError("need T > K+1 and N > K+1 for both passes to be identified")

    # First pass: per-asset time-series betas on [1, factors].
    betas: list[list[Decimal]] = []
    alphas: list[Decimal] = []
    for asset in range(n):
        y_ts = [returns_panel[p][asset] for p in range(t)]
        design = [[Decimal(1), *factor_returns[p]] for p in range(t)]
        coef = ols(design, y_ts)
        alphas.append(coef[0])
        betas.append(coef[1:])

    # Second pass: per-period cross-sectional premia on [1, betas].
    lambda_series: list[list[Decimal]] = [[] for _ in range(k)]
    alpha_series: list[Decimal] = []
    for p in range(t):
        y_cs = [returns_panel[p][asset] for asset in range(n)]
        design = [[Decimal(1), *betas[asset]] for asset in range(n)]
        coef = ols(design, y_cs)
        for factor, lambda_t in enumerate(coef[1:]):
            lambda_series[factor].append(lambda_t)
        fitted = [sum(a * b for a, b in zip(row, coef, strict=True)) for row in design]
        alpha_series.append(sum(abs(y_cs[i] - fitted[i]) for i in range(n)) / Decimal(n))

    lambda_hat = [mean(series) for series in lambda_series]
    t_stats = [mean(series) / (std_dev(series) / Decimal(t).sqrt()) for series in lambda_series]
    return FamaMacBethResult(
        betas=betas,
        alphas=alphas,
        lambda_hat=lambda_hat,
        t_stats=t_stats,
        mean_abs_alpha=mean(alpha_series),
        n_periods=t,
        n_assets=n,
        n_factors=k,
    )


def _pct(rng: random.Random) -> Decimal:
    """One deterministic daily return in ±1% (integer basis points)."""
    return Decimal(rng.randint(-100, 100)) / Decimal(10000)


def main() -> dict[str, object]:
    # Deterministic synthetic panel: T=12 periods, N=8 assets, K=2 factors.
    rng = random.Random(2024)
    t, n, k = 12, 8, 2
    factor_returns = [[_pct(rng) for _ in range(k)] for _ in range(t)]
    assets_ts: list[list[Decimal]] = []
    for _ in range(n):
        beta = Decimal(rng.randint(50, 150)) / Decimal(100)
        assets_ts.append([beta * factor_returns[p][0] + _pct(rng) for p in range(t)])
    returns_panel = [list(col) for col in zip(*assets_ts, strict=True)]

    result = fama_macbeth(returns_panel, factor_returns)
    all_values = (
        [value for row in result.betas for value in row]
        + result.alphas
        + result.lambda_hat
        + result.t_stats
        + [result.mean_abs_alpha]
    )

    return {
        "n_periods": result.n_periods,
        "n_assets": result.n_assets,
        "n_factors": result.n_factors,
        "beta_shape": [len(result.betas), len(result.betas[0])],
        "lambda": [str(value) for value in result.lambda_hat],
        "t_stats": [str(value) for value in result.t_stats],
        "mean_abs_alpha": str(result.mean_abs_alpha),
        "identified": result.n_periods > result.n_factors + 1
        and result.n_assets > result.n_factors + 1,
        "all_decimal": all(isinstance(value, Decimal) for value in all_values),
    }


if __name__ == "__main__":
    print(main())
