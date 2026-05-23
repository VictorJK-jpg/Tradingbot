"""Strategy evaluation endpoints — RSI, DCA, SL/TP check."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from backend.core.config import settings
from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.user import User, Trade, TradeStatus
from backend.services.market.coingecko import CoinGeckoClient
from backend.services.market.indicators import add_all_indicators
from backend.services.strategies.rsi_strategy import RSIStrategy
from backend.services.strategies.dca_strategy import DCAStrategy
from backend.services.strategies.sl_tp_engine import SLTPEngine, OpenPosition

router = APIRouter()
_cg = CoinGeckoClient(api_key=settings.COINGECKO_API_KEY)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class SignalOut(BaseModel):
    signal_type: str
    symbol: str
    price: float
    reason: str
    strategy_name: str
    confidence: float
    stop_loss: float | None = None
    take_profit: float | None = None


class SLTPCheckOut(BaseModel):
    triggered: list[SignalOut]
    checked_count: int


# ---------------------------------------------------------------------------
# RSI evaluation
# ---------------------------------------------------------------------------
@router.get("/rsi/evaluate", response_model=SignalOut)
async def evaluate_rsi(
    coin_id: str = Query("bitcoin"),
    symbol: str = Query("BTC/USDT"),
    oversold: float = Query(30.0),
    overbought: float = Query(70.0),
    current_user: User = Depends(get_current_user),
):
    """Evaluate RSI strategy for a given coin. Returns BUY/SELL/HOLD signal."""
    try:
        candles = await _cg.get_ohlc(coin_id, days=14)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    df = _cg.ohlc_to_dataframe(candles)

    strategy = RSIStrategy(
        oversold_threshold=oversold,
        overbought_threshold=overbought,
    )
    signal = await strategy.evaluate(symbol, df)
    return SignalOut(
        signal_type=signal.signal_type.value,
        symbol=signal.symbol,
        price=signal.price,
        reason=signal.reason,
        strategy_name=signal.strategy_name,
        confidence=signal.confidence,
        stop_loss=signal.stop_loss,
        take_profit=signal.take_profit,
    )


# ---------------------------------------------------------------------------
# DCA evaluation
# ---------------------------------------------------------------------------
@router.get("/dca/evaluate", response_model=SignalOut)
async def evaluate_dca(
    coin_id: str = Query("bitcoin"),
    symbol: str = Query("BTC/USDT"),
    buy_amount_usd: float = Query(50.0),
    current_user: User = Depends(get_current_user),
):
    """Evaluate DCA strategy — should we buy now or skip (overbought)?"""
    try:
        candles = await _cg.get_ohlc(coin_id, days=14)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    df = _cg.ohlc_to_dataframe(candles)

    strategy = DCAStrategy(buy_amount_usd=buy_amount_usd)
    signal = await strategy.evaluate(symbol, df)
    return SignalOut(
        signal_type=signal.signal_type.value,
        symbol=signal.symbol,
        price=signal.price,
        reason=signal.reason,
        strategy_name=signal.strategy_name,
        confidence=signal.confidence,
        stop_loss=signal.stop_loss,
        take_profit=signal.take_profit,
    )


# ---------------------------------------------------------------------------
# SL/TP check on open trades
# ---------------------------------------------------------------------------
@router.get("/sltp/check", response_model=SLTPCheckOut)
async def check_sltp(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check all open trades for SL/TP triggers."""
    result = await db.execute(
        select(Trade).where(
            Trade.user_id == current_user.id,
            Trade.status == TradeStatus.OPEN,
        )
    )
    trades = result.scalars().all()

    if not trades:
        return SLTPCheckOut(triggered=[], checked_count=0)

    positions = []
    coin_ids = set()
    symbol_to_coin: dict[str, str] = {}
    for t in trades:
        if t.entry_price is None:
            continue
        positions.append(OpenPosition(
            symbol=t.symbol,
            entry_price=float(t.entry_price),
            quantity=float(t.quantity),
            stop_loss=float(t.stop_loss) if t.stop_loss else None,
            take_profit=float(t.take_profit) if t.take_profit else None,
            trade_id=t.id,
        ))
        coin_id = t.symbol.split("/")[0].lower()
        coin_ids.add(coin_id)
        symbol_to_coin[t.symbol] = coin_id

    if not positions:
        return SLTPCheckOut(triggered=[], checked_count=0)

    price_data = await _cg.get_price(list(coin_ids))
    prices: dict[str, float] = {}
    for sym, cid in symbol_to_coin.items():
        if cid in price_data and "usd" in price_data[cid]:
            prices[sym] = price_data[cid]["usd"]

    signals = SLTPEngine.check_all(positions, prices)
    return SLTPCheckOut(
        triggered=[
            SignalOut(
                signal_type=s.signal_type.value,
                symbol=s.symbol,
                price=s.price,
                reason=s.reason,
                strategy_name=s.strategy_name,
                confidence=s.confidence,
            )
            for s in signals
        ],
        checked_count=len(positions),
    )
