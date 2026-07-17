from fastapi.testclient import TestClient

from investment_core.main import create_app


CSV_CONTENT = b"symbol,market,name,quantity,avg_cost,currency,account,open_date\n600519,CN,\xe8\xb4\xb5\xe5\xb7\x9e\xe8\x8c\x85\xe5\x8f\xb0,10,1500,CNY,long-term,2020-01-01\n00700,HK,\xe8\x85\xbe\xe8\xae\xaf\xe6\x8e\xa7\xe8\x82\xa1,100,300,HKD,long-term,2021-06-01\nAAPL,US,Apple,20,180,USD,long-term,2022-03-10\n"


def test_import_overview_and_analysis_flow(tmp_path):
    app = create_app(db_path=tmp_path / "test.db")
    client = TestClient(app)

    health_response = client.get("/healthz")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "ok"

    import_response = client.post(
        "/api/v1/holdings/import",
        files={"file": ("holdings.csv", CSV_CONTENT, "text/csv")},
    )
    assert import_response.status_code == 200
    assert import_response.json()["imported"] == 3

    overview_response = client.post(
        "/api/v1/portfolio/overview",
        json={
            "latest_prices": {"600519": 1700, "00700": 420, "AAPL": 210},
            "fx_rates_to_cny": {"CNY": 1.0, "HKD": 0.92, "USD": 7.2},
        },
    )
    assert overview_response.status_code == 200
    overview_payload = overview_response.json()
    assert overview_payload["position_count"] == 3
    assert overview_payload["missing_prices"] == []

    rules_response = client.put(
        "/api/v1/rules/profile",
        json={
            "focus_metrics": ["roe", "free_cash_flow"],
            "forbidden_traits": ["high-debt", "serial-dilution"],
            "target_holding_years": 5,
            "max_single_position_pct": 35,
            "max_drawdown_review_pct": 12,
            "alert_return_pct": 25,
            "daily_sections": ["overview", "risk", "news"],
            "weekly_sections": ["allocation", "valuation", "watchlist"],
        },
    )
    assert rules_response.status_code == 200

    analysis_response = client.post(
        "/api/v1/analysis/daily",
        json={
            "latest_prices": {"600519": 1700, "00700": 420, "AAPL": 210},
            "fx_rates_to_cny": {"CNY": 1.0, "HKD": 0.92, "USD": 7.2},
        },
    )
    assert analysis_response.status_code == 200
    analysis_payload = analysis_response.json()
    assert analysis_payload["overview"]["position_count"] == 3
    assert len(analysis_payload["recommendations"]) == 3
    assert {item["decision"] for item in analysis_payload["recommendations"]} <= {
        "continue_holding",
        "review_needed",
        "focus_now",
    }

    hermes_response = client.post(
        "/api/v1/hermes/context",
        json={
            "question": "今天组合里最需要关注什么？",
            "latest_prices": {"600519": 1700, "00700": 420, "AAPL": 210},
            "fx_rates_to_cny": {"CNY": 1.0, "HKD": 0.92, "USD": 7.2},
        },
    )
    assert hermes_response.status_code == 200
    hermes_payload = hermes_response.json()
    assert hermes_payload["question"] == "今天组合里最需要关注什么？"
    assert "reply_outline" in hermes_payload
