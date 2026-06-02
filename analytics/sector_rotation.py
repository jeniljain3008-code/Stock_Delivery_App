import pandas as pd


def compute_sector_rotation(df: pd.DataFrame) -> pd.DataFrame:
    latest = df.sort_values("Date").groupby("Symbol").tail(1).copy()
    if "Sector" not in latest.columns:
        latest["Sector"] = "Unclassified"
    grouped = (
        latest.groupby("Sector")
        .agg(
            average_delivery_increase=("Surge1M", "mean"),
            average_relative_strength=("AccumulationScore", "mean"),
            stock_count=("Symbol", "nunique"),
        )
        .reset_index()
    )
    grouped["leadership_index"] = (
        grouped["average_delivery_increase"] * 40 + grouped["average_relative_strength"] * 0.6
    )
    return grouped.sort_values("leadership_index", ascending=False)
