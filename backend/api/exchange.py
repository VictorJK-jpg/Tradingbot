"""Exchange connection and basic portfolio read endpoints.

Phase 1: skeleton only. Phase 3 adds live CCXT integration.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.user import User, ExchangeConnection

router = APIRouter()


class ExchangeOut(BaseModel):
    id: int
    exchange: str
    is_testnet: bool
    is_active: bool
    last_verified_at: str | None

    class Config:
        from_attributes = True


@router.get("/connections", response_model=list[ExchangeOut])
async def list_connections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ExchangeConnection]:
    result = await db.execute(
        select(ExchangeConnection).where(ExchangeConnection.user_id == current_user.id)
    )
    return result.scalars().all()


class AddExchangePayload(BaseModel):
    exchange: str
    api_key: str
    api_secret: str
    is_testnet: bool = True


@router.post("/connections")
async def add_connection(
    payload: AddExchangePayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from backend.core.security import encrypt_api_key

    conn = ExchangeConnection(
        user_id=current_user.id,
        exchange=payload.exchange,
        api_key_encrypted=encrypt_api_key(payload.api_key),
        api_secret_encrypted=encrypt_api_key(payload.api_secret),
        is_testnet=payload.is_testnet,
    )
    db.add(conn)
    await db.commit()
    await db.refresh(conn)
    return {"status": "ok", "connection_id": conn.id}
