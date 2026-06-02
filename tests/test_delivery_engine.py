import pytest

pd = pytest.importorskip("pandas")

from analytics.delivery_engine import compute_delivery_analytics, scan_gold_stocks


def test_delivery_score_prioritizes_surge():
    df = pd.read_csv("sample_data/nse_delivery_sample.csv", parse_dates=["Date"])
    analytics = compute_delivery_analytics(df)
    latest = analytics.sort_values("Date").groupby("Symbol").tail(1)
    assert "AccumulationScore" in latest.columns
    assert latest["AccumulationScore"].between(0, 100).all()


def test_gold_scanner_shape():
    df = pd.read_csv("sample_data/nse_delivery_sample.csv", parse_dates=["Date"])
    result = scan_gold_stocks(df)
    expected_columns = {
        "symbol",
        "price",
        "delivery_surge",
        "accumulation_score",
        "risk_rating",
        "potential_upside",
    }
    assert expected_columns.issubset(result.columns)
