import pandas as pd

from backend.app.db.models import (
    UltraSignal,
)

# ==========================================
# Ultra Breakout Thresholds
# ==========================================

ULTRA_BREAKOUT_MIN_VOLUME_RATIO = 1.25

ULTRA_BREAKOUT_MIN_RANK = 80


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

        volume_ratio = float(
            stock.get(
                "VolumeRatio",
                0,
            )
        )

        swing_rank_score = float(
            stock.get(
                "SwingRankScore",
                0,
            )
        )

        breakout_condition = (

            latest_close > signal_high

            and

            volume_ratio
            >
            ULTRA_BREAKOUT_MIN_VOLUME_RATIO

            and

            swing_rank_score
            >
            ULTRA_BREAKOUT_MIN_RANK

        )

        if breakout_condition:

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

    breakout_df = pd.DataFrame(
        breakout_rows
    )

    breakout_df = (
        breakout_df
        .sort_values(
            "SwingRankScore",
            ascending=False,
        )
    )

    return breakout_df
