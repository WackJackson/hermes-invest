from investment_core.models import HoldingRecord, OverviewRequest, RuleProfile
from investment_core.mcp_payloads import (
    build_daily_analysis_payload,
    build_hermes_context_payload,
    build_portfolio_overview_payload,
    build_rule_profile_payload,
)
from investment_core.storage import Storage


def _seed_storage(tmp_path):
    storage = Storage(tmp_path / "mcp.db")
    storage.replace_holdings(
        [
            HoldingRecord(
                symbol="600519",
                market="CN",
                name="贵州茅台",
                quantity=10,
                avg_cost=1500,
                currency="CNY",
                account="long-term",
                open_date="2020-01-01",
            ),
            HoldingRecord(
                symbol="AAPL",
                market="US",
                name="Apple",
                quantity=20,
                avg_cost=180,
                currency="USD",
                account="long-term",
                open_date="2022-03-10",
            ),
        ]
    )
    return storage


def test_build_portfolio_overview_payload(tmp_path):
    storage = _seed_storage(tmp_path)

    payload = build_portfolio_overview_payload(
        storage,
        OverviewRequest(
            latest_prices={"600519": 1700, "AAPL": 210},
            fx_rates_to_cny={"CNY": 1.0, "USD": 7.2},
        ),
    )

    assert payload["position_count"] == 2
    assert payload["missing_prices"] == []


def test_build_daily_analysis_and_hermes_payloads(tmp_path):
    storage = _seed_storage(tmp_path)
    storage.save_rule_profile(
        RuleProfile(
            focus_metrics=["roe"],
            forbidden_traits=["high-debt"],
            target_holding_years=5,
            max_single_position_pct=60,
            max_drawdown_review_pct=12,
            alert_return_pct=25,
            daily_sections=["overview"],
            weekly_sections=["allocation"],
        )
    )
    request = OverviewRequest(
        latest_prices={"600519": 1700, "AAPL": 210},
        fx_rates_to_cny={"CNY": 1.0, "USD": 7.2},
    )

    analysis = build_daily_analysis_payload(storage, request)
    hermes = build_hermes_context_payload(storage, "今天看点什么", request)

    assert analysis["overview"]["position_count"] == 2
    assert hermes["question"] == "今天看点什么"
    assert "reply_outline" in hermes


def test_build_rule_profile_payload(tmp_path):
    storage = _seed_storage(tmp_path)

    updated = build_rule_profile_payload(
        storage,
        RuleProfile(
            focus_metrics=["fcf"],
            forbidden_traits=["serial-dilution"],
            target_holding_years=3,
            max_single_position_pct=35,
            max_drawdown_review_pct=10,
            alert_return_pct=20,
            daily_sections=["overview", "risk"],
            weekly_sections=["allocation", "watchlist"],
        ),
    )

    assert updated["focus_metrics"] == ["fcf"]
