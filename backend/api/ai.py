"""AI endpoints: ask and suggest-trade.

Phase 4 enhancements:
  - Conversation memory: last 10 exchanges injected as chat context
  - AI call budget: enforced per user per day (AI_CALL_BUDGET_PER_USER)
  - Market data: live BTC/ETH prices auto-injected into system prompt
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.user import (
    User,
    TraderProfile,
    PsychProfile,
    RiskBudget,
    ConversationMemory,
)
from backend.services.skills_engine import SkillsEngine
from backend.services.ai.brain import (
    AIBrain,
    BudgetExceeded,
    check_budget,
    fetch_conversation_history,
    fetch_market_context,
)

router = APIRouter()

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------
class AskRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    skills: list[dict[str, str]] = Field(
        default=[], description="List of {'category': '...', 'name': '...'}"
    )
    coin_ids: list[str] = Field(
        default=["bitcoin", "ethereum"],
        description="CoinGecko IDs for market context injection",
    )


class AskResponse(BaseModel):
    response: str
    skills_loaded: list[str]
    budget_remaining: int
    market_coins: list[str]


class SuggestRequest(BaseModel):
    skills: list[dict[str, str]] = Field(default=[])
    coin_ids: list[str] = Field(default=["bitcoin", "ethereum"])


class SuggestResponse(BaseModel):
    ideas: str
    skills_loaded: list[str]
    budget_remaining: int
    market_coins: list[str]


class BudgetResponse(BaseModel):
    calls_used_today: int
    calls_remaining: int
    daily_limit: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _fetch_user_profile(db: AsyncSession, user_id: int) -> dict:
    """Gather TraderProfile, PsychProfile, and RiskBudget into a flat dict."""
    profile = {}

    tp_result = await db.execute(
        select(TraderProfile).where(TraderProfile.user_id == user_id)
    )
    tp: TraderProfile | None = tp_result.scalar_one_or_none()
    if tp:
        profile["style"] = tp.style.value if tp.style else "unset"
        profile["experience"] = tp.experience.value if tp.experience else "unset"
        profile["preferred_assets"] = tp.preferred_assets
        profile["max_daily_trades"] = tp.max_daily_trades

    pp_result = await db.execute(
        select(PsychProfile).where(PsychProfile.user_id == user_id)
    )
    pp: PsychProfile | None = pp_result.scalar_one_or_none()
    if pp:
        profile["fomo_score"] = pp.fomo_score
        profile["panic_score"] = pp.panic_score
        profile["overtrading_score"] = pp.overtrading_score
        profile["revenge_trading_score"] = pp.revenge_trading_score
        profile["cooling_off"] = pp.cooling_off_enabled

    rb_result = await db.execute(
        select(RiskBudget).where(RiskBudget.user_id == user_id)
    )
    rb: RiskBudget | None = rb_result.scalar_one_or_none()
    if rb:
        profile["max_portfolio_risk"] = float(rb.max_portfolio_risk_percent)
        profile["max_position_size"] = float(rb.max_position_size_percent)
        profile["max_daily_loss"] = float(rb.max_daily_loss_percent)
        profile["max_leverage"] = float(rb.max_leverage)

    return profile


def _load_skills(requested: list[dict[str, str]]) -> tuple[str, list[str]]:
    """Load requested skills or default set. Returns (context_string, list_of_loaded_names)."""
    engine = SkillsEngine()
    if requested:
        selections = [{"category": s["category"], "name": s["name"]} for s in requested]
        loaded_names = [f"{s['category']}/{s['name']}" for s in selections]
        try:
            return engine.load_multi(selections), loaded_names
        except FileNotFoundError:
            return "", loaded_names

    defaults = [
        {"category": "strategies", "name": "trend_following"},
        {"category": "risk_management", "name": "position_sizing"},
        {"category": "market_reading", "name": "support_resistance"},
    ]
    loaded_names = [
        "strategies/trend_following",
        "risk_management/position_sizing",
        "market_reading/support_resistance",
    ]
    try:
        return engine.load_multi(defaults), loaded_names
    except FileNotFoundError:
        return "", loaded_names


async def _store_exchange(
    db: AsyncSession,
    user_id: int,
    user_message: str,
    ai_response: str,
) -> None:
    """Persist user message and AI reply as two rows in conversation_memory."""
    db.add_all([
        ConversationMemory(user_id=user_id, role="user", content=user_message),
        ConversationMemory(user_id=user_id, role="assistant", content=ai_response),
    ])
    await db.commit()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post("/ask", response_model=AskResponse)
async def ask_ai(
    payload: AskRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AskResponse:
    """Send a message to the AI and get a response.

    Features:
    - Enforces daily AI call budget per user
    - Injects last 10 conversation exchanges as context
    - Injects live market data (BTC/ETH prices) into system prompt
    - Stores the exchange in conversation_memory
    """
    # 1. Budget check
    try:
        calls_used = await check_budget(current_user.id, db)
    except BudgetExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily AI call limit reached ({e.limit} calls). Resets at midnight UTC.",
        )

    # 2. Gather context in parallel-ish
    user_profile = await _fetch_user_profile(db, current_user.id)
    skills_context, skills_loaded = _load_skills(payload.skills)
    conversation_history = await fetch_conversation_history(current_user.id, db)
    market_context = await fetch_market_context(payload.coin_ids)

    # 3. Call AI
    brain = AIBrain()
    ai_text = await brain.ask(
        user_id=current_user.id,
        user_message=payload.message,
        user_profile=user_profile,
        market_context=market_context,
        skills_context=skills_context,
        conversation_history=conversation_history,
    )

    # 4. Store exchange
    await _store_exchange(db, current_user.id, payload.message, ai_text)

    from backend.core.config import settings as cfg
    budget_remaining = max(0, cfg.AI_CALL_BUDGET_PER_USER - calls_used - 1)

    return AskResponse(
        response=ai_text,
        skills_loaded=skills_loaded,
        budget_remaining=budget_remaining,
        market_coins=payload.coin_ids,
    )


@router.post("/suggest", response_model=SuggestResponse)
async def suggest_trades(
    payload: SuggestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SuggestResponse:
    """Ask the AI to generate trade ideas based on the user's profile.

    Same enhancements as /ask: budget, memory, market data.
    """
    # 1. Budget check
    try:
        calls_used = await check_budget(current_user.id, db)
    except BudgetExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily AI call limit reached ({e.limit} calls). Resets at midnight UTC.",
        )

    # 2. Gather context
    user_profile = await _fetch_user_profile(db, current_user.id)
    skills_context, skills_loaded = _load_skills(payload.skills)
    conversation_history = await fetch_conversation_history(current_user.id, db)
    market_context = await fetch_market_context(payload.coin_ids)

    # 3. Call AI
    brain = AIBrain()
    ai_text = await brain.suggest_trades(
        user_id=current_user.id,
        user_profile=user_profile,
        market_context=market_context,
        skills_context=skills_context,
        conversation_history=conversation_history,
    )

    # 4. Store exchange
    synthetic_prompt = "[TRADE SUGGESTION REQUEST]"
    await _store_exchange(db, current_user.id, synthetic_prompt, ai_text)

    from backend.core.config import settings as cfg
    budget_remaining = max(0, cfg.AI_CALL_BUDGET_PER_USER - calls_used - 1)

    return SuggestResponse(
        ideas=ai_text,
        skills_loaded=skills_loaded,
        budget_remaining=budget_remaining,
        market_coins=payload.coin_ids,
    )


@router.get("/budget", response_model=BudgetResponse)
async def get_budget(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BudgetResponse:
    """Check remaining AI call budget for today."""
    from backend.core.config import settings as cfg
    from datetime import datetime, timezone
    from sqlalchemy import select, func
    from backend.models.user import ConversationMemory

    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    result = await db.execute(
        select(func.count(ConversationMemory.id)).where(
            ConversationMemory.user_id == current_user.id,
            ConversationMemory.role == "assistant",
            ConversationMemory.created_at >= today_start,
        )
    )
    calls_used = result.scalar() or 0
    limit = cfg.AI_CALL_BUDGET_PER_USER

    return BudgetResponse(
        calls_used_today=calls_used,
        calls_remaining=max(0, limit - calls_used),
        daily_limit=limit,
    )
