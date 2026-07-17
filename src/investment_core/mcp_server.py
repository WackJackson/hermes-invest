from __future__ import annotations

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from investment_core.models import OverviewRequest, RuleProfile
from investment_core.mcp_payloads import (
    EmptyHoldingsError,
    build_daily_analysis_payload,
    build_hermes_context_payload,
    build_portfolio_overview_payload,
    build_rule_profile_payload,
)
from investment_core.services.importer import parse_holdings_upload
from investment_core.storage import Storage

mcp = FastMCP("invest-core")
_storage = Storage(Path(os.getenv("INVEST_DB_PATH", "data/investment_core.db")))


def _overview_request(latest_prices: dict[str, float], fx_rates_to_cny: dict[str, float] | None) -> OverviewRequest:
    return OverviewRequest(
        latest_prices=latest_prices,
        fx_rates_to_cny=fx_rates_to_cny or {"CNY": 1.0, "HKD": 0.92, "USD": 7.2},
    )


@mcp.tool()
def list_holdings() -> list[dict]:
    return [record.model_dump(mode="json") for record in _storage.list_holdings()]


@mcp.tool()
def portfolio_overview(
    latest_prices: dict[str, float],
    fx_rates_to_cny: dict[str, float] | None = None,
) -> dict:
    try:
        return build_portfolio_overview_payload(_storage, _overview_request(latest_prices, fx_rates_to_cny))
    except EmptyHoldingsError as exc:
        return {"error": str(exc)}


@mcp.tool()
def daily_analysis(
    latest_prices: dict[str, float],
    fx_rates_to_cny: dict[str, float] | None = None,
) -> dict:
    try:
        return build_daily_analysis_payload(_storage, _overview_request(latest_prices, fx_rates_to_cny))
    except EmptyHoldingsError as exc:
        return {"error": str(exc)}


@mcp.tool()
def hermes_context(
    question: str,
    latest_prices: dict[str, float],
    fx_rates_to_cny: dict[str, float] | None = None,
) -> dict:
    try:
        return build_hermes_context_payload(
            _storage,
            question,
            _overview_request(latest_prices, fx_rates_to_cny),
        )
    except EmptyHoldingsError as exc:
        return {"error": str(exc)}


@mcp.tool()
def update_rule_profile(
    focus_metrics: list[str],
    forbidden_traits: list[str],
    target_holding_years: int,
    max_single_position_pct: float,
    max_drawdown_review_pct: float,
    alert_return_pct: float,
    daily_sections: list[str],
    weekly_sections: list[str],
) -> dict:
    profile = RuleProfile(
        focus_metrics=focus_metrics,
        forbidden_traits=forbidden_traits,
        target_holding_years=target_holding_years,
        max_single_position_pct=max_single_position_pct,
        max_drawdown_review_pct=max_drawdown_review_pct,
        alert_return_pct=alert_return_pct,
        daily_sections=daily_sections,
        weekly_sections=weekly_sections,
    )
    return build_rule_profile_payload(_storage, profile)


@mcp.tool()
def import_holdings_csv(filename: str, csv_text: str) -> dict:
    records = parse_holdings_upload(filename, csv_text.encode("utf-8"))
    imported = _storage.replace_holdings(records)
    return {"imported": imported}


if __name__ == "__main__":
    mcp.run()
