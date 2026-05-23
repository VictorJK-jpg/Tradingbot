"""Dollar-Cost Averaging (DCA) strategy.

Buys a fixed USD amount on a regular schedule regardless of price.
Optional: skip a buy if RSI is overbought (smart DCA).

Parameters:
    buy_amount_usd:    fixed USD to spend per interval (default $50)
    skip_overbought:   skip buy when RSI > threshold   (default True)
    overbought_rsi:    RSI threshold to skip            (default 75)
"""

import pandas as pd

from backend.services.market.indicators import add_rsi
from backend.services.strategies.base import BaseStrategy, Signal, SignalType


class DCAStrategy(BaseStrategy):
    name = "dca"

    def __init__(
        self,
        buy_amount_usd: float = 50.0,
        skip_overbought: bool = True,
        overbought_rsi: float = 75.0,
        rsi_length: int = 14,
    ) -> None:
        self.buy_amount_usd = buy_amount_usd
        self.skip_overbought = skip_overbought
        self.overbought_rsi = overbought_rsi
        self.rsi_length = rsi_length

    async def evaluate(self, symbol: str, df: pd.DataFrame, **kwargs) -> Signal:
        if "rsi" not in df.columns:
            df = add_rsi(df, length=self.rsi_length)

        latest = df.iloc[-1]
        price = latest["close"]
        rsi_val = latest.get("rsi")

        if self.skip_overbought and rsi_val is not None and not pd.isna(rsi_val):
            if rsi_val > self.overbought_rsi:
                return Signal(
                    signal_type=SignalType.HOLD,
                    symbol=symbol,
                    price=float(price),
                    reason=f"DCA skipped — RSI {rsi_val:.1f} > {self.overbought_rsi} (overbought)",
                    strategy_name=self.name,
                )

        quantity = self.buy_amount_usd / float(price)
        return Signal(
            signal_type=SignalType.BUY,
            symbol=symbol,
            price=float(price),
            reason=f"DCA buy ${self.buy_amount_usd:.2f} → {quantity:.8f} {symbol}",
            strategy_name=self.name,
            confidence=1.0,
        )
