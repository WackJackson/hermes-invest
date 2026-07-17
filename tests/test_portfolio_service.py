from investment_core.models import HoldingRecord, OverviewRequest
from investment_core.services.analysis import build_portfolio_overview


def test_build_portfolio_overview_supports_a_hk_us_markets():
    holdings = [
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
            symbol="00700",
            market="HK",
            name="腾讯控股",
            quantity=100,
            avg_cost=300,
            currency="HKD",
            account="long-term",
            open_date="2021-06-01",
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

    overview = build_portfolio_overview(
        holdings,
        OverviewRequest(
            latest_prices={"600519": 1700, "00700": 420, "AAPL": 210},
            fx_rates_to_cny={"CNY": 1.0, "HKD": 0.92, "USD": 7.2},
        ),
    )

    assert overview.position_count == 3
    assert overview.missing_prices == []
    assert overview.cny_equivalent_value > 0
    assert {item.market for item in overview.market_breakdown} == {"CN", "HK", "US"}
    assert round(sum(item.weight_pct for item in overview.positions), 2) == 100.0
