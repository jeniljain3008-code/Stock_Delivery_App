from backend.app.db.models import (
    UltraSignal,
)


def register_ultra_signals(
    db,
    ultra_df,
):

    if ultra_df.empty:
        return

    for _, row in ultra_df.iterrows():

        exists = (
            db.query(
                UltraSignal
            )
            .filter(
                UltraSignal.symbol
                == row["Symbol"]
            )
            .filter(
                UltraSignal.signal_date
                == row["Date"]
            )
            .first()
        )

        if exists:
            continue

        signal = UltraSignal(
            symbol=row["Symbol"],

            signal_date=row["Date"],

            signal_high=float(
                row["High"]
            ),

            signal_close=float(
                row["Close"]
            ),

            signal_rank=float(
                row.get(
                    "SwingRankScore",
                    0,
                )
            ),

            delivery_percent=float(
                row.get(
                    "DeliveryPercent",
                    0,
                )
            ),

            is_breakout=False,
        )

        db.add(signal)

    db.commit()
