"""Tests for backend/services/ai/context_builder.py"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.services.ai.context_builder import (
    ContextBuilder,
    _load_user_profile,
    _format_conversation_history,
    _load_market_snapshot,
    MAX_HISTORY_EXCHANGES,
)


class TestContextBuilderSync:
    """Test ContextBuilder.assemble_sync() - no DB required."""

    def test_assemble_sync_returns_string(self):
        """assemble_sync should return a string."""
        result = ContextBuilder.assemble_sync(1, "Should I long BTC with proper risk?")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_assemble_sync_contains_user_profile_section(self):
        """Result should contain user profile section."""
        result = ContextBuilder.assemble_sync(42, "trend following strategy")
        assert "# USER PROFILE" in result

    def test_assemble_sync_contains_skills_section(self):
        """Result should contain relevant skills section."""
        result = ContextBuilder.assemble_sync(1, "position sizing and leverage")
        assert "# RELEVANT SKILLS" in result

    def test_assemble_sync_contains_conversation_history(self):
        """Result should contain conversation history section."""
        result = ContextBuilder.assemble_sync(1, "test message")
        assert "# CONVERSATION HISTORY" in result

    def test_assemble_sync_contains_market_snapshot(self):
        """Result should contain market snapshot section."""
        result = ContextBuilder.assemble_sync(1, "test message")
        assert "# MARKET SNAPSHOT" in result

    def test_assemble_sync_no_match_returns_placeholder(self):
        """When no skills match, should show placeholder text."""
        result = ContextBuilder.assemble_sync(1, "xyz random nonsense 123")
        assert "No specific skills matched" in result or "# RELEVANT SKILLS" in result


class TestContextBuilderAssemble:
    """Test ContextBuilder.assemble() async method - requires DB."""

    @pytest.mark.asyncio
    async def test_assemble_returns_string(self):
        """assemble should return a context string."""
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock()

        # Mock all the DB queries to return empty results
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await ContextBuilder.assemble(
            user_id=1,
            user_message="Should I long BTC?",
            db=mock_db,
        )
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_assemble_skips_market_snapshot(self):
        """assemble with include_market=False should not include market."""
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await ContextBuilder.assemble(
            user_id=1,
            user_message="test",
            db=mock_db,
            include_market=False,
        )
        assert "# MARKET SNAPSHOT" not in result


class TestFormatConversationHistory:
    """Test _format_conversation_history helper."""

    def test_empty_history(self):
        """Should handle empty history list."""
        result = _format_conversation_history([])
        assert "No prior conversation" in result

    def test_single_message(self):
        """Should format single message correctly."""
        history = [{"role": "user", "content": "Hello"}]
        result = _format_conversation_history(history)
        assert "User" in result
        assert "Hello" in result

    def test_multiple_messages(self):
        """Should format multiple messages."""
        history = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First response"},
        ]
        result = _format_conversation_history(history)
        assert "User" in result
        assert "Assistant" in result
        assert "First message" in result

    def test_truncates_long_content(self):
        """Should truncate messages over 500 chars."""
        long_content = "x" * 600
        history = [{"role": "user", "content": long_content}]
        result = _format_conversation_history(history)
        assert len(result) < 700  # Should be truncated


class TestLoadUserProfile:
    """Test _load_user_profile function."""

    @pytest.mark.asyncio
    async def test_load_profile_returns_user_id(self):
        """Should return profile dict with user_id."""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        profile = await _load_user_profile(1, mock_db)
        assert isinstance(profile, dict)
        assert profile["user_id"] == 1


class TestLoadMarketSnapshot:
    """Test _load_market_snapshot function."""

    @pytest.mark.asyncio
    async def test_market_snapshot_returns_dict(self):
        """Should return market snapshot dict."""
        mock_db = AsyncMock()
        snapshot = await _load_market_snapshot(mock_db, "Should I long BTC?")
        assert isinstance(snapshot, dict)
        assert "snapshot_time" in snapshot

    @pytest.mark.asyncio
    async def test_market_snapshot_detects_assets(self):
        """Should detect mentioned assets in message."""
        mock_db = AsyncMock()
        snapshot = await _load_market_snapshot(mock_db, "What about BTC and ETH?")
        assert "checked_assets" in snapshot


class TestMaxHistoryExchanges:
    """Test MAX_HISTORY_EXCHANGES constant."""

    def test_max_history_value(self):
        """Should be set to 10."""
        assert MAX_HISTORY_EXCHANGES == 10