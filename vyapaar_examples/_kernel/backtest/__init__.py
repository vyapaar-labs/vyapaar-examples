"""Backtest building blocks: simulated execution ports (``_kernel.backtest.simulated``)."""
# mirror: kernel-verbatim port (gap 0006)

from vyapaar_examples._kernel.backtest.impact import (
    MarketImpact,  # gap 0006: backtest simulator mirror
)
from vyapaar_examples._kernel.backtest.l2_sim import (  # gap 0006: backtest simulator mirror
    L2Execution,
    TopOfBook,
)
from vyapaar_examples._kernel.backtest.opening_auction import (
    OpeningAuction,  # gap 0006: backtest simulator mirror
)
from vyapaar_examples._kernel.backtest.simulated import (
    FillCostFn,
    FillModel,
    NextOpenExecution,
    SessionOpen,
    group_sessions,
    make_simulator,
    resolve_fill_costs,
    zero_costs,
)

__all__ = [
    "FillCostFn",
    "FillModel",
    "L2Execution",
    "MarketImpact",
    "NextOpenExecution",
    "OpeningAuction",
    "SessionOpen",
    "TopOfBook",
    "group_sessions",
    "make_simulator",
    "resolve_fill_costs",
    "zero_costs",
]
