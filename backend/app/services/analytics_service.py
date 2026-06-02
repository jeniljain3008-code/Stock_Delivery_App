import pandas as pd

from analytics.backtesting import run_backtest
from analytics.delivery_engine import compute_delivery_analytics, scan_gold_stocks
from analytics.relative_strength import compute_relative_strength
from analytics.sector_rotation import compute_sector_rotation


class AnalyticsService:
    def __init__(self) -> None:
        self.demo_df = pd.read_csv("sample_data/nse_delivery_sample.csv", parse_dates=["Date"])

    def dashboard(self) -> dict:
        analytics = compute_delivery_analytics(self.demo_df)
        latest = analytics.sort_values("Date").groupby("Symbol").tail(1)
        accumulation = latest[latest["AccumulationScore"] >= 70]
        distribution = latest[latest["AccumulationLabel"] == "Distribution"]
        return {
            "kpis": [
                {"label": "Total Stocks Analyzed", "value": int(latest.Symbol.nunique())},
                {"label": "Stocks in Accumulation", "value": int(len(accumulation))},
                {"label": "Stocks in Distribution", "value": int(len(distribution))},
                {
                    "label": "Gold Stock Candidates",
                    "value": int(len(scan_gold_stocks(self.demo_df))),
                },
            ],
            "top_delivery_surge": self._rows(
                latest.sort_values("Surge1M", ascending=False).head(5)
            ),
            "top_breakouts": self._rows(
                latest.sort_values("BreakoutScore", ascending=False).head(5)
            ),
            "sector_leaders": compute_sector_rotation(analytics).head(5).to_dict(orient="records"),
            "market_summary": "Delivery-led accumulation is concentrated in high-score names where delivery expansion is confirmed by price above key moving averages.",
        }

    def stocks(self) -> list[dict]:
        latest = (
            compute_delivery_analytics(self.demo_df).sort_values("Date").groupby("Symbol").tail(1)
        )
        return self._rows(latest.sort_values("AccumulationScore", ascending=False))

    def gold_stocks(self) -> list[dict]:
        return scan_gold_stocks(self.demo_df).to_dict(orient="records")

    def stock_analytics(self, symbol: str) -> dict:
        df = compute_delivery_analytics(self.demo_df)
        stock = df[df.Symbol == symbol.upper()].copy()
        if stock.empty:
            return {"symbol": symbol.upper(), "series": [], "summary": None}
        rs = compute_relative_strength(df, benchmark_symbol="NIFTY")
        return {
            "symbol": symbol.upper(),
            "series": stock.to_dict(orient="records"),
            "relative_strength": rs.get(symbol.upper(), 50),
        }

    def sector_rotation(self) -> list[dict]:
        return compute_sector_rotation(compute_delivery_analytics(self.demo_df)).to_dict(
            orient="records"
        )

    def backtest(self, request) -> dict:
        return run_backtest(
            self.demo_df,
            request.strategy,
            request.start_date,
            request.end_date,
            request.min_accumulation_score,
        )

    @staticmethod
    def _rows(df: pd.DataFrame) -> list[dict]:
        out = []
        for row in df.to_dict(orient="records"):
            out.append(
                {
                    "symbol": row["Symbol"],
                    "close": round(float(row["Close"]), 2),
                    "sector": row.get("Sector", "Unclassified"),
                    "market_cap": row.get("MarketCap", "mid"),
                    "delivery_surge": round(float(row.get("Surge1M", 1)), 2),
                    "accumulation_score": round(float(row.get("AccumulationScore", 0)), 2),
                    "breakout_score": round(float(row.get("BreakoutScore", 0)), 2),
                    "risk_rating": row.get("RiskRating", "Medium"),
                    "swing_signal": row.get("SwingSignal", "WATCH"),
                }
            )
        return out
