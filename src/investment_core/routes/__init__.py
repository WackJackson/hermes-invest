from investment_core.routes.analysis import router as analysis_router
from investment_core.routes.hermes import router as hermes_router
from investment_core.routes.holdings import router as holdings_router
from investment_core.routes.rules import router as rules_router

__all__ = [
    "analysis_router",
    "hermes_router",
    "holdings_router",
    "rules_router",
]
