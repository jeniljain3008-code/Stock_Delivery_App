from datetime import date

import pandas as pd

from backend.app.db.models import (
    UltraSignal,
)


def get_ultra_breakout_tracker(
    db,
    latest_df: pd.DataFrame,
):

    signals = (
        db.query(
            UltraSignal
        )
        .filter(
            UltraSignal.is_breakout == True
        )
        .all()
    )

    if not signals:
        return pd.DataFrame()

    latest_lookup = {
        row["Symbol"]: row
        for _, row in latest_df.iterrows()
    }

    tracker_rows = []

    for signal in signals:

        stock = latest_lookup.get(
            signal.symbol
        )

        if stock is None:
            continue

        current_price = float(
            stock["Close"]
        )

        entry_price = float(
            signal.breakout_close or 0
        )

        if entry_price <= 0:
            continue

        return_pct = (
            (
                current_price
                - entry_price
            )
            / entry_price
        ) * 100

        days_active = (
            date.today()
            - signal.breakout_date
        ).days

        tracker_rows.append(
            {
                "symbol": signal.symbol,

                "breakout_date":
                    str(
                        signal.breakout_date
                    ),

                "entry_price":
                    round(
                        entry_price,
                        2,
                    ),

                "current_price":
                    round(
                        current_price,
                        2,
                    ),

                "return_pct":
                    round(
                        return_pct,
                        2,
                    ),

                "days_active":
                    days_active,

                "swing_rank_score":
                    round(
                        float(
                            stock.get(
                                "SwingRankScore",
                                0,
                            )
                        ),
                        2,
                    ),
            }
        )

    return pd.DataFrame(
        tracker_rows
    )
