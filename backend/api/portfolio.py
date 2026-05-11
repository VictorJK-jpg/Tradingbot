"""Portfolio overview endpoint (skeleton for Phase 1).

Phase 3 will integrate CCXT to fetch real balances and positions.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.core.security import get_current_user
from backend.models.user import User

router = APIRouter()


class PortfolioOut(BaseModel):
    total_balance_usd: float = 0.0
    available_balance_usd: float = 0.0
    open_positions: list[dict] = []
    daily_pnl: float = 0.0


@router.get("/overview", response_model=PortfolioOut)
async def get_portfolio(current_user: User = Depends(get_current_user)) -> PortfolioOut:
    """Return static skeleton until CCXT integration in Phase 3."""
    return PortfolioOut()
