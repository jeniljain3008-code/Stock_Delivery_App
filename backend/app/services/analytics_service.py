import logging

import pandas as pd

from analytics.backtesting import (
    run_backtest,
    run_explosion_backtest,
    run_pre_explosion_study,
    run_pre_explosion_winner_study,
    run_winner_vs_loser_study,
    run_top_decile_study,
    run_filtered_exploded_backtest,
    run_exploded_filter_optimization
)
from analytics.delivery_engine import (
    compute_delivery_analytics, 
    scan_gold_stocks,
    scan_exploded_elite,
    scan_exploded_ultra,
)
from analytics.relative_strength import compute_relative_strength
from analytics.sector_rotation import compute_sector_rotation

from backend.app.db.session import SessionLocal
from backend.app.repositories.stocks import StockRepository

logger = logging.getLogger(__name__)


class AnalyticsService:

    def __init__(self):

        try:
            db = SessionLocal()

            try:
                self.demo_df = (
                    StockRepository(db)
                    .get_all_prices_dataframe()
                )

            finally:
                db.close()

            logger.info(
                f"Loaded {len(self.demo_df)} rows "
                f"for {self.demo_df['Symbol'].nunique()} stocks"
            )

        except Exception as e:

            logger.exception(
                f"Failed loading data from database: {str(e)}"
            )

            self.demo_df = pd.DataFrame(
                columns=[
                    "Date",
                    "Symbol",
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume",
                    "DeliveryQty",
                    "DeliveryPercent",
                ]
            )

    def dashboard(self) -> dict:

        if self.demo_df.empty:
            return {
                "kpis": [],
                "top_delivery_surge": [],
                "top_breakouts": [],
                "sector_leaders": [],
                "market_summary": "No data uploaded yet.",
            }

        analytics = compute_delivery_analytics(self.demo_df)

        latest = (
            analytics
            .sort_values("Date")
            .groupby("Symbol")
            .tail(1)
        )

        accumulation = latest[
            latest["AccumulationScore"] >= 70
        ]

        distribution = latest[
            latest["AccumulationLabel"] == "Distribution"
        ]

        exploded = (
            latest[
                latest["ExplosionCategory"]
                == "EXPLODED"
            ]
            .sort_values(
                "ExplosionScore",
                ascending=False,
            )
            .head(15)
        )

        ready_to_explode = (
            latest[
                latest["ExplosionCategory"]
                == "READY_TO_EXPLODE"
            ]
            .sort_values(
                "ExplosionScore",
                ascending=False,
            )
            .head(15)
        )

        preparing_to_explode = (
            latest[
                latest["ExplosionCategory"]
                == "PREPARING_TO_EXPLODE"
            ]
            .sort_values(
                "ExplosionScore",
                ascending=False,
            )
            .head(15)
        )
        return {
            "kpis": [
                {
                    "label": "Total Stocks Analyzed",
                    "value": int(latest.Symbol.nunique()),
                },
                {
                    "label": "Stocks in Accumulation",
                    "value": int(len(accumulation)),
                },
                {
                    "label": "Stocks in Distribution",
                    "value": int(len(distribution)),
                },
                {
                    "label": "Gold Stock Candidates",
                    "value": int(
                        len(
                            scan_gold_stocks(
                                self.demo_df
                            )
                        )
                    ),
                },
                {
                    "label": "Exploded",
                    "value": int(len(exploded)),
                },
                {
                    "label": "Ready To Explode",
                    "value": int(len(ready_to_explode)),
                },
                {
                    "label": "Preparing",
                    "value": int(len(preparing_to_explode)),
                },
            ],
            "top_delivery_surge": self._rows(
                latest
                .sort_values(
                    "Surge1M",
                    ascending=False,
                )
                .head(5)
            ),
            "top_breakouts": self._rows(
                latest
                .sort_values(
                    "BreakoutScore",
                    ascending=False,
                )
                .head(5)
            ),
            "exploded_stocks": self._rows(
                exploded
            ),
            "exploded_elite":
                self.exploded_elite(),

            "exploded_ultra":
                self.exploded_ultra(),

            "ready_to_explode": self._rows(
                ready_to_explode
            ),

            "preparing_to_explode": self._rows(
                preparing_to_explode
            ),
            "sector_leaders": (
                compute_sector_rotation(
                    analytics
                )
                .head(5)
                .to_dict(
                    orient="records"
                )
            ),
            "market_summary":
                "Delivery-led accumulation is concentrated in high-score names where delivery expansion is confirmed by price above key moving averages.",
        }

    def stocks(self) -> list[dict]:

        if self.demo_df.empty:
            return []

        latest = (
            compute_delivery_analytics(
                self.demo_df
            )
            .sort_values("Date")
            .groupby("Symbol")
            .tail(1)
        )

        return self._rows(
            latest.sort_values(
                "AccumulationScore",
                ascending=False,
            )
        )

    def gold_stocks(self) -> list[dict]:

        if self.demo_df.empty:
            return []

        return (
            scan_gold_stocks(
                self.demo_df
            )
            .to_dict(
                orient="records"
            )
        )

    def stock_analytics(
        self,
        symbol: str,
    ) -> dict:

        if self.demo_df.empty:
            return {
                "symbol": symbol.upper(),
                "series": [],
                "summary": None,
            }

        df = compute_delivery_analytics(
            self.demo_df
        )

        stock = df[
            df.Symbol == symbol.upper()
        ].copy()

        if stock.empty:
            return {
                "symbol": symbol.upper(),
                "series": [],
                "summary": None,
            }

        rs = compute_relative_strength(
            df,
            benchmark_symbol="NIFTY",
        )

        return {
            "symbol": symbol.upper(),
            "series": stock.to_dict(
                orient="records"
            ),
            "relative_strength": rs.get(
                symbol.upper(),
                50,
            ),
        }

    def sector_rotation(self) -> list[dict]:

        if self.demo_df.empty:
            return []

        return (
            compute_sector_rotation(
                compute_delivery_analytics(
                    self.demo_df
                )
            )
            .to_dict(
                orient="records"
            )
        )

    def backtest(self, request) -> dict:

        if self.demo_df.empty:
            return {
                "error": "No market data available"
            }

        return run_backtest(
            self.demo_df,
            request.strategy,
            request.start_date,
            request.end_date,
            request.min_accumulation_score,
        )

    @staticmethod
    def _rows(
        df: pd.DataFrame,
    ) -> list[dict]:

        out = []

        for row in df.to_dict(
            orient="records"
        ):
            print(
                "DeliveryPercent:",
                row.get(
                    "DeliveryPercent"
                )
            )
            out.append(
                {
                    "symbol": row["Symbol"],
                    "close": round(
                        float(row["Close"]),
                        2,
                    ),
                    "delivery_percent": round(
                        float(
                            row.get(
                                "DeliveryPercent",
                                row.get(
                                    "delivery_percent",
                                    0,
                                ),
                            )
                        ),
                        2,
                    ),
                    "sector": row.get(
                        "Sector",
                        "Unclassified",
                    ),
                    "market_cap": row.get(
                        "MarketCap",
                        "mid",
                    ),
                    "delivery_surge": round(
                        float(
                            row.get(
                                "Surge1M",
                                1,
                            )
                        ),
                        2,
                    ),
                    "surge_5d": round(
                        float(
                            row.get(
                                "Surge5D",
                                0,
                            )
                        ),
                        2,
                    ),

                    "surge_10d": round(
                        float(
                            row.get(
                                "Surge10D",
                                0,
                            )
                        ),
                        2,
                    ),

                    "surge_30d": round(
                        float(
                            row.get(
                                "Surge30D",
                                0,
                            )
                        ),
                        2,
                    ),

                    "explosion_score": round(
                        float(
                            row.get(
                                "ExplosionScore",
                                0,
                            )
                        ),
                        2,
                    ),
                    "accumulation_score": round(
                        float(
                            row.get(
                                "AccumulationScore",
                                0,
                            )
                        ),
                        2,
                    ),
                    "breakout_score": round(
                        float(
                            row.get(
                                "BreakoutScore",
                                0,
                            )
                        ),
                        2,
                    ),
                    "risk_rating": row.get(
                        "RiskRating",
                        "Medium",
                    ),
                    "swing_signal": row.get(
                        "SwingSignal",
                        "WATCH",
                    ),
                }
            )

        return out

    def winner_vs_loser_study(
        self,
        days: int = 365,
    ) -> dict:

        db = SessionLocal()
    
        try:
    
            repo = StockRepository(db)
    
            df = repo.get_backtest_dataframe(
                days=days
            )
    
        finally:
    
            db.close()
    
        return run_winner_vs_loser_study(
            df
        )

    def exploded_filter_optimization(
        self,
        days: int = 365,
    ) -> dict:

        db = SessionLocal()
    
        try:
    
            repo = StockRepository(db)
    
            df = repo.get_backtest_dataframe(
                days=days
            )
    
        finally:
    
            db.close()
    
        return run_exploded_filter_optimization(
            df
        )
    def filtered_exploded_backtest(
        self,
        days: int = 365,
    ) -> dict:

        db = SessionLocal()
    
        try:
    
            repo = StockRepository(db)
    
            df = repo.get_backtest_dataframe(
                days=days
            )
    
        finally:
    
            db.close()
    
        return run_filtered_exploded_backtest(
            df
        )
    def top_decile_study(
        self,
        days: int = 365,
    ) -> dict:

        db = SessionLocal()
    
        try:
    
            repo = StockRepository(db)
    
            df = repo.get_backtest_dataframe(
                days=days
            )
    
        finally:
    
            db.close()
    
        return run_top_decile_study(
            df
        )
    def pre_explosion_winner_study(
        self,
        days: int = 365,
    ) -> dict:

        db = SessionLocal()
    
        try:
    
            repo = StockRepository(db)
    
            df = repo.get_backtest_dataframe(
                days=days
            )
    
        finally:
    
            db.close()
    
        return run_pre_explosion_winner_study(
            df
        )
    def pre_explosion_study(
        self,
        days: int = 365,
    ) -> dict:

        db = SessionLocal()
    
        try:
    
            repo = StockRepository(db)
    
            df = repo.get_backtest_dataframe(
                days=days
            )
    
        finally:
    
            db.close()

        return run_pre_explosion_study(
            df
        )    

    def exploded_elite(
        self,
    ):

        return self._rows(
            scan_exploded_elite(
                self.demo_df
            ).head(100)
        )

    def exploded_ultra(
        self,
    ):

        return self._rows(
            scan_exploded_ultra(
                self.demo_df
            ).head(100)
        )
    def explosion_backtest(
        self,
        days: int = 365,
    ) -> dict:

        import gc

        if hasattr(
            self,
            "demo_df",
        ):
            del self.demo_df

        gc.collect()

        db = SessionLocal()

        try:

            repo = StockRepository(db)

            df = repo.get_backtest_dataframe(
                days=days,
            )

            print(
                "Rows fetched:",
                len(df)
            )

            print(
                "Min Date:",
                df["Date"].min()
            )

            print(
                "Max Date:",
                df["Date"].max()
            )

        finally:

            db.close()

        if df.empty:

            return {
                "error": "No market data available"
            }

        return run_explosion_backtest(
            df
        )
