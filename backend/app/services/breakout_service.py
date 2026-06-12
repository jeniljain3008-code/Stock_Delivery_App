import pandas as pd

from backend.app.db.models import (
    UltraSignal,
)


def get_actual_ultra_breakouts(
    db,
    latest_df: pd.DataFrame,
):

    signals = (
        db.query(
            UltraSignal
        )
        .filter(
            UltraSignal.is_breakout == False
        )
        .all()
    )

    if not signals:
        return pd.DataFrame()

    breakout_rows = []

    latest_lookup = {
        row["Symbol"]: row
        for _, row
        in latest_df.iterrows()
    }

    for signal in signals:

        stock = latest_lookup.get(
            signal.symbol
        )

        if stock is None:
            continue

        latest_close = float(
            stock["Close"]
        )

        signal_high = float(
            signal.signal_high
        )

        if latest_close > signal_high:

            breakout_rows.append(
                stock
            )

            signal.is_breakout = True

            signal.breakout_date = (
                stock["Date"]
            )

            signal.breakout_close = (
                latest_close
            )

    db.commit()

    if len(
        breakout_rows
    ) == 0:

        return pd.DataFrame()

    return pd.DataFrame(
        breakout_rows
    )
