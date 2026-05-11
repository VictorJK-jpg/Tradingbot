"""All SQLAlchemy models for the crypto-platform.

Organised by domain but kept in one file for Phase-1 simplicity.
Split into separate modules as the project grows.
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    JSON,
    Numeric,
    Enum,
    Index,
)
from sqlalchemy.orm import relationship

from backend.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class UserRole(str, PyEnum):
    USER = "user"
    ADMIN = "admin"


class TraderStyle(str, PyEnum):
    SCALPER = "scalper"
    DAY_TRADER = "day_trader"
    SWING_TRADER = "swing_trader"
    POSITION_TRADER = "position_trader"
    INVESTOR = "investor"


class ExperienceLevel(str, PyEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ExchangeName(str, PyEnum):
    BINANCE = "binance"
    BYBIT = "bybit"
    COINBASE = "coinbase"
    KRAKEN = "kraken"


class AlertType(str, PyEnum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PERCENT_CHANGE = "percent_change"


class GoalStatus(str, PyEnum):
    ACTIVE = "active"
    ACHIEVED = "achieved"
    FAILED = "failed"


class TradeSide(str, PyEnum):
    BUY = "buy"
    SELL = "sell"


class TradeStatus(str, PyEnum):
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


# ---------------------------------------------------------------------------
# 1. Users
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_onboarded = Column(Boolean, default=False, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    bot_persona = relationship("BotPersona", back_populates="user", uselist=False)
    trader_profile = relationship("TraderProfile", back_populates="user", uselist=False)
    psych_profile = relationship("PsychProfile", back_populates="user", uselist=False)
    exchange_connections = relationship("ExchangeConnection", back_populates="user")
    trades = relationship("Trade", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    risk_budget = relationship("RiskBudget", back_populates="user", uselist=False)
    performance_stats = relationship("PerformanceStats", back_populates="user", uselist=False)
    conversation_memory = relationship("ConversationMemory", back_populates="user")
    price_alerts = relationship("PriceAlert", back_populates="user")
    emotional_logs = relationship("EmotionalLog", back_populates="user")
    missed_opportunities = relationship("MissedOpportunity", back_populates="user")


# ---------------------------------------------------------------------------
# 2. BotPersona
# ---------------------------------------------------------------------------
class BotPersona(Base):
    __tablename__ = "bot_personas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    personality = Column(Text, nullable=True)
    voice_tone = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="bot_persona")


# ---------------------------------------------------------------------------
# 3. TraderProfile
# ---------------------------------------------------------------------------
class TraderProfile(Base):
    __tablename__ = "trader_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    style = Column(Enum(TraderStyle), nullable=True)
    experience = Column(Enum(ExperienceLevel), nullable=True)
    preferred_assets = Column(JSON, default=list, nullable=False)
    blacklist_assets = Column(JSON, default=list, nullable=False)
    trading_hours_start = Column(String(5), nullable=True)
    trading_hours_end = Column(String(5), nullable=True)
    max_daily_trades = Column(Integer, default=5, nullable=False)
    preferred_timeframes = Column(JSON, default=list, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="trader_profile")


# ---------------------------------------------------------------------------
# 4. PsychProfile
# ---------------------------------------------------------------------------
class PsychProfile(Base):
    __tablename__ = "psych_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    fomo_score = Column(Integer, default=50, nullable=False)
    panic_score = Column(Integer, default=50, nullable=False)
    overtrading_score = Column(Integer, default=50, nullable=False)
    revenge_trading_score = Column(Integer, default=50, nullable=False)
    holding_too_long_score = Column(Integer, default=50, nullable=False)
    cooling_off_enabled = Column(Boolean, default=False, nullable=False)
    cooling_off_minutes = Column(Integer, default=30, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="psych_profile")


# ---------------------------------------------------------------------------
# 5. ExchangeConnections
# ---------------------------------------------------------------------------
class ExchangeConnection(Base):
    __tablename__ = "exchange_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    exchange = Column(Enum(ExchangeName), nullable=False)
    api_key_encrypted = Column(Text, nullable=False)
    api_secret_encrypted = Column(Text, nullable=False)
    is_testnet = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="exchange_connections")


# ---------------------------------------------------------------------------
# 6. Trades
# ---------------------------------------------------------------------------
class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    exchange = Column(Enum(ExchangeName), nullable=False)
    symbol = Column(String(20), nullable=False)
    side = Column(Enum(TradeSide), nullable=False)
    status = Column(Enum(TradeStatus), default=TradeStatus.PENDING, nullable=False)

    entry_price = Column(Numeric(24, 8), nullable=True)
    exit_price = Column(Numeric(24, 8), nullable=True)
    quantity = Column(Numeric(24, 8), nullable=False)
    stop_loss = Column(Numeric(24, 8), nullable=True)
    take_profit = Column(Numeric(24, 8), nullable=True)

    strategy_used = Column(String(100), nullable=True)
    ai_advisory = Column(Boolean, default=False, nullable=False)
    autonomous = Column(Boolean, default=False, nullable=False)

    opened_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    user = relationship("User", back_populates="trades")
    journal = relationship("TradeJournal", back_populates="trade", uselist=False)


# ---------------------------------------------------------------------------
# 7. TradeJournal
# ---------------------------------------------------------------------------
class TradeJournal(Base):
    __tablename__ = "trade_journals"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, ForeignKey("trades.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    pre_trade_mood = Column(String(50), nullable=True)
    post_trade_mood = Column(String(50), nullable=True)
    rationale = Column(Text, nullable=True)
    mistakes = Column(Text, nullable=True)
    lessons = Column(Text, nullable=True)
    regret_score = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    trade = relationship("Trade", back_populates="journal")


# ---------------------------------------------------------------------------
# 8. ConversationMemory
# ---------------------------------------------------------------------------
class ConversationMemory(Base):
    __tablename__ = "conversation_memory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    tokens_used = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    user = relationship("User", back_populates="conversation_memory")

    __table_args__ = (
        Index("ix_conversation_memory_user_id_created_at", "user_id", "created_at"),
    )


# ---------------------------------------------------------------------------
# 9. PriceAlerts
# ---------------------------------------------------------------------------
class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    symbol = Column(String(20), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    threshold = Column(Numeric(24, 8), nullable=False)
    is_triggered = Column(Boolean, default=False, nullable=False)
    triggered_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    user = relationship("User", back_populates="price_alerts")


# ---------------------------------------------------------------------------
# 10. Goals
# ---------------------------------------------------------------------------
class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_value = Column(Numeric(24, 8), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(GoalStatus), default=GoalStatus.ACTIVE, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="goals")


# ---------------------------------------------------------------------------
# 11. RiskBudget
# ---------------------------------------------------------------------------
class RiskBudget(Base):
    __tablename__ = "risk_budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    max_portfolio_risk_percent = Column(Numeric(5, 2), default=2.0, nullable=False)
    max_position_size_percent = Column(Numeric(5, 2), default=10.0, nullable=False)
    max_daily_loss_percent = Column(Numeric(5, 2), default=3.0, nullable=False)
    max_leverage = Column(Numeric(5, 2), default=1.0, nullable=False)
    hard_stop_usd = Column(Numeric(18, 2), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="risk_budget")


# ---------------------------------------------------------------------------
# 12. PerformanceStats
# ---------------------------------------------------------------------------
class PerformanceStats(Base):
    __tablename__ = "performance_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    total_trades = Column(Integer, default=0, nullable=False)
    winning_trades = Column(Integer, default=0, nullable=False)
    losing_trades = Column(Integer, default=0, nullable=False)
    win_rate = Column(Numeric(5, 2), default=0.0, nullable=False)
    avg_return = Column(Numeric(10, 4), default=0.0, nullable=False)
    sharpe_ratio = Column(Numeric(10, 4), nullable=True)
    max_drawdown = Column(Numeric(10, 4), nullable=True)
    current_streak = Column(Integer, default=0, nullable=False)
    best_streak = Column(Integer, default=0, nullable=False)
    rank = Column(String(50), default="Novice", nullable=False)
    level = Column(Integer, default=1, nullable=False)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="performance_stats")


# ---------------------------------------------------------------------------
# 13. MissedOpportunities
# ---------------------------------------------------------------------------
class MissedOpportunity(Base):
    __tablename__ = "missed_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    symbol = Column(String(20), nullable=False)
    reason_missed = Column(Text, nullable=True)
    potential_return = Column(Numeric(10, 4), nullable=True)
    ai_note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    user = relationship("User", back_populates="missed_opportunities")


# ---------------------------------------------------------------------------
# 14. EmotionalLog
# ---------------------------------------------------------------------------
class EmotionalLog(Base):
    __tablename__ = "emotional_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    mood = Column(String(50), nullable=False)
    intensity = Column(Integer, default=5, nullable=False)
    trigger = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    user = relationship("User", back_populates="emotional_logs")


# ---------------------------------------------------------------------------
# 15. MacroEvents
# ---------------------------------------------------------------------------
class MacroEvent(Base):
    __tablename__ = "macro_events"

    id = Column(Integer, primary_key=True, index=True)
    event_date = Column(DateTime(timezone=True), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    impact_score = Column(Integer, nullable=True)
    source = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


# ---------------------------------------------------------------------------
# 16. NewsCache
# ---------------------------------------------------------------------------
class NewsCache(Base):
    __tablename__ = "news_cache"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False)
    asset_symbol = Column(String(20), nullable=True)
    headline = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False)
    url = Column(String(500), nullable=True)
    sentiment = Column(String(20), nullable=True)
    fetched_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        Index("ix_news_cache_asset_fetched", "asset_symbol", "fetched_at"),
    )


# ---------------------------------------------------------------------------
# 17. SkillsUsageLog
# ---------------------------------------------------------------------------
class SkillsUsageLog(Base):
    __tablename__ = "skills_usage_log"

    id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String(255), nullable=False)
    asset_symbol = Column(String(20), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    request_id = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
