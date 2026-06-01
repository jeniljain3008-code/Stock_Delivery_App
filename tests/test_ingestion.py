import pytest

pd = pytest.importorskip("pandas")

from ingestion.validators import validate_delivery_frame


def test_validate_delivery_frame_accepts_required_schema():
    df = pd.DataFrame(
        [
            {
                "Date": "2026-01-01",
                "Symbol": "bel",
                "Open": 1,
                "High": 2,
                "Low": 1,
                "Close": 2,
                "Volume": 100,
                "DeliveryQty": 80,
                "DeliveryPercent": 80,
            }
        ]
    )
    clean = validate_delivery_frame(df)
    assert clean.iloc[0]["Symbol"] == "BEL"


def test_validate_delivery_frame_rejects_missing_column():
    with pytest.raises(ValueError):
        validate_delivery_frame(pd.DataFrame([{"Symbol": "BEL"}]))
