import pandas as pd


def compute_relative_strength(
    df: pd.DataFrame, benchmark_symbol: str = "NIFTY", lookback: int = 63
) -> dict[str, float]:
    data = df.sort_values(["Symbol", "Date"]).copy()
    returns = data.groupby("Symbol")["Close"].apply(
        lambda s: s.pct_change(lookback).iloc[-1] if len(s) > 1 else 0
    )
    benchmark = returns.get(benchmark_symbol, returns.median())
    ranked = ((returns - benchmark).rank(pct=True) * 100).fillna(50)
    return {symbol: round(float(score), 2) for symbol, score in ranked.items()}
