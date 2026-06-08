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

def run_winner_vs_loser_study(
    raw: pd.DataFrame,
    lookahead_days: int = 20,
    winner_threshold: float = 15.0,
) -> dict:

    analytics = compute_delivery_analytics(raw)

    exploded = analytics[
        analytics["ExplosionCategory"] == "EXPLODED"
    ].copy()

    if exploded.empty:
        return {
            "error": "No exploded stocks found"
        }

    stock_lookup = {
        symbol: group.sort_values(
            "Date"
        ).reset_index(
            drop=True
        )
        for symbol, group
        in analytics.groupby(
            "Symbol"
        )
    }

    winners = []
    losers = []

    for _, row in exploded.iterrows():

        symbol = row["Symbol"]

        stock = stock_lookup.get(
            symbol
        )

        if stock is None:
            continue

        matching_idx = stock.index[
            stock["Date"] == row["Date"]
        ]

        if len(matching_idx) == 0:
            continue

        explosion_idx = matching_idx[0]

        if (
            explosion_idx
            + lookahead_days
            >= len(stock)
        ):
            continue

        entry_price = float(
            row["Close"]
        )

        future_price = float(
            stock.iloc[
                explosion_idx
                + lookahead_days
            ]["Close"]
        )

        future_return = (
            (
                future_price
                - entry_price
            )
            / entry_price
        ) * 100

        volume_ratio = (
            float(row["Volume"])
            / max(
                float(
                    row["VolumeMA20"]
                ),
                1,
            )
        )

        observation = {
            "AccumulationScore":
                float(
                    row["AccumulationScore"]
                ),

            "ExplosionScore":
                float(
                    row["ExplosionScore"]
                ),

            "BreakoutScore":
                float(
                    row["BreakoutScore"]
                ),

            "InstitutionalConfidence":
                float(
                    row[
                        "InstitutionalConfidence"
                    ]
                ),

            "Surge5D":
                float(
                    row["Surge5D"]
                ),

            "Surge10D":
                float(
                    row["Surge10D"]
                ),

            "Surge30D":
                float(
                    row["Surge30D"]
                ),

            "Surge1M":
                float(
                    row["Surge1M"]
                ),

            "DeliveryPercent":
                float(
                    row[
                        "DeliveryPercent"
                    ]
                ),

            "VolumeRatio":
                volume_ratio,

            "FutureReturn":
                future_return,
        }

        if future_return >= winner_threshold:

            winners.append(
                observation
            )

        elif future_return <= 0:

            losers.append(
                observation
            )

    winner_df = pd.DataFrame(
        winners
    )

    loser_df = pd.DataFrame(
        losers
    )

    if winner_df.empty:
        return {
            "error":
            "No winners found"
        }

    if loser_df.empty:
        return {
            "error":
            "No losers found"
        }

    metrics = [
        "AccumulationScore",
        "ExplosionScore",
        "BreakoutScore",
        "InstitutionalConfidence",
        "Surge5D",
        "Surge10D",
        "Surge30D",
        "Surge1M",
        "DeliveryPercent",
        "VolumeRatio",
    ]

    winner_stats = {}
    loser_stats = {}

    for metric in metrics:

        winner_stats[
            metric
        ] = round(
            float(
                winner_df[
                    metric
                ].mean()
            ),
            2,
        )

        loser_stats[
            metric
        ] = round(
            float(
                loser_df[
                    metric
                ].mean()
            ),
            2,
        )

    return {
        "winner_count":
            int(
                len(
                    winner_df
                )
            ),

        "loser_count":
            int(
                len(
                    loser_df
                )
            ),

        "winner_threshold":
            winner_threshold,

        "lookahead_days":
            lookahead_days,

        "winners":
            winner_stats,

        "losers":
            loser_stats,
    }
