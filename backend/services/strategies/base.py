"""Base class for all trading strategies."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

import pandas as pd


class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class Signal:
    signal_type: SignalType
    symbol: str
    price: float
    reason: str
    strategy_name: str
    confidence: float = 0.0  # 0-1
    stop_loss: float | None = None
    take_profit: float | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BaseStrategy(ABC):
    """All strategies implement this interface."""

    name: str = "base"

    @abstractmethod
    async def evaluate(self, symbol: str, df: pd.DataFrame, **kwargs) -> Signal:
        """Evaluate market data and return a trading signal."""
        ...
