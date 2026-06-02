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
        try:
            for row in df.to_dict(orient="records"):
                stock = self.repo.get_or_create(row["Symbol"])
                self.repo.upsert_price(stock, row)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Failed to persist uploaded delivery data from %s", file.filename)
            raise
        logger.info("Loaded %s delivery rows from %s", len(df), file.filename)
        return {"status": "accepted", "rows_loaded": len(df), "file_name": file.filename}
