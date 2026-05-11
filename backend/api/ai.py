"""AI endpoints: ask and suggest-trade."""

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
from backend.services.ai.brain import AIBrain

router = APIRouter()

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------
class AskRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    skills: list[dict[str, str]] = Field(default=[], description="List of {'category': '...', 'name': '...'}")


class AskResponse(BaseModel):
    response: str
    skills_loaded: list[str]


class SuggestRequest(BaseModel):
    skills: list[dict[str, str]] = Field(default=[])


class SuggestResponse(BaseModel):
    ideas: str
    skills_loaded: list[str]


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
        return engine.load_multi(selections), loaded_names

    # Default skill set for trading advice
    defaults = [
        {"category": "strategies", "name": "trend_following"},
        {"category": "risk_management", "name": "position_sizing"},
        {"category": "market_reading", "name": "support_resistance"},
    ]
    loaded_names = ["strategies/trend_following", "risk_management/position_sizing", "market_reading/support_resistance"]
    return engine.load_multi(defaults), loaded_names


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
    """Send a message to the AI and get a response. Stores the exchange."""
    user_profile = await _fetch_user_profile(db, current_user.id)
    skills_context, skills_loaded = _load_skills(payload.skills)

    brain = AIBrain()
    ai_text = await brain.ask(
        user_id=current_user.id,
        user_message=payload.message,
        user_profile=user_profile,
        skills_context=skills_context,
    )

    await _store_exchange(db, current_user.id, payload.message, ai_text)

    return AskResponse(response=ai_text, skills_loaded=skills_loaded)


@router.post("/suggest", response_model=SuggestResponse)
async def suggest_trades(
    payload: SuggestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SuggestResponse:
    """Ask the AI to generate trade ideas based on the user's profile."""
    user_profile = await _fetch_user_profile(db, current_user.id)
    skills_context, skills_loaded = _load_skills(payload.skills)

    brain = AIBrain()
    ai_text = await brain.suggest_trades(
        user_id=current_user.id,
        user_profile=user_profile,
        skills_context=skills_context,
    )

    # Store the synthetic prompt + response
    synthetic_prompt = "[TRADE SUGGESTION REQUEST]"
    await _store_exchange(db, current_user.id, synthetic_prompt, ai_text)

    return SuggestResponse(ideas=ai_text, skills_loaded=skills_loaded)
