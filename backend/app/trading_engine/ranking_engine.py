"""
==========================================================
Ranking Engine
==========================================================

Responsible for

• Institutional Conviction Score

• Entry Quality

• Position Sizing

• Portfolio Ranking

==========================================================
"""

from __future__ import annotations

import pandas as pd


class RankingEngine:

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

        self.df["VolumeRatio"] = (
            self.df["Volume"]
            /
            self.df["VolumeMA20"]
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

        self.df["ConvictionScore"] = self.df.apply(
            self.calculate_conviction_score,
            axis=1,
        )

    # --------------------------------------------------
    # MASTER SCORE
    # --------------------------------------------------

    def calculate_conviction_score(self, row):

        score = 0

        # ---------------------------------------------
        # Swing Rank (25)
        # ---------------------------------------------

        score += min(
            row.SwingRankScore,
            100,
        ) * 0.25

        # ---------------------------------------------
        # Accumulation (20)
        # ---------------------------------------------

        score += (
            row.AccumulationScore
            * 0.20
        )

        # ---------------------------------------------
        # Delivery (15)
        # ---------------------------------------------

        score += min(
            row.DeliveryPercent,
            100,
        ) * 0.15

        # ---------------------------------------------
        # Explosion (10)
        # ---------------------------------------------

        score += min(
            row.ExplosionScore * 15,
            10,
        )

        # ---------------------------------------------
        # Breakout Score (10)
        # ---------------------------------------------

        score += (
            row.BreakoutScore
            * 0.10
        )

        # ---------------------------------------------
        # Volume Ratio (10)
        # ---------------------------------------------

        score += min(
            row.VolumeRatio,
            2,
        ) * 5

        # ---------------------------------------------
        # Distance To Breakout (10)
        # ---------------------------------------------

        if row.DistanceToBreakout <= 0.5:

            score += 10

        elif row.DistanceToBreakout <= 1:

            score += 8

        elif row.DistanceToBreakout <= 2:

            score += 6

        elif row.DistanceToBreakout <= 3:

            score += 3

        return round(score,2)

    # --------------------------------------------------
    # STAR RATING
    # --------------------------------------------------

    def star_rating(self, score):

        if score >= 95:
            return "★★★★★"

        if score >= 90:
            return "★★★★☆"

        if score >= 85:
            return "★★★★"

        if score >= 75:
            return "★★★"

        if score >= 65:
            return "★★"

        return "★"

    # --------------------------------------------------
    # POSITION SIZE
    # --------------------------------------------------

    def suggested_allocation(self, score):

        if score >= 95:
            return 30

        if score >= 90:
            return 25

        if score >= 85:
            return 20

        if score >= 80:
            return 15

        return 10

    # --------------------------------------------------
    # ACTION
    # --------------------------------------------------

    def suggested_action(self, score):

        if score >= 95:
            return "BUY"

        if score >= 90:
            return "PILOT"

        if score >= 80:
            return "WATCH"

        return "IGNORE"

    # --------------------------------------------------
    # FULL WATCHLIST
    # --------------------------------------------------

    def institutional_watchlist(self):

        df = self.df.copy()

        df["Stars"] = df["ConvictionScore"].apply(
            self.star_rating
        )

        df["Allocation"] = df[
            "ConvictionScore"
        ].apply(
            self.suggested_allocation
        )

        df["Action"] = df[
            "ConvictionScore"
        ].apply(
            self.suggested_action
        )

        return (
            df
            .sort_values(
                "ConvictionScore",
                ascending=False,
            )
            [
                [
                    "Symbol",
                    "Close",
                    "ConvictionScore",
                    "Stars",
                    "Allocation",
                    "Action",
                    "SwingRankScore",
                    "AccumulationScore",
                    "DeliveryPercent",
                    "DistanceToBreakout",
                    "VolumeRatio",
                ]
            ]
        )

    # --------------------------------------------------
    # TOP PICKS
    # --------------------------------------------------

    def top_picks(self, n=10):

        return (
            self.institutional_watchlist()
            .head(n)
        )

    # --------------------------------------------------
    # PORTFOLIO
    # --------------------------------------------------

    def build_portfolio(self, capital):

        picks = self.top_picks(5).copy()

        picks["Investment"] = (
            picks["Allocation"]
            / 100
            * capital
        ).round(2)

        picks["Quantity"] = (
            picks["Investment"]
            /
            picks["Close"]
        ).astype(int)

        return picks
 
