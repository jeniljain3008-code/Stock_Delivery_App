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
def run_explosion_backtest(
    raw: pd.DataFrame,
    holding_periods = [ 5, 10, 15, 20, ],
) -> dict:

    analytics = compute_delivery_analytics(raw)
    stock_lookup = {
        symbol: group.sort_values("Date")
        for symbol, group
        in analytics.groupby("Symbol")
    }

    categories = [
        "EXPLODED",
        "READY_TO_EXPLODE",
        "PREPARING_TO_EXPLODE",
    ]

    results = {}

    for category in categories:

        trades = []
        candidates = analytics[
            analytics["ExplosionCategory"] == category
        ].copy()
        print(f"{category}: "f"{len(candidates)} candidates")
        candidates = candidates.sort_values(
            ["Symbol", "Date"]
        )

        for _, row in candidates.iterrows():

            symbol = row["Symbol"]

            scan_date = row["Date"]

            scanner_high = float(
                row["High"]
            )

            stock = stock_lookup[
                symbol
            ]

            future = stock[
                stock["Date"] > scan_date
            ].copy()

            if future.empty:
                continue

            breakout = future[
                future["High"] > scanner_high
            ]

            if breakout.empty:
                continue

            breakout_row = breakout.iloc[0]

            entry_date = breakout_row["Date"]

            entry_price = scanner_high

            future_after_entry = stock[
                stock["Date"] >= entry_date
            ].reset_index(
                drop=True
            )

            '''if len(future_after_entry) <= holding_days:
                continue

            exit_row = future_after_entry.iloc[
                holding_days
            ]

            exit_price = float(
                exit_row["Close"]
            )

            return_pct = (
                (
                    exit_price
                    - entry_price
                )
                / entry_price
            ) * 100

            trades.append(
                {
                    "symbol": symbol,
                    "scan_date": str(
                        scan_date.date()
                    ),
                    "entry_date": str(
                        entry_date.date()
                    ),
                    "entry_price": round(
                        entry_price,
                        2,
                    ),
                    "exit_price": round(
                        exit_price,
                        2,
                    ),
                    "return_pct": round(
                        return_pct,
                        2,
                    ),
                }
            )'''

            trade = {
                "symbol": symbol,
                "scan_date": str(
                    scan_date.date()
                ),
                "entry_date": str(
                    entry_date.date()
                ),
                "entry_price": round(
                    entry_price,
                    2,
                ),
            }
    
            for holding_days in holding_periods:
    
                    if len(future_after_entry) <= holding_days:
                        continue
                
                    exit_row = future_after_entry.iloc[
                        holding_days
                    ]
                
                    exit_price = float(
                        exit_row["Close"]
                    )
                
                    return_pct = (
                        (
                            exit_price
                            - entry_price
                        )
                        / entry_price
                    ) * 100
                
                    trade[
                        f"return_{holding_days}d"
                    ] = round(
                        return_pct,
                        2,
                    )
                
            trades.append(trade)
    
            if len(trades) == 0:
    
                results[category] = {
                    "signals": 0,
                    "breakouts": 0,
                    "win_rate": 0,
                    "avg_return": 0,
                    "median_return": 0,
                    "max_gain": 0,
                    "max_loss": 0,
                    "trade_log": [],
                }
    
                continue
    
            '''returns = np.array(
                [
                    t["return_pct"]
                    for t in trades
                ]
            )
    
            results[category] = {
                "signals": int(
                    len(candidates)
                ),
                "breakouts": int(
                    len(trades)
                ),
                "win_rate": round(
                    float(
                        (
                            returns > 0
                        ).mean()
                        * 100
                    ),
                    2,
                ),
                "avg_return": round(
                    float(
                        returns.mean()
                    ),
                    2,
                ),
                "median_return": round(
                    float(
                        np.median(
                            returns
                        )
                    ),
                    2,
                ),
                "max_gain": round(
                    float(
                        returns.max()
                    ),
                    2,
                ),
                "max_loss": round(
                    float(
                        returns.min()
                    ),
                    2,
                ),
                "trade_log": trades[:100],
            }'''
    
    
            performance = {}
    
            for holding_days in holding_periods:
            
                returns = np.array(
                    [
                        trade[
                            f"return_{holding_days}d"
                        ]
                        for trade in trades
                        if f"return_{holding_days}d"
                        in trade
                    ]
                )
            
                if len(returns) == 0:
            
                    performance[
                        f"{holding_days}d"
                    ] = {
                        "win_rate": 0,
                        "avg_return": 0,
                        "median_return": 0,
                        "max_gain": 0,
                        "max_loss": 0,
                    }
            
                    continue
            
                performance[
                    f"{holding_days}d"
                ] = {
                    "win_rate": round(
                        float(
                            (returns > 0).mean()
                            * 100
                        ),
                        2,
                    ),
                    "avg_return": round(
                        float(
                            returns.mean()
                        ),
                        2,
                    ),
                    "median_return": round(
                        float(
                            np.median(
                                returns
                            )
                        ),
                        2,
                    ),
                    "max_gain": round(
                        float(
                            returns.max()
                        ),
                        2,
                    ),
                    "max_loss": round(
                        float(
                            returns.min()
                        ),
                        2,
                    ),
                }
            
            results[category] = {
                "signals": int(
                    len(candidates)
                ),
                "breakouts": int(
                    len(trades)
                ),
                "performance": performance,
                "trade_log": trades[:100],
            }

    return results