def run_pre_explosion_winner_study(
    raw: pd.DataFrame,
    winner_threshold: float = 15.0,
    lookahead_days: int = 20,
) -> dict:

    analytics = compute_delivery_analytics(raw)

    exploded = analytics[
        analytics["ExplosionCategory"] == "EXPLODED"
    ].copy()

    if exploded.empty:
        return {
            "error": "No exploded stocks found"
        }

    stock_lookup = {
        symbol: group.sort_values("Date").reset_index(drop=True)
        for symbol, group
        in analytics.groupby("Symbol")
    }

    winner_events = []

    for _, row in exploded.iterrows():

        symbol = row["Symbol"]

        stock = stock_lookup.get(symbol)

        if stock is None:
            continue

        matching_idx = stock.index[
            stock["Date"] == row["Date"]
        ]

        if len(matching_idx) == 0:
            continue

        explosion_idx = matching_idx[0]

        if explosion_idx + lookahead_days >= len(stock):
            continue

        entry_price = float(
            row["Close"]
        )

        future_price = float(
            stock.iloc[
                explosion_idx + lookahead_days
            ]["Close"]
        )

        future_return = (
            (
                future_price
                - entry_price
            )
            / entry_price
        ) * 100

        if future_return >= winner_threshold:

            winner_events.append(
                {
                    "symbol": symbol,
                    "explosion_date": row["Date"],
                    "future_return": future_return,
                }
            )

    if len(winner_events) == 0:

        return {
            "error":
            "No winner explosions found"
        }

    print(
        f"Winner explosions found: "
        f"{len(winner_events)}"
    )

    lookbacks = [
        20,
        15,
        10,
        5,
        0,
    ]

    results = {}

    for days_before in lookbacks:

        observations = []

        for winner in winner_events:

            symbol = winner["symbol"]

            explosion_date = winner[
                "explosion_date"
            ]

            stock = stock_lookup[
                symbol
            ]

            matching_idx = stock.index[
                stock["Date"] == explosion_date
            ]

            if len(matching_idx) == 0:
                continue

            explosion_idx = matching_idx[0]

            target_idx = (
                explosion_idx
                - days_before
            )

            if target_idx < 0:
                continue

            row = stock.iloc[
                target_idx
            ]

            observations.append(
                {
                    "AccumulationScore":
                        row["AccumulationScore"],

                    "ExplosionScore":
                        row["ExplosionScore"],

                    "Surge5D":
                        row["Surge5D"],

                    "Surge10D":
                        row["Surge10D"],

                    "Surge30D":
                        row["Surge30D"],

                    "Surge1M":
                        row["Surge1M"],

                    "BreakoutScore":
                        row["BreakoutScore"],

                    "InstitutionalConfidence":
                        row[
                            "InstitutionalConfidence"
                        ],
                }
            )

        study_df = pd.DataFrame(
            observations
        )

        if study_df.empty:

            results[
                f"{days_before}_days_before"
            ] = {
                "count": 0
            }

            continue

        results[
            f"{days_before}_days_before"
        ] = {
            "count":
                int(len(study_df)),

            "avg_accumulation":
                round(
                    float(
                        study_df[
                            "AccumulationScore"
                        ].mean()
                    ),
                    2,
                ),

            "avg_explosion_score":
                round(
                    float(
                        study_df[
                            "ExplosionScore"
                        ].mean()
                    ),
                    2,
                ),

            "avg_surge5d":
                round(
                    float(
                        study_df[
                            "Surge5D"
                        ].mean()
                    ),
                    2,
                ),

            "avg_surge10d":
                round(
                    float(
                        study_df[
                            "Surge10D"
                        ].mean()
                    ),
                    2,
                ),

            "avg_surge30d":
                round(
                    float(
                        study_df[
                            "Surge30D"
                        ].mean()
                    ),
                    2,
                ),

            "avg_surge1m":
                round(
                    float(
                        study_df[
                            "Surge1M"
                        ].mean()
                    ),
                    2,
                ),

            "avg_breakout_score":
                round(
                    float(
                        study_df[
                            "BreakoutScore"
                        ].mean()
                    ),
                    2,
                ),

            "avg_institutional_confidence":
                round(
                    float(
                        study_df[
                            "InstitutionalConfidence"
                        ].mean()
                    ),
                    2,
                ),
        }

    return {
        "winner_threshold":
            winner_threshold,

        "lookahead_days":
            lookahead_days,

        "winner_explosions":
            len(
                winner_events
            ),

        "study_results":
            results,
    }
