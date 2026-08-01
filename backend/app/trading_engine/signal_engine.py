"""
==========================================================
Signal Engine
==========================================================

Purpose
-------
Converts the analytics dataframe into trading signals.

This engine NEVER talks to:

- Database
- FastAPI
- SQLAlchemy
- Dashboard

It only works on the analytics dataframe produced by
delivery_engine.compute_delivery_analytics()

==========================================================
"""

from __future__ import annotations

import pandas as pd

from .models import TradeSignal


class SignalEngine:

    def __init__(self, analytics_df: pd.DataFrame):

        self.df = analytics_df.copy()

        if self.df.empty:
            return

        self.df = (
            self.df
            .sort_values("Date")
            .groupby("Symbol", group_keys=False)
            .tail(1)
            .reset_index(drop=True)
        )

    # --------------------------------------------------
    # Internal
    # --------------------------------------------------

    def _rows_to_signals(
        self,
        df: pd.DataFrame,
    ) -> list[TradeSignal]:

        signals = []

        for _, row in df.iterrows():

            signals.append(

                TradeSignal(

                    symbol=row["Symbol"],

                    signal_date=row["Date"],

                    close=float(row["Close"]),

                    high=float(row["High"]),

                    delivery_percent=float(row["DeliveryPercent"]),

                    surge_5d=float(row["Surge5D"]),

                    surge_10d=float(row["Surge10D"]),

                    surge_30d=float(row["Surge30D"]),

                    explosion_score=float(row["ExplosionScore"]),

                    accumulation_score=float(row["AccumulationScore"]),

                    breakout_score=float(row["BreakoutScore"]),

                    swing_rank=float(row["SwingRankScore"]),

                    swing_signal=str(row["SwingSignal"]),

                    risk_rating=str(row["RiskRating"]),
                )

            )

        return signals

    # --------------------------------------------------
    # Public APIs
    # --------------------------------------------------

    def get_all(self) -> list[TradeSignal]:

        return self._rows_to_signals(self.df)

    def get_exploded(self) -> list[TradeSignal]:

        exploded = self.df[
            self.df["ExplosionCategory"] == "EXPLODED"
        ]

        return self._rows_to_signals(exploded)

    def get_ready(self) -> list[TradeSignal]:

        ready = self.df[
            self.df["ExplosionCategory"] == "READY_TO_EXPLODE"
        ]

        return self._rows_to_signals(ready)

    def get_preparing(self) -> list[TradeSignal]:

        preparing = self.df[
            self.df["ExplosionCategory"] == "PREPARING_TO_EXPLODE"
        ]

        return self._rows_to_signals(preparing)

    def get_elite(self) -> list[TradeSignal]:

        elite = self.df[

            (self.df["ExplosionCategory"] == "EXPLODED")
            &
            (self.df["DeliveryPercent"] >= 60)
            &
            (self.df["Surge30D"] >= 2.8)

        ]

        elite = elite.sort_values(
            "SwingRankScore",
            ascending=False,
        )

        return self._rows_to_signals(elite)

    def get_ultra(self) -> list[TradeSignal]:

        ultra = self.df[

            (self.df["ExplosionCategory"] == "EXPLODED")
            &
            (self.df["DeliveryPercent"] >= 60)
            &
            (self.df["Surge30D"] >= 3.2)

        ]

        ultra = ultra.sort_values(
            "SwingRankScore",
            ascending=False,
        )

        return self._rows_to_signals(ultra)

    def get_top_ranked(
        self,
        limit: int = 20,
    ) -> list[TradeSignal]:

        ranked = (
            self.df
            .sort_values(
                "SwingRankScore",
                ascending=False,
            )
            .head(limit)
        )

        return self._rows_to_signals(ranked)

    def get_buy_candidates(self) -> list[TradeSignal]:

        buy = self.df[

            (self.df["SwingSignal"] == "BUY")
            &
            (self.df["AccumulationScore"] >= 75)

        ]

        buy = buy.sort_values(
            "SwingRankScore",
            ascending=False,
        )

        return self._rows_to_signals(buy)

    def get_watch_candidates(self) -> list[TradeSignal]:

        watch = self.df[

            (self.df["SwingSignal"] == "WATCH")
            &
            (self.df["AccumulationScore"] >= 60)

        ]

        watch = watch.sort_values(
            "SwingRankScore",
            ascending=False,
        )

        return self._rows_to_signals(watch)
