---
title: Trend-Following Strategy
description: Ride established directional momentum. Enter on pullbacks to the dominant trend.
tags: [strategy, momentum, technical, swing-trading]
author: crypto-platform
version: 1.0.0
---

## Overview
Ride established directional momentum. Enter on pullbacks to the dominant trend, not breakouts.

## Core Rules
1. **Trend definition**: Price above 20 EMA and 20 EMA above 50 EMA = uptrend. Inverse for downtrend.
2. **Entry**: Wait for a retracement to the 20 EMA or a prior support/resistance flip zone.
3. **Stop loss**: Below the swing low that preceded the entry candle (or 2× ATR for volatility-adjusted).
4. **Take profit**: Partial at 1.5 R, runner to 3 R or trailing 20 EMA.
5. **Timeframe**: 4H for signal, 1H for precise entry.

## Filters — Do NOT Enter If
- ADX < 20 (no trend strength)
- RSI > 75 on longs or < 25 on shorts (overextended)
- Major macro event within 4 hours (NFP, CPI, FOMC)

## Crypto-Specific Notes
- Use funding-rate heatmap: extreme positive funding = late longs, favour shorts.
- Breakouts on low weekend volume are fake 70% of the time; wait for Monday confirmation.
