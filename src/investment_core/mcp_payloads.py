from __future__ import annotations

from investment_core.models import OverviewRequest, RuleProfile
from investment_core.services.analysis import build_daily_analysis, build_portfolio_overview
from investment_core.storage import Storage


class EmptyHoldingsError(RuntimeError):
    pass


def _require_holdings(storage: Storage):
    holdings = storage.list_holdings()
    if not holdings:
        raise EmptyHoldingsError("No holdings imported yet")
    return holdings


def build_portfolio_overview_payload(storage: Storage, request: OverviewRequest) -> dict:
    holdings = _require_holdings(storage)
    return build_portfolio_overview(holdings, request).model_dump(mode="json")


def build_daily_analysis_payload(storage: Storage, request: OverviewRequest) -> dict:
    holdings = _require_holdings(storage)
    profile = storage.get_rule_profile()
    return build_daily_analysis(holdings, request, profile).model_dump(mode="json")


def build_hermes_context_payload(storage: Storage, question: str, request: OverviewRequest) -> dict:
    holdings = _require_holdings(storage)
    profile = storage.get_rule_profile()
    analysis = build_daily_analysis(holdings, request, profile)
    return {
        "question": question,
        "overview": analysis.overview.model_dump(mode="json"),
        "recommendations": [item.model_dump(mode="json") for item in analysis.recommendations],
        "reply_outline": [
            "先总结组合整体仓位与收益情况",
            "再指出最该关注的持仓与理由",
            "最后给出价值投资视角下的后续动作",
        ],
        "system_hint": "Hermes must use these structured facts and should not invent holdings or returns.",
    }


def build_rule_profile_payload(storage: Storage, profile: RuleProfile) -> dict:
    return storage.save_rule_profile(profile).model_dump(mode="json")
