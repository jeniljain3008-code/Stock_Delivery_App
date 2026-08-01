"""
==========================================================
Trading Engine Models
==========================================================

These models are INTERNAL to the Trading Engine.

Database Models
↓

Analytics

↓

Trading Models

↓

API Schemas

==========================================================
"""

from dataclasses import dataclass
from datetime import date


# ---------------------------------------------------------
# Ultra Signal
# ---------------------------------------------------------

@dataclass(slots=True)
class TradeSignal:

    symbol: str

    signal_date: date

    close: float

    high: float

    delivery_percent: float

    surge_5d: float

    surge_10d: float

    surge_30d: float

    explosion_score: float

    accumulation_score: float

    breakout_score: float

    swing_rank: float

    swing_signal: str

    risk_rating: str


# ---------------------------------------------------------
# Near Breakout
# ---------------------------------------------------------

@dataclass(slots=True)
class NearBreakout:

    symbol: str

    signal_high: float

    current_close: float

    distance_pct: float

    swing_rank: float

    accumulation_score: float

    breakout_score: float


# ---------------------------------------------------------
# Pilot Entry
# ---------------------------------------------------------

@dataclass(slots=True)
class PilotEntry:

    symbol: str

    entry_score: float

    suggested_allocation: float

    signal_strength: str


# ---------------------------------------------------------
# Active Position
# ---------------------------------------------------------

@dataclass(slots=True)
class TradePosition:

    symbol: str

    signal_date: date

    breakout_date: date

    entry_price: float

    current_price: float

    highest_close: float

    return_pct: float

    days_active: int

    status: str


# ---------------------------------------------------------
# Strategy Statistics
# ---------------------------------------------------------

@dataclass(slots=True)
class StrategyStatistics:

    total_signals: int

    total_breakouts: int

    total_open_trades: int

    total_closed_trades: int

    win_rate: float

    average_return: float

    average_holding_days: float

    best_trade: float

    worst_trade: float
