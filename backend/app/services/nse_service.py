from io import StringIO
from backend.app.db.session import SessionLocal
from backend.app.repositories.stocks import StockRepository

import httpx
import pandas as pd


class NSEService:

    async def fetch_delivery_data(
        self,
        trade_date: str,
    ) -> pd.DataFrame:

        formatted = (
            pd.to_datetime(trade_date)
            .strftime("%d%m%Y")
        )

        url = (
            f"https://archives.nseindia.com/products/content/"
            f"sec_bhavdata_full_{formatted}.csv"
        )

        async with httpx.AsyncClient(
            timeout=60
        ) as client:

            response = await client.get(url)

        response.raise_for_status()

        df = pd.read_csv(
            StringIO(response.text)
        )

        df.columns = [
            col.strip()
            for col in df.columns
        ]

        df = df[
            df["SERIES"]
            .astype(str)
            .str.strip()
            == "EQ"
        ].copy()

        return self.transform(df)

    def transform(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        out = pd.DataFrame()

        out["Date"] = pd.to_datetime(
            df["DATE1"],
            errors="coerce",
        ).dt.date

        out["Symbol"] = (
            df["SYMBOL"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        out["Open"] = pd.to_numeric(
            df["OPEN_PRICE"],
            errors="coerce",
        )

        out["High"] = pd.to_numeric(
            df["HIGH_PRICE"],
            errors="coerce",
        )

        out["Low"] = pd.to_numeric(
            df["LOW_PRICE"],
            errors="coerce",
        )

        out["Close"] = pd.to_numeric(
            df["CLOSE_PRICE"],
            errors="coerce",
        )

        out["Volume"] = pd.to_numeric(
            df["TTL_TRD_QNTY"],
            errors="coerce",
        )

        out["DeliveryQty"] = pd.to_numeric(
            df["DELIV_QTY"],
            errors="coerce",
        )

        out["DeliveryPercent"] = pd.to_numeric(
            df["DELIV_PER"],
            errors="coerce",
        )

        out = out.dropna()

        return out

     async def load_to_database(
            self,
            trade_date: str,
        ) -> dict:

    df = await self.fetch_delivery_data(
        trade_date
    )

    db = SessionLocal()

    inserted = 0

    try:

        repo = StockRepository(db)

        for row in df.to_dict(
            orient="records"
        ):

            stock = repo.get_or_create(
                row["Symbol"]
            )

            repo.upsert_price(
                stock,
                row,
            )

            inserted += 1

        db.commit()

        return {
            "status": "success",
            "trade_date": trade_date,
            "rows_loaded": inserted,
        }

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()   
