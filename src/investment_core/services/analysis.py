from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from investment_core.models import (
    DailyAnalysisResponse,
    HoldingPosition,
    HoldingRecord,
    MarketWeight,
    OverviewRequest,
    PortfolioOverview,
    RecommendationItem,
    RuleProfile,
)


def build_portfolio_overview(
    holdings: list[HoldingRecord],
    request: OverviewRequest,
) -> PortfolioOverview:
    missing_prices: list[str] = []
    positions: list[HoldingPosition] = []
    market_values: dict[str, float] = defaultdict(float)
    total_value = 0.0
    total_cost = 0.0

    for holding in holdings:
        latest_price = request.latest_prices.get(holding.symbol)
        if latest_price is None:
            missing_prices.append(holding.symbol)
            latest_price = holding.avg_cost
        fx_rate = request.fx_rates_to_cny.get(holding.currency.upper(), 1.0)
        market_value = holding.quantity * latest_price * fx_rate
        cost_value = holding.quantity * holding.avg_cost * fx_rate
        profit_value = market_value - cost_value
        total_value += market_value
        total_cost += cost_value
        market_values[holding.market] += market_value
        positions.append(
            HoldingPosition(
                symbol=holding.symbol,
                market=holding.market,
                name=holding.name,
                quantity=holding.quantity,
                avg_cost=holding.avg_cost,
                latest_price=latest_price,
                currency=holding.currency,
                market_value=round(market_value, 2),
                cost_value=round(cost_value, 2),
                profit_value=round(profit_value, 2),
                return_pct=round((profit_value / cost_value) * 100, 2) if cost_value else 0.0,
                weight_pct=0.0,
            )
        )

    for position in positions:
        position.weight_pct = round((position.market_value / total_value) * 100, 2) if total_value else 0.0

    market_breakdown = [
        MarketWeight(
            market=market,
            value=round(value, 2),
            weight_pct=round((value / total_value) * 100, 2) if total_value else 0.0,
        )
        for market, value in sorted(market_values.items())
    ]

    total_profit = total_value - total_cost
    return PortfolioOverview(
        generated_at=datetime.now(timezone.utc),
        position_count=len(holdings),
        cny_equivalent_value=round(total_value, 2),
        cny_equivalent_cost=round(total_cost, 2),
        cny_equivalent_profit=round(total_profit, 2),
        total_return_pct=round((total_profit / total_cost) * 100, 2) if total_cost else 0.0,
        missing_prices=missing_prices,
        positions=sorted(positions, key=lambda item: item.weight_pct, reverse=True),
        market_breakdown=market_breakdown,
    )


def build_recommendations(overview: PortfolioOverview, profile: RuleProfile) -> list[RecommendationItem]:
    recommendations: list[RecommendationItem] = []
    for position in overview.positions:
        decision = "continue_holding"
        reasons = []
        if position.weight_pct > profile.max_single_position_pct:
            decision = "focus_now"
            reasons.append(f"single position weight {position.weight_pct}% exceeds {profile.max_single_position_pct}%")
        elif position.return_pct <= -profile.max_drawdown_review_pct:
            decision = "review_needed"
            reasons.append(f"drawdown {position.return_pct}% breached review threshold")
        elif position.return_pct >= profile.alert_return_pct:
            reasons.append(f"return {position.return_pct}% reached alert threshold")

        if not reasons:
            reasons.append("position is within current long-term value investing guardrails")

        recommendations.append(
            RecommendationItem(
                symbol=position.symbol,
                market=position.market,
                decision=decision,
                reason="; ".join(reasons),
            )
        )
    return recommendations


def build_daily_analysis(
    holdings: list[HoldingRecord],
    request: OverviewRequest,
    profile: RuleProfile,
) -> DailyAnalysisResponse:
    overview = build_portfolio_overview(holdings, request)
    recommendations = build_recommendations(overview, profile)
    report_outline = [
        "组合总览：仓位、收益、市场分布",
        "重点持仓：超配、回撤、收益触发项",
        "价值投资视角：是否继续持有或需要复盘",
        "后续动作：日报、周报、异动推送候选",
    ]
    return DailyAnalysisResponse(
        generated_at=datetime.now(timezone.utc),
        overview=overview,
        recommendations=recommendations,
        report_outline=report_outline,
    )
