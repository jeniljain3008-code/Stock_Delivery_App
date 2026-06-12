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
        for _, row
        in latest_df.iterrows()
    }

    tracker_rows = []

    for signal in signals:

        stock = latest_lookup.get(
            signal.symbol
        )

        if stock is None:
            continue

        current_close = float(
            stock["Close"]
        )

        breakout_close = float(
            signal.breakout_close
        )

        return_pct = round(
            (
                (
                    current_close
                    -
                    breakout_close
                )
                /
                breakout_close
            )
            * 100,
            2,
        )

        days_active = (
            date.today()
            -
            signal.breakout_date
        ).days

        tracker_rows.append(
            {
                "Symbol":
                    signal.symbol,

                "BreakoutDate":
                    signal.breakout_date,

                "EntryPrice":
                    breakout_close,

                "CurrentPrice":
                    current_close,

                "ReturnPct":
                    return_pct,

                "DaysActive":
                    days_active,

                "SwingRankScore":
                    stock.get(
                        "SwingRankScore",
                        0,
                    ),
            }
        )

    return pd.DataFrame(
        tracker_rows
    )
