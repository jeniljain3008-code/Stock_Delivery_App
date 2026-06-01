import numpy as np
import pandas as pd

from analytics.delivery_engine import compute_delivery_analytics


def run_backtest(
    raw: pd.DataFrame, strategy: str, start_date, end_date, min_score: float = 70
) -> dict:
    df = compute_delivery_analytics(raw)
    df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]
    trades = []
    for symbol, stock in df.groupby("Symbol"):
        stock = stock.sort_values("Date").reset_index(drop=True)
        entries = stock.index[stock["AccumulationScore"] >= min_score].tolist()
        for idx in entries[:3]:
            exit_idx = min(idx + 20, len(stock) - 1)
            if exit_idx <= idx:
                continue
            entry = float(stock.loc[idx, "Close"])
            exit_price = float(stock.loc[exit_idx, "Close"])
            ret = (exit_price - entry) / entry
            trades.append(
                {
                    "symbol": symbol,
                    "entry_date": str(stock.loc[idx, "Date"].date()),
                    "exit_date": str(stock.loc[exit_idx, "Date"].date()),
                    "return": round(ret, 4),
                }
            )
    returns = np.array([t["return"] for t in trades]) if trades else np.array([0.0])
    wins = returns[returns > 0]
    losses = returns[returns < 0]
    return {
        "win_rate": round(float((returns > 0).mean() * 100), 2),
        "cagr": round(float((1 + returns.mean()) ** 12 - 1) * 100, 2),
        "profit_factor": round(float(wins.sum() / abs(losses.sum())) if losses.size else 99.0, 2),
        "max_drawdown": round(float(min(0, returns.min()) * 100), 2),
        "sharpe_ratio": round(float((returns.mean() / (returns.std() or 1)) * np.sqrt(12)), 2),
        "trade_log": trades[:100],
    }
