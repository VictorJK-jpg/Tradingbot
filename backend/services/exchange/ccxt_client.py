"""CCXT exchange client — unified interface to Binance (testnet-first).

Wraps ccxt's async API for placing orders, fetching balances, and reading OHLCV.
All exchange API keys are decrypted on demand via security.decrypt_api_key().
"""

from typing import Any

import ccxt.async_support as ccxt

from backend.core.config import settings


_EXCHANGE_CLASSES: dict[str, type] = {
    "binance": ccxt.binance,
    "bybit": ccxt.bybit,
    "coinbase": ccxt.coinbase,
    "kraken": ccxt.kraken,
}


class CCXTClient:
    """Async wrapper around a ccxt exchange instance."""

    def __init__(
        self,
        exchange_name: str,
        api_key: str,
        api_secret: str,
        testnet: bool = True,
    ) -> None:
        cls = _EXCHANGE_CLASSES.get(exchange_name)
        if cls is None:
            raise ValueError(f"Unsupported exchange: {exchange_name}")

        opts: dict[str, Any] = {
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": True,
        }

        if testnet:
            opts["sandbox"] = True

        self._exchange: ccxt.Exchange = cls(opts)
        self._exchange_name = exchange_name

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    async def close(self) -> None:
        await self._exchange.close()

    # ------------------------------------------------------------------
    # Balance
    # ------------------------------------------------------------------
    async def fetch_balance(self) -> dict[str, Any]:
        """Return full balance dict (free, used, total per asset)."""
        return await self._exchange.fetch_balance()

    async def fetch_free_balance(self) -> dict[str, float]:
        """Return only non-zero free balances."""
        bal = await self._exchange.fetch_balance()
        return {k: v for k, v in bal.get("free", {}).items() if v and v > 0}

    # ------------------------------------------------------------------
    # OHLCV
    # ------------------------------------------------------------------
    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 100,
    ) -> list[list]:
        """Return OHLCV candles: [[timestamp, O, H, L, C, V], ...]."""
        return await self._exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    def ohlcv_to_dataframe(self, candles: list[list]):
        """Convert OHLCV list to pandas DataFrame."""
        import pandas as pd

        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df.set_index("timestamp", inplace=True)
        return df

    # ------------------------------------------------------------------
    # Orders
    # ------------------------------------------------------------------
    async def create_market_buy(self, symbol: str, amount: float) -> dict[str, Any]:
        """Place a market buy order."""
        return await self._exchange.create_market_buy_order(symbol, amount)

    async def create_market_sell(self, symbol: str, amount: float) -> dict[str, Any]:
        """Place a market sell order."""
        return await self._exchange.create_market_sell_order(symbol, amount)

    async def create_limit_buy(self, symbol: str, amount: float, price: float) -> dict[str, Any]:
        """Place a limit buy order."""
        return await self._exchange.create_limit_buy_order(symbol, amount, price)

    async def create_limit_sell(self, symbol: str, amount: float, price: float) -> dict[str, Any]:
        """Place a limit sell order."""
        return await self._exchange.create_limit_sell_order(symbol, amount, price)

    # ------------------------------------------------------------------
    # Order management
    # ------------------------------------------------------------------
    async def fetch_open_orders(self, symbol: str | None = None) -> list[dict[str, Any]]:
        return await self._exchange.fetch_open_orders(symbol)

    async def cancel_order(self, order_id: str, symbol: str) -> dict[str, Any]:
        return await self._exchange.cancel_order(order_id, symbol)

    # ------------------------------------------------------------------
    # Ticker
    # ------------------------------------------------------------------
    async def fetch_ticker(self, symbol: str) -> dict[str, Any]:
        """Return current ticker (last price, bid, ask, volume, etc)."""
        return await self._exchange.fetch_ticker(symbol)

    async def fetch_tickers(self, symbols: list[str] | None = None) -> dict[str, dict[str, Any]]:
        """Return tickers for multiple symbols."""
        return await self._exchange.fetch_tickers(symbols)
