"""Stop-loss / take-profit monitoring engine.

Checks open positions against current prices and fires SELL signals
when stop-loss or take-profit levels are hit.
"""

from dataclasses import dataclass
from datetime import datetime, timezone

from backend.services.strategies.base import Signal, SignalType


@dataclass
class OpenPosition:
    symbol: str
    entry_price: float
    quantity: float
    stop_loss: float | None = None
    take_profit: float | None = None
    trade_id: int | None = None


class SLTPEngine:
    """Evaluates open positions against current prices."""

    @staticmethod
    def check_position(position: OpenPosition, current_price: float) -> Signal | None:
        """Return a SELL signal if SL or TP is hit, else None."""
        if position.stop_loss and current_price <= position.stop_loss:
            pnl_pct = ((current_price - position.entry_price) / position.entry_price) * 100
            return Signal(
                signal_type=SignalType.SELL,
                symbol=position.symbol,
                price=current_price,
                reason=(
                    f"STOP-LOSS hit: price ${current_price:.2f} <= SL ${position.stop_loss:.2f} "
                    f"(entry ${position.entry_price:.2f}, PnL {pnl_pct:+.2f}%)"
                ),
                strategy_name="sl_tp_engine",
                confidence=1.0,
            )

        if position.take_profit and current_price >= position.take_profit:
            pnl_pct = ((current_price - position.entry_price) / position.entry_price) * 100
            return Signal(
                signal_type=SignalType.SELL,
                symbol=position.symbol,
                price=current_price,
                reason=(
                    f"TAKE-PROFIT hit: price ${current_price:.2f} >= TP ${position.take_profit:.2f} "
                    f"(entry ${position.entry_price:.2f}, PnL {pnl_pct:+.2f}%)"
                ),
                strategy_name="sl_tp_engine",
                confidence=1.0,
            )

        return None

    @staticmethod
    def check_all(
        positions: list[OpenPosition],
        prices: dict[str, float],
    ) -> list[Signal]:
        """Check a batch of positions. Returns list of triggered signals."""
        signals: list[Signal] = []
        for pos in positions:
            price = prices.get(pos.symbol)
            if price is None:
                continue
            sig = SLTPEngine.check_position(pos, price)
            if sig is not None:
                signals.append(sig)
        return signals