def run_pre_explosion_study(
    raw: pd.DataFrame,
) -> dict:

    analytics = compute_delivery_analytics(raw)

    exploded = analytics[
        analytics["ExplosionCategory"] == "EXPLODED"
    ].copy()

    if exploded.empty:
        return {
            "error": "No exploded stocks found"
        }

    first_explosions = (
        exploded
        .sort_values("Date")
        .groupby("Symbol")
        .head(1)
        .copy()
    )

    print(
        f"Found {len(first_explosions)} first explosion events"
    )

    lookbacks = [
        20,
        15,
        10,
        5,
        0,
    ]

    results = {}

    stock_lookup = {
        symbol: group.sort_values("Date").reset_index(drop=True)
        for symbol, group
        in analytics.groupby("Symbol")
    }

    for days_before in lookbacks:

        observations = []

        for _, explosion_row in first_explosions.iterrows():

            symbol = explosion_row["Symbol"]

            explosion_date = explosion_row["Date"]

            stock = stock_lookup.get(
                symbol
            )

            if stock is None:
                continue

            matching_idx = stock.index[
                stock["Date"] == explosion_date
            ]

            if len(matching_idx) == 0:
                continue

            explosion_idx = matching_idx[0]

            target_idx = (
                explosion_idx
                - days_before
            )

            if target_idx < 0:
                continue

            row = stock.iloc[
                target_idx
            ]

            observations.append(
                {
                    "AccumulationScore":
                        row["AccumulationScore"],

                    "ExplosionScore":
                        row["ExplosionScore"],

                    "Surge5D":
                        row["Surge5D"],

                    "Surge10D":
                        row["Surge10D"],

                    "Surge30D":
                        row["Surge30D"],

                    "Surge1M":
                        row["Surge1M"],
                }
            )

        study_df = pd.DataFrame(
            observations
        )

        if study_df.empty:

            results[
                f"{days_before}_days_before"
            ] = {
                "count": 0
            }

            continue

        results[
            f"{days_before}_days_before"
        ] = {
            "count": int(
                len(study_df)
            ),

            "avg_accumulation_score":
                round(
                    float(
                        study_df[
                            "AccumulationScore"
                        ].mean()
                    ),
                    2,
                ),

            "avg_explosion_score":
                round(
                    float(
                        study_df[
                            "ExplosionScore"
                        ].mean()
                    ),
                    2,
                ),

            "avg_surge_5d":
                round(
                    float(
                        study_df[
                            "Surge5D"
                        ].mean()
                    ),
                    2,
                ),

            "avg_surge_10d":
                round(
                    float(
                        study_df[
                            "Surge10D"
                        ].mean()
                    ),
                    2,
                ),

            "avg_surge_30d":
                round(
                    float(
                        study_df[
                            "Surge30D"
                        ].mean()
                    ),
                    2,
                ),

            "avg_surge_1m":
                round(
                    float(
                        study_df[
                            "Surge1M"
                        ].mean()
                    ),
                    2,
                ),
        }

    return {
        "exploded_stocks":
            int(
                len(
                    first_explosions
                )
            ),

        "study_results":
            results,
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
        '''candidates = analytics[
            analytics["ExplosionCategory"] == category
        ].copy()'''
        candidates = (
            analytics[
                analytics["ExplosionCategory"] == category
            ]
            .sort_values("Date")
            .groupby("Symbol")
            .tail(1)
            .copy()
        )
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
