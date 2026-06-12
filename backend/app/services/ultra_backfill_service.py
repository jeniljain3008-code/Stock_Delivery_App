from datetime import timedelta

from sqlalchemy.orm import Session

from backend.app.db.models import UltraSignal
from backend.app.services.delivery_engine import (
    compute_delivery_analytics,
    remove_etfs,
)


def backfill_ultra_signals(
    db: Session,
    raw_df,
    days: int = 30,
):

    analytics = compute_delivery_analytics(
        raw_df
    )

    analytics = remove_etfs(
        analytics
    )

    analytics["Date"] = (
        analytics["Date"]
        .dt.date
    )

    all_dates = sorted(
        analytics["Date"]
        .unique()
    )

    target_dates = (
        all_dates[-days:]
        if len(all_dates) > days
        else all_dates
    )

    inserted = 0

    for trade_date in target_dates:

        snapshot = analytics[
            analytics["Date"]
            == trade_date
        ].copy()

        ultra = snapshot[
            (
                snapshot[
                    "ExplosionCategory"
                ]
                == "EXPLODED"
            )
            &
            (
                snapshot[
                    "DeliveryPercent"
                ]
                >= 60
            )
            &
            (
                snapshot[
                    "Surge30D"
                ]
                >= 3.2
            )
        ]

        for _, row in ultra.iterrows():

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
                    == trade_date
                )
                .first()
            )

            if exists:
                continue

            db.add(
                UltraSignal(
                    symbol=row[
                        "Symbol"
                    ],

                    signal_date=
                    trade_date,

                    signal_high=float(
                        row["High"]
                    ),

                    breakout_close=None,

                    breakout_date=None,

                    is_breakout=False,
                )
            )

            inserted += 1

    db.commit()

    return {
        "inserted":
            inserted,
        "dates":
            len(target_dates),
    }
