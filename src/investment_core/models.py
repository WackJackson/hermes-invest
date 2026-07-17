from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

MarketCode = Literal["CN", "HK", "US"]
DecisionCode = Literal["continue_holding", "review_needed", "focus_now"]


class HoldingRecord(BaseModel):
    symbol: str
    market: MarketCode
    name: str
    quantity: float
    avg_cost: float
    currency: str
    account: str
    open_date: str


class HoldingPosition(BaseModel):
    symbol: str
    market: MarketCode
    name: str
    quantity: float
    avg_cost: float
    latest_price: float
    currency: str
    market_value: float
    cost_value: float
    profit_value: float
    return_pct: float
    weight_pct: float


class MarketWeight(BaseModel):
    market: MarketCode
    value: float
    weight_pct: float


class OverviewRequest(BaseModel):
    latest_prices: dict[str, float] = Field(default_factory=dict)
    fx_rates_to_cny: dict[str, float] = Field(default_factory=lambda: {"CNY": 1.0, "HKD": 0.92, "USD": 7.2})


class PortfolioOverview(BaseModel):
    generated_at: datetime
    position_count: int
    cny_equivalent_value: float
    cny_equivalent_cost: float
    cny_equivalent_profit: float
    total_return_pct: float
    missing_prices: list[str]
    positions: list[HoldingPosition]
    market_breakdown: list[MarketWeight]


class RuleProfile(BaseModel):
    focus_metrics: list[str] = Field(default_factory=list)
    forbidden_traits: list[str] = Field(default_factory=list)
    target_holding_years: int = 3
    max_single_position_pct: float = 35
    max_drawdown_review_pct: float = 12
    alert_return_pct: float = 25
    daily_sections: list[str] = Field(default_factory=lambda: ["overview", "risk", "news"])
    weekly_sections: list[str] = Field(default_factory=lambda: ["allocation", "valuation", "watchlist"])


class RecommendationItem(BaseModel):
    symbol: str
    market: MarketCode
    decision: DecisionCode
    reason: str


class DailyAnalysisResponse(BaseModel):
    generated_at: datetime
    overview: PortfolioOverview
    recommendations: list[RecommendationItem]
    report_outline: list[str]


class HermesContextRequest(BaseModel):
    question: str
    latest_prices: dict[str, float] = Field(default_factory=dict)
    fx_rates_to_cny: dict[str, float] = Field(default_factory=lambda: {"CNY": 1.0, "HKD": 0.92, "USD": 7.2})


class HermesContextResponse(BaseModel):
    question: str
    overview: PortfolioOverview
    recommendations: list[RecommendationItem]
    reply_outline: list[str]
    system_hint: str
