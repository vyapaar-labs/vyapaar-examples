"""Compatibility helpers for the examples harness.

The ``vyapaar`` native wheel and the sibling SDK/data packages are optional at
runtime; pure-Python ``decimal.Decimal`` fallbacks keep every example
deterministic and offline-runnable.
"""

from __future__ import annotations

from decimal import Decimal

try:  # pragma: no cover - exercised only when the native wheel is absent
    from vyapaar import Decimal as VyapaarDecimal

    VYAAPAAR_AVAILABLE = True
except ImportError:  # pragma: no cover
    VyapaarDecimal = Decimal
    VYAAPAAR_AVAILABLE = False

D = Decimal
