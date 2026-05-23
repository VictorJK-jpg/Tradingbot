"""CoinGecko market data client (free API — no key required for basic endpoints).

Provides current prices, OHLC candles, and market overview data.
Rate-limited to ~10-30 req/min on the free tier.
"""

from datetime import datetime, timezone
from typing import Any

import httpx

_BASE = "https://api.coingecko.com/api/v3"
_TIMEOUT = 15.0


class CoinGeckoClient:
    """Async wrapper around CoinGecko's free REST API."""

    def __init__(self, api_key: str | None = None) -> None:
        headers: dict[str, str] = {"accept": "application/json"}
        if api_key:
            headers["x-cg-demo-key"] = api_key
        self._headers = headers

    # ------------------------------------------------------------------
    # Price
    # ------------------------------------------------------------------
    async def get_price(
        self,
        coin_ids: list[str],
        vs_currency: str = "usd",
    ) -> dict[str, dict[str, float]]:
        """Return current prices for one or more coins.

        Example return: {"bitcoin": {"usd": 65000.0, "usd_24h_change": 1.23}}
        """
        params = {
            "ids": ",".join(coin_ids),
            "vs_currencies": vs_currency,
            "include_24hr_change": "true",
            "include_market_cap": "true",
            "include_24hr_vol": "true",
        }
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(
                f"{_BASE}/simple/price",
                params=params,
                headers=self._headers,
            )
            resp.raise_for_status()
            return resp.json()

    # ------------------------------------------------------------------
    # OHLC candles (for technical analysis)
    # ------------------------------------------------------------------
    async def get_ohlc(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: int = 30,
    ) -> list[list[float]]:
        """Return OHLC candles.

        Each candle: [timestamp_ms, open, high, low, close]
        days: 1, 7, 14, 30, 90, 180, 365, max
        """
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(
                f"{_BASE}/coins/{coin_id}/ohlc",
                params={"vs_currency": vs_currency, "days": str(days)},
                headers=self._headers,
            )
            resp.raise_for_status()
            return resp.json()

    # ------------------------------------------------------------------
    # Market chart (granular price + volume history)
    # ------------------------------------------------------------------
    async def get_market_chart(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: int = 30,
    ) -> dict[str, list[list[float]]]:
        """Return price, market_cap, and volume time series.

        Returns {"prices": [[ts, val], ...], "market_caps": [...], "total_volumes": [...]}
        """
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(
                f"{_BASE}/coins/{coin_id}/market_chart",
                params={"vs_currency": vs_currency, "days": str(days)},
                headers=self._headers,
            )
            resp.raise_for_status()
            return resp.json()

    # ------------------------------------------------------------------
    # Top coins by market cap
    # ------------------------------------------------------------------
    async def get_top_coins(
        self,
        vs_currency: str = "usd",
        per_page: int = 20,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """Return top coins sorted by market cap."""
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(
                f"{_BASE}/coins/markets",
                params={
                    "vs_currency": vs_currency,
                    "order": "market_cap_desc",
                    "per_page": str(per_page),
                    "page": str(page),
                    "sparkline": "false",
                },
                headers=self._headers,
            )
            resp.raise_for_status()
            return resp.json()

    # ------------------------------------------------------------------
    # Coin detail
    # ------------------------------------------------------------------
    async def get_coin_detail(self, coin_id: str) -> dict[str, Any]:
        """Return full coin metadata (description, links, etc)."""
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(
                f"{_BASE}/coins/{coin_id}",
                params={
                    "localization": "false",
                    "tickers": "false",
                    "community_data": "false",
                    "developer_data": "false",
                },
                headers=self._headers,
            )
            resp.raise_for_status()
            return resp.json()

    # ------------------------------------------------------------------
    # Helper: OHLC → pandas DataFrame
    # ------------------------------------------------------------------
    def ohlc_to_dataframe(self, candles: list[list[float]]):
        """Convert raw OHLC list to a pandas DataFrame."""
        import pandas as pd

        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df.set_index("timestamp", inplace=True)
        return df
