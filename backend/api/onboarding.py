"""Onboarding flow endpoints (9 steps).

Stores intermediate and final onboarding data across the 9-step wizard.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.user import (
    User,
    BotPersona,
    TraderProfile,
    PsychProfile,
    RiskBudget,
    PerformanceStats,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Step 1 — Welcome + name AI persona
# ---------------------------------------------------------------------------
class Step1Payload(BaseModel):
    persona_name: str
    personality: str | None = None
    voice_tone: str | None = None


@router.post("/step-1")
async def step_1(
    payload: Step1Payload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    persona = BotPersona(
        user_id=current_user.id,
        name=payload.persona_name,
        personality=payload.personality,
        voice_tone=payload.voice_tone,
    )
    db.add(persona)
    await db.commit()
    return {"status": "ok", "step": 1}


# ---------------------------------------------------------------------------
# Step 2 — Trader style + experience
# ---------------------------------------------------------------------------
class Step2Payload(BaseModel):
    style: str
    experience: str
    preferred_timeframes: list[str] | None = None


@router.post("/step-2")
async def step_2(
    payload: Step2Payload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = TraderProfile(
        user_id=current_user.id,
        style=payload.style,
        experience=payload.experience,
        preferred_timeframes=payload.preferred_timeframes or [],
    )
    db.add(profile)
    await db.commit()
    return {"status": "ok", "step": 2}


# ---------------------------------------------------------------------------
# Step 3 — Psychological profile
# ---------------------------------------------------------------------------
class Step3Payload(BaseModel):
    fomo_score: int = 50
    panic_score: int = 50
    overtrading_score: int = 50
    revenge_trading_score: int = 50
    holding_too_long_score: int = 50
    cooling_off_enabled: bool = False
    cooling_off_minutes: int = 30


@router.post("/step-3")
async def step_3(
    payload: Step3Payload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    psych = PsychProfile(
        user_id=current_user.id,
        **payload.model_dump(),
    )
    db.add(psych)
    await db.commit()
    return {"status": "ok", "step": 3}


# ---------------------------------------------------------------------------
# Step 4 — Goals + targets + deadlines
# ---------------------------------------------------------------------------
class Step4Goal(BaseModel):
    title: str
    description: str | None = None
    target_value: float | None = None
    deadline: str | None = None


class Step4Payload(BaseModel):
    goals: list[Step4Goal]


@router.post("/step-4")
async def step_4(
    payload: Step4Payload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from backend.models.user import Goal
    for g in payload.goals:
        goal = Goal(
            user_id=current_user.id,
            title=g.title,
            description=g.description,
            target_value=g.target_value,
        )
        db.add(goal)
    await db.commit()
    return {"status": "ok", "step": 4}


# ---------------------------------------------------------------------------
# Step 5 — Risk profile + limits + trading hours
# ---------------------------------------------------------------------------
class Step5Payload(BaseModel):
    max_portfolio_risk_percent: float = 2.0
    max_position_size_percent: float = 10.0
    max_daily_loss_percent: float = 3.0
    max_leverage: float = 1.0
    hard_stop_usd: float | None = None
    trading_hours_start: str | None = None
    trading_hours_end: str | None = None
    max_daily_trades: int = 5


@router.post("/step-5")
async def step_5(
    payload: Step5Payload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    risk = RiskBudget(
        user_id=current_user.id,
        max_portfolio_risk_percent=payload.max_portfolio_risk_percent,
        max_position_size_percent=payload.max_position_size_percent,
        max_daily_loss_percent=payload.max_daily_loss_percent,
        max_leverage=payload.max_leverage,
        hard_stop_usd=payload.hard_stop_usd,
    )
    db.add(risk)

    # Update trader profile with trading hours and max daily trades
    # We assume trader_profile exists from step 2
    from sqlalchemy import select
    result = await db.execute(
        select(TraderProfile).where(TraderProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if profile:
        profile.trading_hours_start = payload.trading_hours_start
        profile.trading_hours_end = payload.trading_hours_end
        profile.max_daily_trades = payload.max_daily_trades

    await db.commit()
    return {"status": "ok", "step": 5}


# ---------------------------------------------------------------------------
# Step 6 — Asset preferences + blacklist
# ---------------------------------------------------------------------------
class Step6Payload(BaseModel):
    preferred_assets: list[str]
    blacklist_assets: list[str]


@router.post("/step-6")
async def step_6(
    payload: Step6Payload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import select
    result = await db.execute(
        select(TraderProfile).where(TraderProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if profile:
        profile.preferred_assets = payload.preferred_assets
        profile.blacklist_assets = payload.blacklist_assets
        await db.commit()
    return {"status": "ok", "step": 6}


# ---------------------------------------------------------------------------
# Step 7 — Exchange API connection
# ---------------------------------------------------------------------------
class Step7Payload(BaseModel):
    exchange: str
    api_key: str
    api_secret: str
    is_testnet: bool = True


@router.post("/step-7")
async def step_7(
    payload: Step7Payload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from backend.core.security import encrypt_api_key
    from backend.models.user import ExchangeConnection

    conn = ExchangeConnection(
        user_id=current_user.id,
        exchange=payload.exchange,
        api_key_encrypted=encrypt_api_key(payload.api_key),
        api_secret_encrypted=encrypt_api_key(payload.api_secret),
        is_testnet=payload.is_testnet,
    )
    db.add(conn)
    await db.commit()
    return {"status": "ok", "step": 7}


# ---------------------------------------------------------------------------
# Step 8 — Strategy selection
# ---------------------------------------------------------------------------
class Step8Payload(BaseModel):
    selected_strategies: list[str]


@router.post("/step-8")
async def step_8(
    payload: Step8Payload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Strategies are stored in skills/; here we just log user preference.
    # A `UserStrategy` model can be added in Phase 3.
    return {"status": "ok", "step": 8, "selected": payload.selected_strategies}


# ---------------------------------------------------------------------------
# Step 9 — Finalise onboarding
# ---------------------------------------------------------------------------
@router.post("/complete")
async def complete_onboarding(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark user as onboarded and initialise performance stats."""
    current_user.is_onboarded = True

    stats = PerformanceStats(user_id=current_user.id)
    db.add(stats)
    await db.commit()

    return {"status": "ok", "message": "Onboarding complete. Welcome aboard!"}
