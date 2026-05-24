"""AI endpoints: ask and suggest-trade.

Stage 7: Uses ContextBuilder for context assembly
- Loads user profile, skills, conversation history, market snapshot
- Returns AI response with reasoning
- Supports intelligent skills matching via match_skills()
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.user import User, ConversationMemory
from backend.services.ai.brain import AIBrain, BudgetExceeded, check_budget
from backend.services.ai.context_builder import ContextBuilder

router = APIRouter()

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------
class AskRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    coin_ids: list[str] = Field(
        default=["bitcoin", "ethereum"],
        description="CoinGecko IDs for market context injection",
    )
    include_market: bool = Field(
        default=True,
        description="Include live market data in context",
    )


class AskResponse(BaseModel):
    response: str
    skills_loaded: list[str]
    budget_remaining: int
    market_coins: list[str]


class SuggestRequest(BaseModel):
    coin_ids: list[str] = Field(default=["bitcoin", "ethereum"])
    include_market: bool = Field(default=True)


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


def _extract_skills_from_context(context: str) -> list[str]:
    """Extract skill names from context string for response."""
    import re
    skills = []
    for match in re.finditer(r'# \[(\w+)\] (.+)', context):
        skills.append(f"{match.group(1).lower()}/{match.group(2).strip()}")
    # If no headers found, return defaults
    if not skills:
        skills = [
            "strategies/trend_following",
            "risk_management/position_sizing",
            "market_reading/support_resistance",
        ]
    return skills


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

    Uses ContextBuilder to assemble:
    - User profile (TraderProfile, PsychProfile, RiskBudget, PerformanceStats)
    - Relevant skills (matched from user message)
    - Last 10 conversation memory entries
    - Market snapshot (optional)
    """
    # 1. Budget check
    try:
        calls_used = await check_budget(current_user.id, db)
    except BudgetExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily AI call limit reached ({e.limit} calls). Resets at midnight UTC.",
        )

    # 2. Build context using ContextBuilder
    context = await ContextBuilder.assemble(
        user_id=current_user.id,
        user_message=payload.message,
        db=db,
        include_market=payload.include_market,
    )

    # 3. Extract loaded skills from context
    skills_loaded = _extract_skills_from_context(context)

    # 4. Call AI with assembled context
    brain = AIBrain()
    ai_text = await brain.ask(
        user_id=current_user.id,
        user_message=payload.message,
        skills_context=context,
    )

    # 5. Store exchange
    await _store_exchange(db, current_user.id, payload.message, ai_text)

    # 6. Calculate budget
    from backend.core.config import settings as cfg
    budget_remaining = max(0, cfg.AI_CALL_BUDGET_PER_USER - calls_used - 1)

    return AskResponse(
        response=ai_text,
        skills_loaded=skills_loaded,
        budget_remaining=budget_remaining,
        market_coins=payload.coin_ids if payload.include_market else [],
    )


@router.post("/suggest", response_model=SuggestResponse)
async def suggest_trades(
    payload: SuggestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SuggestResponse:
    """Ask the AI to generate trade ideas based on user profile + loaded skills.

    Uses ContextBuilder to build context, then brain.suggest_trades()
    for structured trade idea generation.
    """
    # 1. Budget check
    try:
        calls_used = await check_budget(current_user.id, db)
    except BudgetExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily AI call limit reached ({e.limit} calls). Resets at midnight UTC.",
        )

    # 2. Build context
    context = await ContextBuilder.assemble(
        user_id=current_user.id,
        user_message="trade suggestions for current market conditions",
        db=db,
        include_market=payload.include_market,
    )

    # 3. Extract loaded skills
    skills_loaded = _extract_skills_from_context(context)

    # 4. Call AI for trade suggestions
    brain = AIBrain()
    ai_text = await brain.suggest_trades(
        user_id=current_user.id,
        skills_context=context,
    )

    # 5. Store exchange
    synthetic_prompt = "[TRADE SUGGESTION REQUEST]"
    await _store_exchange(db, current_user.id, synthetic_prompt, ai_text)

    # 6. Calculate budget
    from backend.core.config import settings as cfg
    budget_remaining = max(0, cfg.AI_CALL_BUDGET_PER_USER - calls_used - 1)

    return SuggestResponse(
        ideas=ai_text,
        skills_loaded=skills_loaded,
        budget_remaining=budget_remaining,
        market_coins=payload.coin_ids if payload.include_market else [],
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
