---
title: Position Sizing & Risk-per-Trade
description: The 1% rule, leverage guidelines, and daily drawdown limits.
tags: [risk, position-sizing, leverage, drawdown]
author: crypto-platform
version: 1.0.0
---

## The 1% Rule
Never risk more than **1% of total account equity** on a single trade.

## Formula
```
Position Size = (Account Equity × Risk %) / (Entry − Stop Loss)
```

## Examples
- **Account**: $10,000
- **Risk**: 1% = $100
- **Entry**: $50,000
- **Stop**: $48,500 (3% below entry)
- **Position Size** = $100 / $1,500 = 0.0667 BTC ≈ $3,333 notional

## Leverage Guidelines
| Volatility (14D ATR) | Max Leverage |
|-----------------------|-------------|
| < 2%                  | 5×          |
| 2% – 5%               | 3×          |
| > 5%                  | 1× (spot)   |

## Correlation Risk
If two positions share > 0.7 correlation (e.g. BTC and ETH), treat them as **one trade** for sizing.

## Daily Loss Limit
- Hard stop at **3% daily drawdown**. Close all positions, no new trades until next session.
- Soft warning at 2% — reduce position sizes by 50%.
