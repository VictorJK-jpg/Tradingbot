"""Tradingbot

Pytest configuration and shared fixtures.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool

from backend.core.database import Base


@pytest.fixture
def mock_db():
    """Mock AsyncSession for tests without real DB."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.add = MagicMock()
    session.add_all = MagicMock()
    return session


@pytest.fixture
def sample_user_message():
    """Sample user messages for testing."""
    return [
        "Should I long BTC with proper risk?",
        "trend following strategy for swing trading",
        "position sizing and leverage",
        "support resistance technical analysis",
        "macro outlook weekly DXY VIX",
        "random nonsense xyz123",
    ]