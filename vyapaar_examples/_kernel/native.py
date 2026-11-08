"""In-repo stand-in for the compiled kernel extension attributes.

Mirrored kernel code (``_kernel/*``) reads version constants and the currency
table from the compiled extension of the owning engine (there, ``honba._native``).
The vyapaar wheel does not expose these yet, so the values are pinned here from
the owning repo's constants until the owning surface ships.

Owner/gap: ``vyapaar-ffi`` (kernel constants + currency table). Cited as gap
``0006-vyapaar-wheel-kernel-domain-surface``; delete this module together with
the mirrored kernel once the wheel provides the same public surface.
"""

from __future__ import annotations

from typing import Any

SCHEMA_VERSION = 8
"""Wire-contract version of the mirrored kernel events (kernel lib.rs)."""

API_VERSION = "v1"

STRATEGY_API_VERSION = "1.0.0"
"""Strategy-contract version pinned from ``honba-tamashii-py`` (manifest.rs)."""

_CURRENCY_MINOR_UNITS: dict[str, tuple[int, str, str]] = {
    "INR": (2, "paisa", "paise"),
    "USD": (2, "cent", "cents"),
    "EUR": (2, "euro_cent", "euro_cents"),
    "GBP": (2, "penny", "pence"),
}


def native_attr(name: str) -> Any:
    """Kernel extension attribute by name (version constants, currency table)."""
    if name == "SCHEMA_VERSION":
        return SCHEMA_VERSION
    if name == "API_VERSION":
        return API_VERSION
    if name == "STRATEGY_API_VERSION":
        return STRATEGY_API_VERSION
    if name == "currency_minor_units":
        return lambda: dict(_CURRENCY_MINOR_UNITS)
    raise AttributeError(f"no mirrored kernel attribute: {name!r}")
