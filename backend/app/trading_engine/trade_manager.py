"""
==========================================================
Trade Manager
==========================================================

Owns the complete trade lifecycle.

SIGNAL

↓

NEAR_BREAKOUT

↓

PILOT_ENTRY

↓

BREAKOUT

↓

OPEN

↓

PARTIAL_EXIT

↓

CLOSED

==========================================================
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from backend.app.db.models import UltraSignal


class TradeManager:

    def __init__(
        self,
        db,
        latest_df: pd.DataFrame,
    ):

        self.db = db

        self.df = latest_df.copy()

        if self.df.empty:
            return

        self.df = (
            self.df
            .sort_values("Date")
            .groupby("Symbol")
            .tail(1)
        )

        self.lookup = {

            row["Symbol"]: row

            for _, row

            in self.df.iterrows()

        }

    # ------------------------------------------------------
    # Update Every Trade
    # ------------------------------------------------------

    def update_trades(self):

        trades = self.db.query(
            UltraSignal
        ).all()

        updated = 0

        for trade in trades:

            row = self.lookup.get(
                trade.symbol
            )

            if row is None:
                continue

            current_price = float(
                row["Close"]
            )

            trade.current_price = current_price

            # Highest Close

            if (
                trade.highest_close is None
                or
                current_price > float(trade.highest_close)
            ):

                trade.highest_close = current_price

            # Return

            if trade.entry_price:

                trade.return_pct = round(

                    (
                        (
                            current_price
                            -
                            float(trade.entry_price)
                        )
                        /
                        float(trade.entry_price)
                    )
                    * 100,
                    2,
                )

            # Max Return

            if trade.entry_price:

                max_return = round(

                    (
                        (
                            float(trade.highest_close)
                            -
                            float(trade.entry_price)
                        )
                        /
                        float(trade.entry_price)
                    )
                    * 100,
                    2,
                )

                trade.max_return_pct = max_return

            # Days Active

            if trade.breakout_date:

                trade.days_active = (

                    date.today()

                    -

                    trade.breakout_date

                ).days

            # Status

            trade.entry_status = self.determine_status(
                trade
            )

            updated += 1

        self.db.commit()

        return updated

    # ------------------------------------------------------
    # Status
    # ------------------------------------------------------

    def determine_status(
        self,
        trade,
    ):

        if trade.exit_date:

            return "CLOSED"

        if trade.entry_price:

            if (
                trade.return_pct
                is not None
            ):

                if trade.return_pct >= 20:

                    return "PARTIAL_EXIT"

                if trade.return_pct >= 0:

                    return "OPEN"

                return "LOSS"

        if trade.breakout_date:

            return "BREAKOUT"

        return "SIGNAL"

    # ------------------------------------------------------
    # Suggested Action
    # ------------------------------------------------------

    def suggested_action(
        self,
        trade,
    ):

        status = trade.entry_status

        if status == "SIGNAL":

            return "WATCH"

        if status == "BREAKOUT":

            return "BUY"

        if status == "OPEN":

            return "HOLD"

        if status == "PARTIAL_EXIT":

            return "BOOK 50%"

        if status == "LOSS":

            return "REVIEW"

        if status == "CLOSED":

            return "DONE"

        return "WATCH"

    # ------------------------------------------------------
    # Active Trades
    # ------------------------------------------------------

    def active_trades(self):

        return (

            self.db.query(

                UltraSignal

            )

            .filter(

                UltraSignal.entry_status.in_(

                    [

                        "BREAKOUT",

                        "OPEN",

                        "PARTIAL_EXIT",

                    ]

                )

            )

            .all()

        )

    # ------------------------------------------------------
    # Closed Trades
    # ------------------------------------------------------

    def closed_trades(self):

        return (

            self.db.query(

                UltraSignal

            )

            .filter(

                UltraSignal.entry_status == "CLOSED"

            )

            .all()

        )

    # ------------------------------------------------------
    # Portfolio Summary
    # ------------------------------------------------------

    def portfolio_summary(self):

        trades = self.active_trades()

        if len(trades) == 0:

            return {

                "active": 0,

                "avg_return": 0,

                "best": 0,

                "worst": 0,

            }

        returns = [

            float(

                t.return_pct or 0

            )

            for t

            in trades

        ]

        return {

            "active": len(trades),

            "avg_return": round(

                sum(returns)

                /

                len(returns),

                2,

            ),

            "best": round(

                max(returns),

                2,

            ),

            "worst": round(

                min(returns),

                2,

            ),

        }
