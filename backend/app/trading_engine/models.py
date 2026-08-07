"""
==========================================================
Trading Engine Models
==========================================================

Everything inside Trading Engine revolves around ONE object.

Trade

Each engine updates the Trade.

Signal Engine

↓

Entry Engine

↓

Ranking Engine

↓

Trade Manager

↓

Statistics

==========================================================
"""

from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class Trade:

    # -------------------------------------------------
    # Identity
    # -------------------------------------------------

    symbol: str

    signal_date: date

    # -------------------------------------------------
    # Prices
    # -------------------------------------------------

    close: float

    high: float

    signal_high: float

    entry_price: float = 0

    current_price: float = 0

    highest_close: float = 0

    exit_price: float = 0

    # -------------------------------------------------
    # Analytics
    # -------------------------------------------------

    delivery_percent: float = 0

    surge_5d: float = 0

    surge_10d: float = 0

    surge_30d: float = 0

    explosion_score: float = 0

    accumulation_score: float = 0

    breakout_score: float = 0

    swing_rank: float = 0

    volume_ratio: float = 0

    distance_to_breakout: float = 0

    conviction_score: float = 0

    entry_score: float = 0

    # -------------------------------------------------
    # Position
    # -------------------------------------------------

    allocation: float = 0

    quantity: int = 0

    # -------------------------------------------------
    # Performance
    # -------------------------------------------------

    return_pct: float = 0

    max_return_pct: float = 0

    days_active: int = 0

    # -------------------------------------------------
    # Status
    # -------------------------------------------------

    status: str = "SIGNAL"

    action: str = "WATCH"

    stars: str = "★"

    risk_rating: str = "LOW"
