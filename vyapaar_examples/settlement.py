"""Settlement cycle resolution for Indian markets + kernel market-pack mirror.

``resolve_settlement_days`` is the CLI/config precedence resolver; the kernel-
mirrored schedule below supplies the market default it falls back to.
"""

from datetime import date, datetime
from typing import Any, Final

# =============================================================================
# Mirrored kernel schedule (markets.india.settlement). Kernel-owner gap:
# 0006-vyapaar-wheel-kernel-domain-surface.
# =============================================================================

__all__ = [
    "INDIA_EXCHANGES",
    "INSTRUMENT_KINDS",
    "nse_equity_settlement_days",
    "settlement_days_for",
    "to_iso_date",
]

# Native hook: the compiled kernel's read of the Rust market-pack schedule is part of
# the wheel surface this mirror does not own, so it is always None here. The fallback
# below mirrors that Rust schedule exactly (T+2 before 2023-01-27, T+1 from then).
# Kernel-owner gap: 0006-vyapaar-wheel-kernel-domain-surface.
_native_nse_equity_settlement_days = None

# Exchange codes served by the India market pack (`nse_bse`).
INDIA_EXCHANGES: Final[frozenset[str]] = frozenset({"NSE", "BSE"})

# Accepted `kind` values; mirrors the non-index variants of `honba_entities::InstrumentKind`.
INSTRUMENT_KINDS: Final[frozenset[str]] = frozenset(
    {"equity", "etf", "bond", "ipo", "future", "option", "fx", "index", "mf"}
)

# T+1 is the market default everywhere outside India's equity delivery cycle.
_DEFAULT_SETTLEMENT_DAYS: Final[int] = 1


# First date every NSE/BSE equity settles T+1; mirrors the Rust schedule (fallback only).
_FALLBACK_T_PLUS_1_FROM: Final[date] = date(2023, 1, 27)


def to_iso_date(as_of: date | datetime | str) -> str:
    """Normalize ``as_of`` (date, datetime or ISO string) to ``YYYY-MM-DD``."""
    if isinstance(as_of, datetime):
        return as_of.date().isoformat()
    if isinstance(as_of, date):
        return as_of.isoformat()
    return date.fromisoformat(as_of.strip()).isoformat()


def nse_equity_settlement_days(as_of: date | datetime | str | None = None) -> int:
    """Settlement cycle for NSE/BSE equity delivery.

    T+2 before 2023-01-27 and T+1 from then; ``as_of=None`` is the cycle in force today.
    """
    iso = None if as_of is None else to_iso_date(as_of)
    if _native_nse_equity_settlement_days is not None:
        return _native_nse_equity_settlement_days(iso)
    if iso is not None and date.fromisoformat(iso) < _FALLBACK_T_PLUS_1_FROM:
        return 2
    return 1


def settlement_days_for(
    exchange: str, *, kind: str = "equity", as_of: date | datetime | str | None = None
) -> int:
    """Settlement cycle in days for ``exchange`` and instrument ``kind``, as of a date.

    ``exchange`` is a case-insensitive exchange code: Indian venues (NSE, BSE) follow the
    Rust market pack schedule (T+2 before 2023-01-27, T+1 from then; today's cycle when
    ``as_of`` is None), every other venue reports T+1. ``kind`` is one of
    :data:`INSTRUMENT_KINDS`; the India pack models a single delivery cycle per venue, so
    it does not vary by kind yet.

    Raises:
        ValueError: if ``kind`` is not a known instrument kind or ``as_of`` is malformed.
    """
    normalized = kind.strip().lower()
    if normalized not in INSTRUMENT_KINDS:
        raise ValueError(
            f"unknown instrument kind {kind!r}; expected one of {sorted(INSTRUMENT_KINDS)}"
        )
    if exchange.strip().upper() in INDIA_EXCHANGES:
        return nse_equity_settlement_days(as_of)
    return _DEFAULT_SETTLEMENT_DAYS


def resolve_settlement_days(
    exchange: str | None,
    as_of: date | None = None,
    cli_value: int | None = None,
    cfg_value: Any = None,
) -> tuple[int, str]:
    """Return (settlement_days, source) where source in {'cli','config','market'}.

    Precedence: cli_value (not None) > cfg_value (not None/truthy as used) > market default.
    Mirrors examples: cli overrides config overrides settlement_days_for(exchange).
    """
    if cli_value is not None:
        return int(cli_value), "cli"
    # config may be 0 or int; treat None/empty as not set
    if cfg_value is not None and cfg_value != "":
        try:
            days = int(cfg_value)
            return days, "config"
        except (TypeError, ValueError):
            pass
    # fallback to market
    exch = exchange or "NSE"
    src = f"engine:settlement_days_for({exch}, as_of={as_of})" if as_of is not None else "market"
    try:
        days = settlement_days_for(exch, as_of=as_of)
    except (TypeError, ValueError):
        try:
            days = settlement_days_for(exch)
        except (TypeError, ValueError):
            return 1, src
    return int(days), src
