"""Context Builder — assembles full AI context per request.

Responsibilities:
  1. Load user profile (TraderProfile, PsychProfile, RiskBudget, PerformanceStats)
  2. Match relevant skills via SkillsEngine.match_skills()
  3. Fetch last 10 conversation memory entries
  4. Fetch market snapshot (prices + basic indicators)
  5. Return concatenated context string for brain.py

Usage:
    from backend.services.ai.context_builder import ContextBuilder

    context = await ContextBuilder.assemble(
        user_id=1,
        user_message="Should I long BTC here?",
        db=session,
    )
    # context is a single string ready for system prompt injection
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user import (
    ConversationMemory,
    PerformanceStats,
    PsychProfile,
    RiskBudget,
    TraderProfile,
)
from backend.services.skills_engine import SkillsEngine


# ---------------------------------------------------------------------------
# User profile aggregation
# ---------------------------------------------------------------------------
async def _load_user_profile(user_id: int, db: AsyncSession) -> dict[str, Any]:
    """Aggregate trader profile, psych profile, risk budget, and stats."""
    profile: dict[str, Any] = {"user_id": user_id}

    # TraderProfile
    result = await db.execute(
        select(TraderProfile).where(TraderProfile.user_id == user_id)
    )
    tp = result.scalar_one_or_none()
    if tp:
        profile["trading_style"] = tp.style.value if tp.style else None
        profile["experience_level"] = tp.experience.value if tp.experience else None
        profile["preferred_assets"] = tp.preferred_assets or []
        profile["max_daily_trades"] = tp.max_daily_trades
        profile["preferred_timeframes"] = tp.preferred_timeframes or []

    # PsychProfile
    result = await db.execute(
        select(PsychProfile).where(PsychProfile.user_id == user_id)
    )
    pp = result.scalar_one_or_none()
    if pp:
        profile["psych_scores"] = {
            "fomo": pp.fomo_score,
            "panic": pp.panic_score,
            "overtrading": pp.overtrading_score,
            "revenge_trading": pp.revenge_trading_score,
            "holding_too_long": pp.holding_too_long_score,
        }
        profile["cooling_off_enabled"] = pp.cooling_off_enabled
        profile["cooling_off_minutes"] = pp.cooling_off_minutes

    # RiskBudget
    result = await db.execute(
        select(RiskBudget).where(RiskBudget.user_id == user_id)
    )
    rb = result.scalar_one_or_none()
    if rb:
        profile["risk_budget"] = {
            "max_portfolio_risk_pct": float(rb.max_portfolio_risk_percent or 0),
            "max_position_size_pct": float(rb.max_position_size_percent or 0),
            "max_daily_loss_pct": float(rb.max_daily_loss_percent or 0),
            "max_leverage": float(rb.max_leverage or 1),
        }

    # PerformanceStats
    result = await db.execute(
        select(PerformanceStats).where(PerformanceStats.user_id == user_id)
    )
    ps = result.scalar_one_or_none()
    if ps:
        profile["performance"] = {
            "total_trades": ps.total_trades,
            "win_rate": float(ps.win_rate or 0),
            "avg_return": float(ps.avg_return or 0),
            "current_streak": ps.current_streak,
            "rank": ps.rank,
            "level": ps.level,
        }

    return profile


# ---------------------------------------------------------------------------
# Conversation memory
# ---------------------------------------------------------------------------
MAX_HISTORY_EXCHANGES = 10


def _format_conversation_history(messages: list[dict[str, str]]) -> str:
    """Format conversation history as readable text for injection."""
    if not messages:
        return "No prior conversation."

    lines = ["## Recent Conversation History\n"]
    for msg in messages:
        role = msg.get("role", "unknown").capitalize()
        content = msg.get("content", "")
        # Truncate long messages
        if len(content) > 500:
            content = content[:500] + "..."
        lines.append(f"**{role}**: {content}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Market snapshot (placeholder — extend with live data later)
# ---------------------------------------------------------------------------
async def _load_market_snapshot(
    db: AsyncSession,
    user_message: str | None = None,
) -> dict[str, Any]:
    """Return market snapshot. Currently a placeholder; extend with live data."""
    # Check if user_message mentions specific assets
    mentioned: list[str] = []
    if user_message:
        upper = user_message.upper()
        known = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "AVAX", "DOT"]
        for asset in known:
            if asset in upper or asset.lower().replace("btc", "bitcoin") in upper:
                mentioned.append(asset)

    # TODO: Replace with live market data fetch
    snapshot: dict[str, Any] = {
        "snapshot_time": "2026-05-24T09:00:00Z",
        "note": "Market snapshot placeholder — extend with live prices",
    }

    # Return what we'd check for specific assets
    if mentioned:
        snapshot["checked_assets"] = mentioned

    return snapshot


# ---------------------------------------------------------------------------
# Main assembler
# ---------------------------------------------------------------------------
class ContextBuilder:
    """Assembles all context pieces into a single string for the AI brain."""

    @staticmethod
    async def assemble(
        user_id: int,
        user_message: str,
        db: AsyncSession,
        include_market: bool = True,
    ) -> str:
        """Build complete context string for AI request.

        Components (in order):
          1. User profile summary
          2. Relevant skills (matched from user_message)
          3. Last 10 conversation exchanges
          4. Market snapshot (optional)
        """
        parts: list[str] = []

        # 1. User Profile
        profile = await _load_user_profile(user_id, db)
        profile_lines = [f"# USER PROFILE (ID: {user_id})\n"]

        style = profile.get("trading_style", "Not set")
        exp = profile.get("experience_level", "Not set")
        profile_lines.append(f"- Trading Style: {style}")
        profile_lines.append(f"- Experience Level: {exp}")

        if profile.get("preferred_assets"):
            profile_lines.append(f"- Preferred Assets: {', '.join(profile['preferred_assets'])}")

        if profile.get("max_daily_trades"):
            profile_lines.append(f"- Max Daily Trades: {profile['max_daily_trades']}")

        if profile.get("risk_budget"):
            rb = profile["risk_budget"]
            profile_lines.append(
                f"- Risk Budget: Max {rb['max_portfolio_risk_pct']}% portfolio risk, "
                f"{rb['max_daily_loss_pct']}% daily loss limit"
            )

        if profile.get("psych_scores"):
            scores = profile["psych_scores"]
            profile_lines.append(
                f"- Psych Flags: FOMO={scores['fomo']}, Panic={scores['panic']}, "
                f"Overtrading={scores['overtrading']}"
            )

        if profile.get("performance"):
            p = profile["performance"]
            profile_lines.append(
                f"- Performance: {p['total_trades']} trades, "
                f"Win Rate {p['win_rate']:.1f}%, Rank: {p['rank']}"
            )

        parts.append("\n".join(profile_lines))

        # 2. Relevant Skills
        skills_content = SkillsEngine.match_skills(user_message)
        if skills_content:
            parts.append(f"# RELEVANT SKILLS\n\n{skills_content}")
        else:
            parts.append("# RELEVANT SKILLS\n\nNo specific skills matched for this query.")

        # 3. Conversation History
        result = await db.execute(
            select(ConversationMemory)
            .where(ConversationMemory.user_id == user_id)
            .order_by(ConversationMemory.created_at.desc())
            .limit(MAX_HISTORY_EXCHANGES * 2 + 2)
        )
        rows = result.scalars().all()
        rows.reverse()  # oldest first

        history = [{"role": r.role, "content": r.content} for r in rows]
        # Truncate to last 10 exchanges
        if len(history) > MAX_HISTORY_EXCHANGES * 2:
            history = history[-MAX_HISTORY_EXCHANGES * 2:]

        parts.append(_format_conversation_history(history))

        # 4. Market Snapshot
        if include_market:
            market = await _load_market_snapshot(db, user_message)
            market_lines = ["# MARKET SNAPSHOT\n"]
            for key, value in market.items():
                if key != "note":
                    market_lines.append(f"- {key}: {value}")
            market_lines.append(f"\n_{market.get('note', '')}_")
            parts.append("\n".join(market_lines))

        return "\n\n---\n\n".join(parts)

    @staticmethod
    def assemble_sync(
        user_id: int,
        user_message: str,
    ) -> str:
        """Synchronous version that only includes skills (no DB/market).
        
        Use this when DB session is not available or market data not needed.
        """
        parts: list[str] = []
        parts.append(f"# USER PROFILE (ID: {user_id})\n- Profile: not loaded (sync mode)")

        skills_content = SkillsEngine.match_skills(user_message)
        if skills_content:
            parts.append(f"# RELEVANT SKILLS\n\n{skills_content}")
        else:
            parts.append("# RELEVANT SKILLS\n\nNo specific skills matched for this query.")

        parts.append("# CONVERSATION HISTORY\n\nNot loaded (sync mode).")
        parts.append("# MARKET SNAPSHOT\n\nNot loaded (sync mode).")

        return "\n\n---\n\n".join(parts)