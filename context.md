You are my development partner helping me build a 
multi-tenant AI-powered crypto trading intelligence 
platform as a sideloaded native mobile app.

## What We're Building
A private AI trading intelligence app (APK for Android, 
TestFlight for iOS). Multi-tenant — I host everything, 
users install and go. No app store.

## The Core Concept — Decision Trinity
Every AI decision is powered by three sources:
1. Data APIs — quantitative (price, on-chain, macro)
2. Skills.md files — technical analysis framework (expert-curated by us)
3. External News — fundamental analysis (Cryptopanic, NewsAPI, RSS)

AI synthesizes all three against the user's personal 
profile and delivers a reasoned decision with full context.

## Full Tech Stack
- Mobile: React Native (Expo) + NativeWind + Victory Native charts
- State: Zustand
- Backend: FastAPI (Python 3.11+)
- AI Brain: Claude API (Sonnet) via Anthropic SDK
- Skills Engine: Markdown files server-side, AI loads relevant ones per request
- Exchange: CCXT (Binance/Bybit first)
- Indicators: pandas-ta
- Scheduler: APScheduler
- Price Data: CoinGecko + CCXT
- On-chain: DeFiLlama, Token Terminal, Glassnode (free tiers)
- Macro: FRED API, Alternative.me (Fear & Greed)
- News: Cryptopanic API + NewsAPI + RSS feeds
- Sentiment: LunarCrush
- Database: PostgreSQL + SQLAlchemy
- Cache: Redis
- Auth: JWT
- Notifications: Telegram bot (alerts only) + Expo Push
- Data Pipelines: n8n
- Hosting: Hetzner VPS
- Version Control: GitHub + GitHub Actions
- IDE: Windsurf

## Project Folder Structure
crypto-platform/
├── app/                        # React Native (Expo)
│   ├── screens/
│   ├── components/
│   ├── navigation/
│   ├── store/                  # Zustand
│   └── services/               # API calls
├── backend/                    # FastAPI
│   ├── api/                    # Routes
│   ├── core/                   # Config, auth, security
│   ├── models/                 # SQLAlchemy models
│   ├── services/               # Business logic
│   │   ├── ai/                 # Claude integration
│   │   ├── exchange/           # CCXT
│   │   ├── market/             # Data pipeline
│   │   ├── news/               # News pipeline
│   │   └── strategies/         # Strategy engine
│   └── skills/                 # All .md skill files
│       ├── strategies/
│       ├── risk_management/
│       ├── market_reading/
│       ├── fundamental/
│       └── weekly_outlook/
├── n8n/                        # Pipeline workflows
├── .env
├── requirements.txt
├── CONTEXT.md                  # This file, kept updated
└── docker-compose.yml

## Database Tables
Users, BotPersona, TraderProfile, PsychProfile,
ExchangeConnections, Trades, TradeJournal,
ConversationMemory, PriceAlerts, Goals, RiskBudget,
PerformanceStats, MissedOpportunities, EmotionalLog,
MacroEvents, NewsCache, SkillsUsageLog

## Skills System
Server-side markdown files. AI loads only relevant 
files per request — not all at once.
Each skill file contains:
- What it is
- When to apply
- Entry/exit rules
- Risk parameters
- Red flags / invalidation
- Notes for AI on how to apply it

## News Pipeline
Cryptopanic + NewsAPI + RSS → n8n fetches every 30min
→ Claude summarizes to 150 words → stored structured in DB
→ AI reads on demand per asset

## Onboarding Flow (9 steps)
1. Welcome + name AI persona
2. Trader style + experience
3. Psychological profile (FOMO, panic seller, overtrader)
4. Goals + targets + deadlines
5. Risk profile + limits + trading hours
6. Asset preferences + blacklist
7. Exchange API connection (trade-only permissions)
8. Strategy selection
9. AI-generated personalized intro

## Key Security Decisions
- Exchange API keys encrypted with Fernet, stored in DB
- Encryption keys in separate secrets manager
- Trade-only API permissions — no withdrawal ever
- JWT auth with refresh tokens
- All autonomous trades hard-capped in code

## Key Product Decisions
- Advisory mode default
- Autonomous mode opt-in after 30 days
- AI call budget per user per day (prevent cost blowout)
- Conversation memory truncated to last 10 exchanges
- News summarized before feeding to AI (keep context lean)
- Skills files updated server-side — no app update needed
- Telegram bot = notifications/alerts only, app = everything else
- Two bot tokens always: dev and prod

## Build Phases
Phase 1 — Foundation
  Backend skeleton, FastAPI setup, PostgreSQL + Redis,
  JWT auth, user registration, React Native app skeleton,
  navigation structure, onboarding flow, exchange connection,
  basic portfolio screen

Phase 2 — Skills Engine + AI Brain
  Skills .md file system, Claude integration,
  preference profile → AI context pipeline,
  AI chat screen, /ask /suggest, conversation memory

Phase 3 — Trading + Strategies
  Market data pipeline, pandas-ta indicators,
  strategy execution engine, stop-loss/take-profit,
  DCA + RSI + MACD + Grid strategies, APScheduler

Phase 4 — FA + News + Weekly Outlook
  News pipeline (n8n), Cryptopanic + RSS integration,
  FA report generator, weekly outlook engine,
  macro data integration

Phase 5 — Personalization
  Behavioral pattern detection, emotional tracking,
  cooling off period, missed opportunity log,
  goal tracking, risk budget system, trade regret log

Phase 6 — Delight
  Streaks, ranks, levels, personal records,
  monthly trader personality report, weekly AI review

## Current Status
Phase 1 — COMPLETE.

Backend skeleton with FastAPI, async PostgreSQL + SQLAlchemy,
17 SQLAlchemy models, JWT auth (register/login/refresh),
9-step onboarding REST API, exchange connection + portfolio
skeleton endpoints. React Native Expo app with NativeWind,
Zustand auth store, React Navigation, 9 onboarding screens,
login/register, portfolio, exchange connection, settings.
docker-compose.yml for PostgreSQL + Redis.

Ready for Phase 2.

## How To Work With Me
- Always explain what you're building and why before coding
- One feature at a time, fully complete before next
- Flag security issues immediately
- Keep code modular — one concern per file
- Always show full file contents not snippets
- Remind me of dependencies if I skip ahead
- Update CONTEXT.md after each completed phase