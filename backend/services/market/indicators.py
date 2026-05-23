"""Technical indicators powered by the `ta` library.

Wraps the `ta` (Technical Analysis) library to provide a clean interface
for the strategy engine.  Works on Python 3.8+ (unlike pandas-ta which
requires 3.12+).

All functions expect a pandas DataFrame with OHLC columns.
"""

import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator, SMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange


def add_rsi(df: pd.DataFrame, length: int = 14, column: str = "close") -> pd.DataFrame:
    """Add RSI column to DataFrame."""
    df["rsi"] = RSIIndicator(close=df[column], window=length).rsi()
    return df


def add_macd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    column: str = "close",
) -> pd.DataFrame:
    """Add MACD, MACD signal, and MACD histogram columns."""
    macd = MACD(close=df[column], window_fast=fast, window_slow=slow, window_sign=signal)
    df["MACD_12_26_9"] = macd.macd()
    df["MACDs_12_26_9"] = macd.macd_signal()
    df["MACDh_12_26_9"] = macd.macd_diff()
    return df


def add_bollinger_bands(
    df: pd.DataFrame,
    length: int = 20,
    std: float = 2.0,
    column: str = "close",
) -> pd.DataFrame:
    """Add Bollinger Bands (lower, mid, upper)."""
    bb = BollingerBands(close=df[column], window=length, window_dev=std)
    df["BBL_20_2.0"] = bb.bollinger_lband()
    df["BBM_20_2.0"] = bb.bollinger_mavg()
    df["BBU_20_2.0"] = bb.bollinger_hband()
    return df


def add_ema(df: pd.DataFrame, length: int = 20, column: str = "close") -> pd.DataFrame:
    """Add Exponential Moving Average."""
    df[f"ema_{length}"] = EMAIndicator(close=df[column], window=length).ema_indicator()
    return df


def add_sma(df: pd.DataFrame, length: int = 20, column: str = "close") -> pd.DataFrame:
    """Add Simple Moving Average."""
    df[f"sma_{length}"] = SMAIndicator(close=df[column], window=length).sma_indicator()
    return df


def add_atr(df: pd.DataFrame, length: int = 14) -> pd.DataFrame:
    """Add Average True Range (requires high, low, close)."""
    df["atr"] = AverageTrueRange(
        high=df["high"], low=df["low"], close=df["close"], window=length
    ).average_true_range()
    return df


def add_volume_sma(df: pd.DataFrame, length: int = 20) -> pd.DataFrame:
    """Add volume SMA (requires 'volume' column)."""
    if "volume" in df.columns:
        df[f"volume_sma_{length}"] = SMAIndicator(close=df["volume"], window=length).sma_indicator()
    return df


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add a standard set of indicators for strategy evaluation."""
    df = add_rsi(df)
    df = add_macd(df)
    df = add_bollinger_bands(df)
    df = add_ema(df, length=9)
    df = add_ema(df, length=21)
    df = add_sma(df, length=50)
    df = add_atr(df)
    return df
