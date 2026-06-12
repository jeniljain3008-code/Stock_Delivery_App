from datetime import date

from pydantic import BaseModel, Field

class NSELoadRequest(BaseModel):
    trade_date: str
    
class NSEFetchRequest(BaseModel):
    trade_date: str

class NSEFetchResponse(BaseModel):
    status: str
    rows: int
    data: list[dict]

class KPI(BaseModel):
    label: str
    value: str | int | float
    change: float | None = None

class StockRow(BaseModel):
    symbol: str
    close: float

    sector: str | None = None
    market_cap: str | None = None

    delivery_surge: float
    delivery_percent: float | None = None

    surge_5d: float = 0
    surge_10d: float = 0
    surge_30d: float = 0

    explosion_score: float = 0

    accumulation_score: float
    breakout_score: float

    risk_rating: str
    swing_signal: str
    swing_rank_score: float | None = 0
    entry_price: float | None = None
    current_price: float | None = None
    return_pct: float | None = None
    days_active: int | None = None
    breakout_date: str | None = None
    
class DashboardSummary(BaseModel):
    kpis: list[KPI]

    top_delivery_surge: list[StockRow]
    top_breakouts: list[StockRow]

    exploded_stocks: list[StockRow]
    exploded_elite: list[StockRow]
    exploded_ultra: list[StockRow]
    breakout_entries: list[StockRow]
    ultra_breakout_tracker: list[
        UltraBreakoutTrackerRow
    ]
    ready_to_explode: list[StockRow]
    preparing_to_explode: list[StockRow]

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
    
class ExplosionBacktestRequest(BaseModel):
    days: int = 365

class UltraBreakoutTrackerRow(BaseModel):

    symbol: str

    breakout_date: str

    entry_price: float

    current_price: float

    return_pct: float

    days_active: int

    swing_rank_score: float
