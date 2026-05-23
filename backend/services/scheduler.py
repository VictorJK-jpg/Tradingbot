"""APScheduler service — runs strategies on intervals.

Manages scheduled jobs for:
  - RSI strategy checks (every 15 min)
  - DCA buys (configurable interval)
  - SL/TP monitoring (every 1 min)
"""

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.services.market.coingecko import CoinGeckoClient
from backend.services.market.indicators import add_rsi, add_all_indicators
from backend.services.strategies.rsi_strategy import RSIStrategy
from backend.services.strategies.dca_strategy import DCAStrategy
from backend.services.strategies.sl_tp_engine import SLTPEngine, OpenPosition
from backend.services.strategies.base import SignalType

logger = logging.getLogger("scheduler")

_scheduler: AsyncIOScheduler | None = None
_coingecko = CoinGeckoClient()


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="UTC")
    return _scheduler


# ---------------------------------------------------------------------------
# RSI job
# ---------------------------------------------------------------------------
async def rsi_check_job(
    coin_id: str = "bitcoin",
    symbol: str = "BTC/USDT",
) -> None:
    """Fetch OHLC data and evaluate RSI strategy."""
    try:
        candles = await _coingecko.get_ohlc(coin_id, days=14)
        if not candles:
            logger.warning("No OHLC data for %s", coin_id)
            return

        df = _coingecko.ohlc_to_dataframe(candles)
        strategy = RSIStrategy()
        signal = await strategy.evaluate(symbol, df)
        logger.info("[RSI] %s → %s: %s", symbol, signal.signal_type.value, signal.reason)
    except Exception:
        logger.exception("RSI check failed for %s", coin_id)


# ---------------------------------------------------------------------------
# DCA job
# ---------------------------------------------------------------------------
async def dca_check_job(
    coin_id: str = "bitcoin",
    symbol: str = "BTC/USDT",
    buy_amount_usd: float = 50.0,
) -> None:
    """Evaluate whether to execute a DCA buy."""
    try:
        candles = await _coingecko.get_ohlc(coin_id, days=14)
        if not candles:
            logger.warning("No OHLC data for %s", coin_id)
            return

        df = _coingecko.ohlc_to_dataframe(candles)
        strategy = DCAStrategy(buy_amount_usd=buy_amount_usd)
        signal = await strategy.evaluate(symbol, df)
        logger.info("[DCA] %s → %s: %s", symbol, signal.signal_type.value, signal.reason)
    except Exception:
        logger.exception("DCA check failed for %s", coin_id)


# ---------------------------------------------------------------------------
# SL/TP monitoring job
# ---------------------------------------------------------------------------
async def sltp_monitor_job(
    positions: list[OpenPosition] | None = None,
) -> None:
    """Check open positions against current prices for SL/TP triggers."""
    if not positions:
        return
    try:
        symbols = list({p.symbol for p in positions})
        coin_ids = [s.split("/")[0].lower() for s in symbols]
        price_data = await _coingecko.get_price(coin_ids)

        prices: dict[str, float] = {}
        for sym in symbols:
            coin_id = sym.split("/")[0].lower()
            if coin_id in price_data and "usd" in price_data[coin_id]:
                prices[sym] = price_data[coin_id]["usd"]

        signals = SLTPEngine.check_all(positions, prices)
        for sig in signals:
            logger.info("[SL/TP] %s → %s: %s", sig.symbol, sig.signal_type.value, sig.reason)
    except Exception:
        logger.exception("SL/TP monitor failed")


# ---------------------------------------------------------------------------
# Scheduler lifecycle
# ---------------------------------------------------------------------------
def start_scheduler() -> AsyncIOScheduler:
    """Start the scheduler with default jobs."""
    scheduler = get_scheduler()
    if scheduler.running:
        return scheduler

    scheduler.add_job(
        rsi_check_job,
        trigger=IntervalTrigger(minutes=15),
        id="rsi_btc_15m",
        name="RSI check BTC every 15min",
        replace_existing=True,
    )

    scheduler.add_job(
        dca_check_job,
        trigger=IntervalTrigger(hours=24),
        id="dca_btc_daily",
        name="DCA BTC daily",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with %d jobs", len(scheduler.get_jobs()))
    return scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
    _scheduler = None
