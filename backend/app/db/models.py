from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.session import Base


class Sector(Base):
    __tablename__ = "sectors"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    stocks: Mapped[list["Stock"]] = relationship(back_populates="sector")


class Stock(Base):
    __tablename__ = "stocks"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    symbol: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    company_name: Mapped[str | None] = mapped_column(String)
    sector_id: Mapped[str | None] = mapped_column(ForeignKey("sectors.id"))
    market_cap_category: Mapped[str | None] = mapped_column(String)
    sector: Mapped[Sector | None] = relationship(back_populates="stocks")
    prices: Mapped[list["StockPrice"]] = relationship(
        back_populates="stock", cascade="all, delete-orphan"
    )


class StockPrice(Base):
    __tablename__ = "stock_prices"
    __table_args__ = (UniqueConstraint("stock_id", "trade_date", name="uq_stock_trade_date"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    stock_id: Mapped[str] = mapped_column(
        ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False
    )
    trade_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    open: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    high: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    low: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    close: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    volume: Mapped[int] = mapped_column(nullable=False)
    delivery_qty: Mapped[int] = mapped_column(nullable=False)
    delivery_percent: Mapped[float] = mapped_column(Numeric(7, 3), nullable=False)
    stock: Mapped[Stock] = relationship(back_populates="prices")


class AnalyticsSnapshot(Base):
    __tablename__ = "analytics_snapshots"
    __table_args__ = (
        UniqueConstraint("stock_id", "trade_date", name="uq_snapshot_stock_trade_date"),
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    stock_id: Mapped[str] = mapped_column(
        ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False
    )
    trade_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    accumulation_score: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    breakout_score: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    relative_strength_score: Mapped[float | None] = mapped_column(Numeric(6, 2))
    institutional_confidence: Mapped[float | None] = mapped_column(Numeric(6, 2))
    swing_signal: Mapped[str] = mapped_column(String, nullable=False)
    risk_rating: Mapped[str] = mapped_column(String, nullable=False)
    potential_upside: Mapped[float | None] = mapped_column(Numeric(7, 3))
    label: Mapped[str] = mapped_column(String, nullable=False)
