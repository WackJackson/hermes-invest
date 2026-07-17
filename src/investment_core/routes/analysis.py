from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from investment_core.dependencies import get_storage
from investment_core.models import DailyAnalysisResponse, OverviewRequest, PortfolioOverview
from investment_core.services.analysis import build_daily_analysis, build_portfolio_overview
from investment_core.storage import Storage

router = APIRouter(prefix="/api/v1", tags=["analysis"])


@router.post("/portfolio/overview")
def portfolio_overview(
    request: OverviewRequest,
    storage: Storage = Depends(get_storage),
) -> PortfolioOverview:
    holdings = storage.list_holdings()
    if not holdings:
        raise HTTPException(status_code=400, detail="No holdings imported yet")
    return build_portfolio_overview(holdings, request)


@router.post("/analysis/daily")
def daily_analysis(
    request: OverviewRequest,
    storage: Storage = Depends(get_storage),
) -> DailyAnalysisResponse:
    holdings = storage.list_holdings()
    if not holdings:
        raise HTTPException(status_code=400, detail="No holdings imported yet")
    profile = storage.get_rule_profile()
    return build_daily_analysis(holdings, request, profile)
