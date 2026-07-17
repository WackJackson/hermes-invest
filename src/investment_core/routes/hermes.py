from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from investment_core.dependencies import get_storage
from investment_core.models import HermesContextRequest, HermesContextResponse, OverviewRequest
from investment_core.services.analysis import build_daily_analysis
from investment_core.storage import Storage

router = APIRouter(prefix="/api/v1/hermes", tags=["hermes"])


@router.post("/context")
def build_context(
    request: HermesContextRequest,
    storage: Storage = Depends(get_storage),
) -> HermesContextResponse:
    holdings = storage.list_holdings()
    if not holdings:
        raise HTTPException(status_code=400, detail="No holdings imported yet")
    profile = storage.get_rule_profile()
    analysis = build_daily_analysis(
        holdings,
        OverviewRequest(
            latest_prices=request.latest_prices,
            fx_rates_to_cny=request.fx_rates_to_cny,
        ),
        profile,
    )
    return HermesContextResponse(
        question=request.question,
        overview=analysis.overview,
        recommendations=analysis.recommendations,
        reply_outline=[
            "先回答用户最关心的组合风险与重点持仓",
            "再补充价值投资视角下的继续持有/复盘建议",
            "最后给出日报或提醒触发建议",
        ],
        system_hint="Hermes should use this structured payload to generate Feishu-friendly replies instead of inventing portfolio facts.",
    )
