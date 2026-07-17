from investment_core.services.importer import parse_holdings_upload


CSV_CONTENT = b"symbol,market,name,quantity,avg_cost,currency,account,open_date\n600519,CN,\xe8\xb4\xb5\xe5\xb7\x9e\xe8\x8c\x85\xe5\x8f\xb0,5,1550,CNY,long-term,2020-01-01\nAAPL,US,Apple,10,180,USD,broker-a,2022-03-10\n"


def test_parse_holdings_upload_supports_csv():
    records = parse_holdings_upload("holdings.csv", CSV_CONTENT)

    assert len(records) == 2
    assert records[0].symbol == "600519"
    assert records[1].currency == "USD"
