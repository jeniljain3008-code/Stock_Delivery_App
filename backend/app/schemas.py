from datetime import date

from pydantic import BaseModel, Field


class KPI(BaseModel):
    label: str
    value: str | int | float
    change: float | None = None


class StockRow(BaseModel):
    symbol: str
    close: float
    sector: str | None = None
    market_cap: str | None = None
    delivery_surge: float = Field(description="Current delivery / historical average")
    accumulation_score: float
    breakout_score: float
    risk_rating: str
    swing_signal: str


class DashboardSummary(BaseModel):
    kpis: list[KPI]
    top_delivery_surge: list[StockRow]
    top_breakouts: list[StockRow]
    sector_leaders: list[dict]
    market_summary: str


class GoldStock(BaseModel):
    symbol: str
    price: float
    delivery_surge: float
    accumulation_score: float
    risk_rating: str
    potential_upside: float


class AIQuestion(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    symbol: str | None = None


class AIAnswer(BaseModel):
    answer: str
    supporting_symbols: list[str] = []


class BacktestRequest(BaseModel):
    strategy: str = Field(pattern="^(delivery|moving_average|breakout)$")
    start_date: date
    end_date: date
    min_accumulation_score: float = 70


class BacktestResult(BaseModel):
    win_rate: float
    cagr: float
    profit_factor: float
    max_drawdown: float
    sharpe_ratio: float
    trade_log: list[dict]
