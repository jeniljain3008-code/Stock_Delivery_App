import logging
from tempfile import SpooledTemporaryFile

from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.repositories.stocks import StockRepository
from ingestion.validators import parse_delivery_file

logger = logging.getLogger(__name__)


class UploadService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = StockRepository(db)

    async def ingest(self, file: UploadFile) -> dict:
            suffix = file.filename.rsplit(".", 1)[-1].lower() if file.filename else "csv"

    with SpooledTemporaryFile() as tmp:
        tmp.write(await file.read())
        tmp.seek(0)

        df = parse_delivery_file(tmp, suffix=suffix)

    logger.warning(f"Rows after validation = {len(df)}")
    logger.warning("Starting database insert")

    try:

        counter = 0

        for row in df.to_dict(orient="records"):

            counter += 1

            if counter <= 10:
                logger.warning(
                    f"Processing row {counter} : Symbol={row['Symbol']}"
                )

            stock = self.repo.get_or_create(row["Symbol"])

            self.repo.upsert_price(stock, row)

        logger.warning("About to commit")

        self.db.commit()

        logger.warning("Commit successful")

    except Exception as e:

        self.db.rollback()

        logger.exception(
            f"UPLOAD FAILED: {str(e)}"
        )

        raise

    return {
        "status": "accepted",
        "rows_loaded": len(df),
        "file_name": file.filename,
    }
