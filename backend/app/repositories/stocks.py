from sqlalchemy import select, text
from sqlalchemy.orm import Session
import pandas as pd

from backend.app.db.models import Stock, StockPrice


class StockRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, symbol: str) -> Stock:
        normalized = symbol.upper().strip()

        stock = self.db.scalar(
            select(Stock).where(
                Stock.symbol == normalized
            )
        )

        if stock:
            return stock

        stock = Stock(symbol=normalized)

        self.db.add(stock)

        self.db.flush()

        return stock

    def list_symbols(self) -> list[str]:
        return list(
            self.db.scalars(
                select(Stock.symbol).order_by(Stock.symbol)
            )
        )

    def upsert_price(self, stock: Stock, row: dict) -> None:
        existing = self.db.scalar(
            select(StockPrice).where(
                StockPrice.stock_id == stock.id,
                StockPrice.trade_date == row["Date"],
            )
        )

        payload = {
            "open": row["Open"],
            "high": row["High"],
            "low": row["Low"],
            "close": row["Close"],
            "volume": int(row["Volume"]),
            "delivery_qty": int(row["DeliveryQty"]),
            "delivery_percent": float(row["DeliveryPercent"]),
        }

        if existing:
            for key, value in payload.items():
                setattr(existing, key, value)
            return

        self.db.add(
            StockPrice(
                stock_id=stock.id,
                trade_date=row["Date"],
                **payload,
            )
        )

    def get_all_prices_dataframe(self) -> pd.DataFrame:
    """
    Loads all stock price history from Supabase/PostgreSQL
    into a pandas dataframe for analytics.
    """

    query = text(
        """
        SELECT
            sp.trade_date AS "Date",
            s.symbol AS "Symbol",
            sp.open AS "Open",
            sp.high AS "High",
            sp.low AS "Low",
            sp.close AS "Close",
            sp.volume AS "Volume",
            sp.delivery_qty AS "DeliveryQty",
            sp.delivery_percent AS "DeliveryPercent"
        FROM stock_prices sp
        INNER JOIN stocks s
            ON s.id = sp.stock_id
        ORDER BY
            s.symbol,
            sp.trade_date
        """
    )

    result = self.db.execute(query)

    rows = result.fetchall()

    if not rows:
        return pd.DataFrame(
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

    df = pd.DataFrame(
        rows,
        columns=result.keys(),
    )

    # Convert PostgreSQL NUMERIC/DECIMAL values to Pandas numeric types
    numeric_cols = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "DeliveryQty",
        "DeliveryPercent",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Ensure Date column is datetime
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df
