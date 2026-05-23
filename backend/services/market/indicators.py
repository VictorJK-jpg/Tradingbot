"""Technical indicators powered by pandas-ta.

Wraps pandas-ta to provide a clean interface for the strategy engine.
All functions expect a pandas DataFrame with OHLC columns.
"""

import pandas as pd
import pandas_ta as ta


def add_rsi(df: pd.DataFrame, length: int = 14, column: str = "close") -> pd.DataFrame:
    """Add RSI column to DataFrame."""
    df["rsi"] = ta.rsi(df[column], length=length)
    return df


def add_macd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    column: str = "close",
) -> pd.DataFrame:
    """Add MACD, MACD signal, and MACD histogram columns."""
    macd = ta.macd(df[column], fast=fast, slow=slow, signal=signal)
    if macd is not None:
        df = pd.concat([df, macd], axis=1)
    return df


def add_bollinger_bands(
    df: pd.DataFrame,
    length: int = 20,
    std: float = 2.0,
    column: str = "close",
) -> pd.DataFrame:
    """Add Bollinger Bands (lower, mid, upper, bandwidth, percent)."""
    bbands = ta.bbands(df[column], length=length, std=std)
    if bbands is not None:
        df = pd.concat([df, bbands], axis=1)
    return df


def add_ema(df: pd.DataFrame, length: int = 20, column: str = "close") -> pd.DataFrame:
    """Add Exponential Moving Average."""
    df[f"ema_{length}"] = ta.ema(df[column], length=length)
    return df


def add_sma(df: pd.DataFrame, length: int = 20, column: str = "close") -> pd.DataFrame:
    """Add Simple Moving Average."""
    df[f"sma_{length}"] = ta.sma(df[column], length=length)
    return df


def add_atr(df: pd.DataFrame, length: int = 14) -> pd.DataFrame:
    """Add Average True Range (requires high, low, close)."""
    df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=length)
    return df


def add_volume_sma(df: pd.DataFrame, length: int = 20) -> pd.DataFrame:
    """Add volume SMA (requires 'volume' column)."""
    if "volume" in df.columns:
        df[f"volume_sma_{length}"] = ta.sma(df["volume"], length=length)
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
