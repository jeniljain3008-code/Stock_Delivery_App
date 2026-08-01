 """
==========================================================
Entry Engine
==========================================================

Responsible for

• Distance To Breakout

• Near Breakout

• Pilot Entry

• Entry Score

• Suggested Allocation

• Breakout Trigger

==========================================================
"""

from __future__ import annotations

import pandas as pd

from .models import (
    NearBreakout,
    PilotEntry,
)


class EntryEngine:

    def __init__(
        self,
        analytics_df: pd.DataFrame,
    ):

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

        self.df["DistanceToBreakout"] = (
            (
                self.df["High20"]
                -
                self.df["Close"]
            )
            /
            self.df["High20"]
        ) * 100

        self.df["VolumeRatio"] = (
            self.df["Volume"]
            /
            self.df["VolumeMA20"]
        )

    # -------------------------------------------------
    # Entry Score
    # -------------------------------------------------

    def calculate_entry_score(
        self,
        row,
    ):

        score = 0

        # Distance (40)

        if row.DistanceToBreakout <= 0.50:
            score += 40

        elif row.DistanceToBreakout <= 1:
            score += 35

        elif row.DistanceToBreakout <= 2:
            score += 30

        elif row.DistanceToBreakout <= 3:
            score += 20

        # Swing Rank (25)

        score += min(
            row.SwingRankScore,
            100,
        ) * 0.25

        # Accumulation (15)

        score += (
            row.AccumulationScore
            * 0.15
        )

        # Delivery (10)

        score += (
            row.DeliveryPercent
            * 0.10
        )

        # Volume (10)

        score += min(
            row.VolumeRatio,
            2,
        ) * 5

        return round(
            score,
            2,
        )

    # -------------------------------------------------
    # Near Breakout
    # -------------------------------------------------

    def get_near_breakouts(
        self,
        max_distance=2,
    ):

        df = self.df.copy()

        df = df[

            (df.DistanceToBreakout <= max_distance)

            &

            (df.ExplosionCategory == "EXPLODED")

        ]

        rows = []

        for _, row in df.iterrows():

            rows.append(

                NearBreakout(

                    symbol=row.Symbol,

                    signal_high=row.High20,

                    current_close=row.Close,

                    distance_pct=round(
                        row.DistanceToBreakout,
                        2,
                    ),

                    swing_rank=row.SwingRankScore,

                    accumulation_score=row.AccumulationScore,

                    breakout_score=row.BreakoutScore,

                )

            )

        return rows

    # -------------------------------------------------
    # Pilot Entries
    # -------------------------------------------------

    def get_pilot_entries(
        self,
    ):

        df = self.df.copy()

        df["EntryScore"] = df.apply(
            self.calculate_entry_score,
            axis=1,
        )

        df = df[

            (df.EntryScore >= 85)

            &

            (df.SwingRankScore >= 85)

            &

            (df.AccumulationScore >= 75)

            &

            (df.DistanceToBreakout <= 2)

        ]

        df = df.sort_values(
            "EntryScore",
            ascending=False,
        )

        entries = []

        for _, row in df.iterrows():

            entries.append(

                PilotEntry(

                    symbol=row.Symbol,

                    entry_score=row.EntryScore,

                    suggested_allocation=25,

                    signal_strength="★★★★★",

                )

            )

        return entries

    # -------------------------------------------------
    # Breakout Trigger
    # -------------------------------------------------

    def get_breakout_candidates(
        self,
    ):

        df = self.df.copy()

        breakout = df[

            (df.Close > df.High20)

            &

            (df.VolumeRatio > 1.25)

            &

            (df.SwingRankScore > 80)

        ]

        return breakout.sort_values(
            "SwingRankScore",
            ascending=False,
        )

    # -------------------------------------------------
    # Position Size
    # -------------------------------------------------

    def suggested_position_size(
        self,
        entry_score,
    ):

        if entry_score >= 95:

            return 40

        if entry_score >= 90:

            return 30

        if entry_score >= 85:

            return 25

        if entry_score >= 80:

            return 20

        return 10
