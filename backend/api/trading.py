"""Trading endpoints — execute trades via CCXT on connected exchanges."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.security import get_current_user, decrypt_api_key
from backend.models.user import (
    User,
    ExchangeConnection,
    Trade,
    TradeSide,
    TradeStatus,
)
from backend.services.exchange.ccxt_client import CCXTClient

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class PlaceOrderRequest(BaseModel):
    connection_id: int
    symbol: str = Field(..., description="Trading pair, e.g. BTC/USDT")
    side: str = Field(..., description="buy or sell")
    amount: float = Field(..., gt=0, description="Quantity to trade")
    order_type: str = Field(default="market", description="market or limit")
    price: float | None = Field(default=None, description="Limit price (required for limit orders)")
    stop_loss: float | None = None
    take_profit: float | None = None
    strategy_used: str | None = None


class OrderOut(BaseModel):
    trade_id: int
    order_id: str | None
    symbol: str
    side: str
    status: str
    filled_price: float | None
    amount: float


class BalanceOut(BaseModel):
    asset: str
    free: float


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _get_exchange_connection(
    db: AsyncSession, user_id: int, connection_id: int
) -> ExchangeConnection:
    result = await db.execute(
        select(ExchangeConnection).where(
            ExchangeConnection.id == connection_id,
            ExchangeConnection.user_id == user_id,
            ExchangeConnection.is_active == True,
        )
    )
    conn = result.scalar_one_or_none()
    if conn is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange connection not found or inactive",
        )
    return conn


def _build_client(conn: ExchangeConnection) -> CCXTClient:
    return CCXTClient(
        exchange_name=conn.exchange.value if hasattr(conn.exchange, "value") else conn.exchange,
        api_key=decrypt_api_key(conn.api_key_encrypted),
        api_secret=decrypt_api_key(conn.api_secret_encrypted),
        testnet=conn.is_testnet,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post("/order", response_model=OrderOut)
async def place_order(
    payload: PlaceOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Place a market or limit order on the connected exchange."""
    conn = await _get_exchange_connection(db, current_user.id, payload.connection_id)
    client = _build_client(conn)

    try:
        if payload.order_type == "market":
            if payload.side == "buy":
                order = await client.create_market_buy(payload.symbol, payload.amount)
            else:
                order = await client.create_market_sell(payload.symbol, payload.amount)
        elif payload.order_type == "limit":
            if payload.price is None:
                raise HTTPException(status_code=400, detail="Limit orders require a price")
            if payload.side == "buy":
                order = await client.create_limit_buy(payload.symbol, payload.amount, payload.price)
            else:
                order = await client.create_limit_sell(payload.symbol, payload.amount, payload.price)
        else:
            raise HTTPException(status_code=400, detail="order_type must be 'market' or 'limit'")

        trade = Trade(
            user_id=current_user.id,
            exchange=conn.exchange,
            symbol=payload.symbol,
            side=TradeSide.BUY if payload.side == "buy" else TradeSide.SELL,
            status=TradeStatus.OPEN,
            entry_price=order.get("average") or order.get("price"),
            quantity=payload.amount,
            stop_loss=payload.stop_loss,
            take_profit=payload.take_profit,
            strategy_used=payload.strategy_used,
            opened_at=datetime.now(timezone.utc),
        )
        db.add(trade)
        await db.commit()
        await db.refresh(trade)

        return OrderOut(
            trade_id=trade.id,
            order_id=order.get("id"),
            symbol=payload.symbol,
            side=payload.side,
            status="open",
            filled_price=order.get("average") or order.get("price"),
            amount=payload.amount,
        )
    finally:
        await client.close()


@router.get("/balance", response_model=list[BalanceOut])
async def get_balance(
    connection_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch non-zero balances from a connected exchange."""
    conn = await _get_exchange_connection(db, current_user.id, connection_id)
    client = _build_client(conn)

    try:
        free = await client.fetch_free_balance()
        return [BalanceOut(asset=k, free=v) for k, v in free.items()]
    finally:
        await client.close()


@router.get("/ohlcv")
async def get_exchange_ohlcv(
    connection_id: int,
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch OHLCV candles directly from an exchange via CCXT."""
    conn = await _get_exchange_connection(db, current_user.id, connection_id)
    client = _build_client(conn)

    try:
        candles = await client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = client.ohlcv_to_dataframe(candles)
        return [
            {
                "timestamp": str(idx),
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": row["volume"],
            }
            for idx, row in df.iterrows()
        ]
    finally:
        await client.close()
