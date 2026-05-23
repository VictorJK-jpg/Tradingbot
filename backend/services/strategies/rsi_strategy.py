"""RSI mean-reversion strategy — buy oversold, sell overbought.

Parameters:
    oversold_threshold:  RSI below this → BUY signal  (default 30)
    overbought_threshold: RSI above this → SELL signal (default 70)
    rsi_length:          lookback period for RSI       (default 14)
    stop_loss_pct:       stop-loss as % below entry    (default 3%)
    take_profit_pct:     take-profit as % above entry  (default 6%)
"""

import pandas as pd

from backend.services.market.indicators import add_rsi
from backend.services.strategies.base import BaseStrategy, Signal, SignalType


class RSIStrategy(BaseStrategy):
    name = "rsi_mean_reversion"

    def __init__(
        self,
        oversold_threshold: float = 30.0,
        overbought_threshold: float = 70.0,
        rsi_length: int = 14,
        stop_loss_pct: float = 3.0,
        take_profit_pct: float = 6.0,
    ) -> None:
        self.oversold = oversold_threshold
        self.overbought = overbought_threshold
        self.rsi_length = rsi_length
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

    async def evaluate(self, symbol: str, df: pd.DataFrame, **kwargs) -> Signal:
        if "rsi" not in df.columns:
            df = add_rsi(df, length=self.rsi_length)

        latest = df.iloc[-1]
        rsi_val = latest["rsi"]
        price = latest["close"]

        if pd.isna(rsi_val):
            return Signal(
                signal_type=SignalType.HOLD,
                symbol=symbol,
                price=float(price),
                reason=f"RSI not yet available (need {self.rsi_length}+ candles)",
                strategy_name=self.name,
            )

        if rsi_val < self.oversold:
            sl = price * (1 - self.stop_loss_pct / 100)
            tp = price * (1 + self.take_profit_pct / 100)
            return Signal(
                signal_type=SignalType.BUY,
                symbol=symbol,
                price=float(price),
                reason=f"RSI {rsi_val:.1f} < {self.oversold} (oversold)",
                strategy_name=self.name,
                confidence=min((self.oversold - rsi_val) / self.oversold, 1.0),
                stop_loss=float(sl),
                take_profit=float(tp),
            )

        if rsi_val > self.overbought:
            return Signal(
                signal_type=SignalType.SELL,
                symbol=symbol,
                price=float(price),
                reason=f"RSI {rsi_val:.1f} > {self.overbought} (overbought)",
                strategy_name=self.name,
                confidence=min((rsi_val - self.overbought) / (100 - self.overbought), 1.0),
            )

        return Signal(
            signal_type=SignalType.HOLD,
            symbol=symbol,
            price=float(price),
            reason=f"RSI {rsi_val:.1f} — neutral zone ({self.oversold}-{self.overbought})",
            strategy_name=self.name,
        )
