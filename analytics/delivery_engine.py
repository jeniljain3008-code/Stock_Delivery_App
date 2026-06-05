import numpy as np
import pandas as pd

WINDOWS = {
    "DeliveryMA5": 5,
    "DeliveryMA10": 10,
    "DeliveryMA30": 30,
    "DeliveryMA60": 60,
    "DeliveryMA90": 90,
}


def _score_clip(series: pd.Series, low: float = 0, high: float = 100) -> pd.Series:
    return series.clip(lower=low, upper=high).fillna(0)


def compute_delivery_analytics(raw: pd.DataFrame) -> pd.DataFrame:
    """Compute delivery-first analytics for smart-money accumulation detection.

    The model deliberately makes delivery quantity the leading signal and only uses price,
    volume, and trend as confirmation layers for 1–8 week swing candidates.
    """
    df = raw.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(["Symbol", "Date"])
    groups = df.groupby("Symbol", group_keys=False)

    for name, window in WINDOWS.items():
        df[name] = groups["DeliveryQty"].transform(
            lambda s, rolling_window=window: s.rolling(rolling_window, min_periods=1).mean()
        )

    df["DeliveryMA126"] = groups["DeliveryQty"].transform(
        lambda s: s.rolling(126, min_periods=1).mean()
    )
    df["Surge1M"] = df["DeliveryQty"] / df["DeliveryMA30"].replace(0, np.nan)
    df["Surge2M"] = df["DeliveryQty"] / df["DeliveryMA60"].replace(0, np.nan)
    df["Surge3M"] = df["DeliveryQty"] / df["DeliveryMA90"].replace(0, np.nan)
    df["Surge6M"] = df["DeliveryQty"] / df["DeliveryMA126"].replace(0, np.nan)
    df["Surge5D"] = (
            df["DeliveryQty"]
            / df["DeliveryMA5"].replace(
                0,
                np.nan,
            )
        )

    df["Surge10D"] = (
            df["DeliveryQty"]
            / df["DeliveryMA10"].replace(
                0,
                np.nan,
            )
        )

    df["Surge30D"] = (
            df["DeliveryQty"]
            / df["DeliveryMA30"].replace(
                0,
                np.nan,
            )
        )
    
    df["ExplosionScore"] = (
            (df["Surge5D"] * 0.50)
            + (df["Surge10D"] * 0.30)
            + (df["Surge30D"] * 0.20)
        )
    df["DMA20"] = groups["Close"].transform(lambda s: s.rolling(20, min_periods=1).mean())
    df["DMA50"] = groups["Close"].transform(lambda s: s.rolling(50, min_periods=1).mean())
    df["DMA200"] = groups["Close"].transform(lambda s: s.rolling(200, min_periods=1).mean())
    df["VolumeMA20"] = groups["Volume"].transform(lambda s: s.rolling(20, min_periods=1).mean())
    df["High20"] = groups["High"].transform(lambda s: s.rolling(20, min_periods=1).max())
    df["Return20D"] = groups["Close"].pct_change(20).fillna(0)

    delivery_strength = _score_clip(
        ((df["Surge1M"] - 1) * 35) + ((df["Surge3M"] - 1) * 25) + (df["DeliveryPercent"] - 35)
    )
    price_strength = _score_clip(
        (df["Close"] > df["DMA20"]).astype(int) * 35
        + (df["Close"] > df["DMA50"]).astype(int) * 40
        + df["Return20D"] * 125
    )
    volume_strength = _score_clip(
        (df["Volume"] / df["VolumeMA20"].replace(0, np.nan) - 1) * 55 + 45
    )
    trend_strength = _score_clip(
        (df["DMA20"] > df["DMA50"]).astype(int) * 40
        + (df["DMA50"] > df["DMA200"]).astype(int) * 35
        + (df["Close"] / df["High20"].replace(0, np.nan)) * 25
    )

    df["AccumulationScore"] = _score_clip(
        delivery_strength * 0.40
        + price_strength * 0.20
        + volume_strength * 0.20
        + trend_strength * 0.20
    )

    df["ExplosionCategory"] = np.select(
            [
                (
                    (df["Surge5D"] > 1.25)
                    &
                    (df["Surge10D"] > 1.10)
                    &
                    (df["Surge30D"] > 1.00)
                    &
                    (df["AccumulationScore"] >= 60)
                ),
        
                (
                    (df["Surge5D"] > df["Surge10D"])
                    &
                    (df["Surge5D"] < df["Surge30D"])
                    &
                    (df["AccumulationScore"] >= 60)
                ),
        
                (
                    (df["Surge5D"] < df["Surge10D"])
                    &
                    (df["Surge10D"] > df["Surge30D"])
                    &
                    (df["AccumulationScore"] >= 60)
                ),
            ],
            [
                "EXPLODED",
                "READY_TO_EXPLODE",
                "PREPARING_TO_EXPLODE",
            ],
            default="OTHER",
        )    
    df["BreakoutScore"] = _score_clip(
        (df["Close"] / df["High20"].replace(0, np.nan)) * 40
        + (df["Surge1M"] * 20)
        + (df["Volume"] / df["VolumeMA20"].replace(0, np.nan)) * 20
        + (df["Close"] > df["DMA50"]).astype(int) * 20
    )
    df["InstitutionalConfidence"] = _score_clip(
        df["AccumulationScore"] * 0.55
        + df["BreakoutScore"] * 0.25
        + (df["DeliveryMA5"] > df["DeliveryMA30"]).astype(int) * 20
    )
    df["PotentialUpside"] = np.select(
        [
            df["AccumulationScore"] >= 85,
            df["AccumulationScore"] >= 70,
            df["AccumulationScore"] >= 55,
        ],
        [20, 12, 7],
        default=3,
    )
    df["RiskRating"] = np.select(
        [df["Close"] < df["DMA50"], df["Surge1M"] > 3], ["High", "Medium"], default="Low"
    )
    df["SwingSignal"] = np.select(
        [df["AccumulationScore"] >= 75, df["AccumulationScore"] >= 55],
        ["BUY", "WATCH"],
        default="SELL",
    )
    df["AccumulationLabel"] = pd.cut(
        df["AccumulationScore"],
        bins=[-1, 25, 45, 60, 75, 100],
        labels=["Distribution", "Weak", "Neutral", "Moderate Accumulation", "Strong Accumulation"],
    ).astype(str)
    return df.replace([np.inf, -np.inf], np.nan).fillna(0)


def scan_gold_stocks(raw: pd.DataFrame) -> pd.DataFrame:
    df = compute_delivery_analytics(raw)
    latest = df.sort_values("Date").groupby("Symbol").tail(1).copy()
    mask = (
        (latest["DeliveryQty"] > 2 * latest["DeliveryMA30"])
        & (latest["DeliveryQty"] > 1.5 * latest["DeliveryMA90"])
        & (latest["Close"] > latest["DMA20"])
        & (latest["Close"] > latest["DMA50"])
        & (latest["Volume"] > latest["VolumeMA20"])
    )
    out = latest.loc[mask].sort_values("AccumulationScore", ascending=False)
    return out.assign(
        price=out["Close"].round(2),
        delivery_surge=out["Surge1M"].round(2),
        accumulation_score=out["AccumulationScore"].round(2),
        risk_rating=out["RiskRating"],
        potential_upside=out["PotentialUpside"],
    )[
        [
            "Symbol",
            "price",
            "delivery_surge",
            "accumulation_score",
            "risk_rating",
            "potential_upside",
        ]
    ].rename(columns={"Symbol": "symbol"})
