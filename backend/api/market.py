"""Market data endpoints — prices, OHLC, indicators, top coins."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import httpx

from backend.core.config import settings
from backend.services.market.coingecko import CoinGeckoClient
from backend.services.market.indicators import add_all_indicators

router = APIRouter()

_cg = CoinGeckoClient(api_key=settings.COINGECKO_API_KEY)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class PriceOut(BaseModel):
    coin_id: str
    usd: float
    usd_24h_change: float | None = None
    usd_market_cap: float | None = None
    usd_24h_vol: float | None = None


class OHLCCandle(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float


class IndicatorRow(BaseModel):
    timestamp: str
    close: float
    rsi: float | None = None
    ema_9: float | None = None
    ema_21: float | None = None
    sma_50: float | None = None
    atr: float | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.get("/price", response_model=list[PriceOut])
async def get_prices(
    coin_ids: str = Query("bitcoin,ethereum", description="Comma-separated CoinGecko IDs"),
):
    """Get current prices for one or more coins."""
    ids = [c.strip() for c in coin_ids.split(",") if c.strip()]
    if not ids:
        raise HTTPException(status_code=400, detail="Provide at least one coin_id")

    try:
        data = await _cg.get_price(ids)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    result = []
    for cid in ids:
        if cid not in data:
            continue
        d = data[cid]
        result.append(PriceOut(
            coin_id=cid,
            usd=d.get("usd", 0),
            usd_24h_change=d.get("usd_24h_change"),
            usd_market_cap=d.get("usd_market_cap"),
            usd_24h_vol=d.get("usd_24h_vol"),
        ))
    return result


@router.get("/ohlc", response_model=list[OHLCCandle])
async def get_ohlc(
    coin_id: str = Query("bitcoin"),
    days: int = Query(30, ge=1, le=365),
):
    """Get OHLC candle data for a coin."""
    try:
        candles = await _cg.get_ohlc(coin_id, days=days)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    df = _cg.ohlc_to_dataframe(candles)
    return [
        OHLCCandle(
            timestamp=str(idx),
            open=row["open"],
            high=row["high"],
            low=row["low"],
            close=row["close"],
        )
        for idx, row in df.iterrows()
    ]


@router.get("/indicators", response_model=list[IndicatorRow])
async def get_indicators(
    coin_id: str = Query("bitcoin"),
    days: int = Query(30, ge=1, le=365),
):
    """Get OHLC data with technical indicators (RSI, MACD, EMA, etc)."""
    try:
        candles = await _cg.get_ohlc(coin_id, days=days)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    df = _cg.ohlc_to_dataframe(candles)
    df = add_all_indicators(df)

    def _safe(val):
        import math
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return None
        return val

    rows = []
    for idx, row in df.iterrows():
        rows.append(IndicatorRow(
            timestamp=str(idx),
            close=row["close"],
            rsi=_safe(row.get("rsi")),
            ema_9=_safe(row.get("ema_9")),
            ema_21=_safe(row.get("ema_21")),
            sma_50=_safe(row.get("sma_50")),
            atr=_safe(row.get("atr")),
        ))
    return rows


@router.get("/top")
async def get_top_coins(
    per_page: int = Query(20, ge=1, le=100),
):
    """Get top coins by market cap."""
    try:
        return await _cg.get_top_coins(per_page=per_page)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
