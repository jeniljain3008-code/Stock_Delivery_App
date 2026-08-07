from datetime import datetime

from backend.app.db.models import UltraSignal


def register_ultra_signals(
    db,
    ultra_df,
):
    """
    Registers newly generated Ultra Signals.

    Only one signal per Symbol + Signal Date is stored.

    Future trade lifecycle is managed by TradeManager.
    """

    if ultra_df.empty:
        return

    new_signals = 0

    for _, row in ultra_df.iterrows():

        exists = (
            db.query(UltraSignal)
            .filter(
                UltraSignal.symbol == row["Symbol"]
            )
            .filter(
                UltraSignal.signal_date == row["Date"]
            )
            .first()
        )

        if exists:
            continue

        signal = UltraSignal(

            # --------------------------------------------------
            # Signal Information
            # --------------------------------------------------

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

            # --------------------------------------------------
            # Breakout Tracking
            # --------------------------------------------------

            is_breakout=False,

            breakout_date=None,

            breakout_close=None,

            # --------------------------------------------------
            # Trade Lifecycle
            # --------------------------------------------------

            entry_status="SIGNAL",

            entry_price=None,

            current_price=float(
                row["Close"]
            ),

            highest_close=float(
                row["Close"]
            ),

            return_pct=0,

            max_return_pct=0,

            days_active=0,

            exit_price=None,

            exit_date=None,

            entry_score=None,

            # --------------------------------------------------
            # Strategy Metadata
            # --------------------------------------------------

            entry_method="BREAKOUT",

            strategy_name="ULTRA_BREAKOUT",

            exit_reason=None,

            # --------------------------------------------------
            # Audit Fields
            # --------------------------------------------------

            status_changed_at=datetime.utcnow(),

        )

        db.add(signal)

        new_signals += 1

    db.commit()

    print(
        f"Registered {new_signals} new Ultra Signals"
    )
