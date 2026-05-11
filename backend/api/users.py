"""User profile and account management endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.user import User

router = APIRouter()


class UserProfileOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_onboarded: bool
    role: str

    class Config:
        from_attributes = True


class OnboardingStatus(BaseModel):
    is_onboarded: bool


@router.get("/me", response_model=UserProfileOut)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/me/onboarding", response_model=OnboardingStatus)
async def get_onboarding_status(current_user: User = Depends(get_current_user)) -> dict[str, bool]:
    return {"is_onboarded": current_user.is_onboarded}
