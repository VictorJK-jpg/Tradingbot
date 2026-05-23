"""Provider-agnostic AI Brain — Groq (default), OpenRouter, Anthropic.

Enhancements over Phase 2:
  - Conversation memory: last 10 exchanges injected as chat history
  - AI call budget: enforced per user per day via DB counter
  - Market data: live prices/indicators injected into system prompt
  - Structured response: reasoning field in output

Usage:
    from backend.services.ai.brain import AIBrain
    brain = AIBrain()
    response = await brain.ask(
        user_id=1,
        user_message="Should I long BTC here?",
        user_profile={"style": "swing_trader"},
        market_context={"btc_price": 65000},
        skills_context="[STRATEGIES] Trend Following...",
        conversation_history=[...],
    )
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from typing import Any

from backend.core.config import settings

# ---------------------------------------------------------------------------
# System prompt template
# ---------------------------------------------------------------------------
_SYSTEM_TEMPLATE = """You are an expert AI trading partner for a crypto platform.
Your goal is to help the user make better trading decisions through education,
analysis, and personalised advice. You NEVER guarantee profits or give financial
advice that could be construed as regulated investment advice.

# User Profile
{user_profile}

# Market Context
{market_context}

# Relevant Skills & Knowledge
{skills_context}

Respond concisely. When discussing trades, always reference risk management.
If you lack enough context to answer confidently, say so and ask clarifying
questions.

Structure your responses with:
1. A direct answer or recommendation
2. Brief reasoning (2-3 sentences max)
3. Risk considerations"""


def _build_system_prompt(
    user_profile: dict[str, Any] | None,
    market_context: dict[str, Any] | None,
    skills_context: str,
) -> str:
    up = user_profile or {}
    mc = market_context or {}
    return _SYSTEM_TEMPLATE.format(
        user_profile="\n".join(f"- {k}: {v}" for k, v in up.items()) or "N/A",
        market_context="\n".join(f"- {k}: {v}" for k, v in mc.items()) or "N/A",
        skills_context=skills_context or "No specific skills loaded.",
    )


# ---------------------------------------------------------------------------
# Conversation history helpers
# ---------------------------------------------------------------------------
MAX_HISTORY_EXCHANGES = 10  # keep last 10 user+assistant pairs = 20 messages


def truncate_history(
    history: list[dict[str, str]],
    max_exchanges: int = MAX_HISTORY_EXCHANGES,
) -> list[dict[str, str]]:
    """Keep only the last N exchanges (user+assistant pairs).

    Each exchange = 2 messages. If history has odd count, keep the extra
    user message at the start.
    """
    max_messages = max_exchanges * 2
    if len(history) <= max_messages:
        return history
    return history[-max_messages:]


# ---------------------------------------------------------------------------
# Budget enforcement
# ---------------------------------------------------------------------------
class BudgetExceeded(Exception):
    """Raised when a user exceeds their daily AI call budget."""

    def __init__(self, user_id: int, limit: int, used: int) -> None:
        self.user_id = user_id
        self.limit = limit
        self.used = used
        super().__init__(
            f"User {user_id} exceeded daily AI budget: {used}/{limit} calls used"
        )


async def check_budget(user_id: int, db) -> int:
    """Check and increment daily AI call count. Returns calls used today.

    Uses the conversation_memory table to count today's assistant messages
    as a proxy for AI calls (no Redis required).
    """
    from sqlalchemy import select, func
    from backend.models.user import ConversationMemory

    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    result = await db.execute(
        select(func.count(ConversationMemory.id)).where(
            ConversationMemory.user_id == user_id,
            ConversationMemory.role == "assistant",
            ConversationMemory.created_at >= today_start,
        )
    )
    calls_today = result.scalar() or 0

    limit = settings.AI_CALL_BUDGET_PER_USER
    if calls_today >= limit:
        raise BudgetExceeded(user_id, limit, calls_today)

    return calls_today


# ---------------------------------------------------------------------------
# Fetch conversation history from DB
# ---------------------------------------------------------------------------
async def fetch_conversation_history(
    user_id: int,
    db,
    max_exchanges: int = MAX_HISTORY_EXCHANGES,
) -> list[dict[str, str]]:
    """Load recent conversation memory from DB, truncated to last N exchanges."""
    from sqlalchemy import select
    from backend.models.user import ConversationMemory

    max_rows = max_exchanges * 2 + 2  # fetch slightly more than needed

    result = await db.execute(
        select(ConversationMemory)
        .where(ConversationMemory.user_id == user_id)
        .order_by(ConversationMemory.created_at.desc())
        .limit(max_rows)
    )
    rows = result.scalars().all()
    rows.reverse()  # oldest first

    history = [{"role": r.role, "content": r.content} for r in rows]
    return truncate_history(history, max_exchanges)


# ---------------------------------------------------------------------------
# Fetch live market data for context
# ---------------------------------------------------------------------------
async def fetch_market_context(
    coin_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Fetch current prices and basic indicators for system prompt injection."""
    from backend.services.market.coingecko import CoinGeckoClient

    if not coin_ids:
        coin_ids = ["bitcoin", "ethereum"]

    cg = CoinGeckoClient(api_key=settings.COINGECKO_API_KEY)
    try:
        prices = await cg.get_price(coin_ids)
    except Exception:
        return {"market_data": "unavailable (API error)"}

    context: dict[str, Any] = {}
    for cid in coin_ids:
        if cid in prices:
            d = prices[cid]
            context[f"{cid}_price_usd"] = d.get("usd", "N/A")
            change = d.get("usd_24h_change")
            if change is not None:
                context[f"{cid}_24h_change"] = f"{change:+.2f}%"
            vol = d.get("usd_24h_vol")
            if vol is not None:
                context[f"{cid}_24h_volume"] = f"${vol:,.0f}"

    return context


# ---------------------------------------------------------------------------
# Provider ABC
# ---------------------------------------------------------------------------
class AIProvider(ABC):
    """Abstract base for all LLM providers."""

    @abstractmethod
    async def complete(
        self,
        system: str,
        messages: list[dict[str, str]],
        max_tokens: int = 2048,
    ) -> str:
        """Return plain text response from the LLM."""
        ...


# ---------------------------------------------------------------------------
# Groq (default) — OpenAI-compatible SDK
# ---------------------------------------------------------------------------
class GroqProvider(AIProvider):
    """Groq via AsyncOpenAI client."""

    def __init__(self, api_key: str, model: str) -> None:
        from openai import AsyncOpenAI
        self._client = AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
        )
        self._model = model

    async def complete(
        self,
        system: str,
        messages: list[dict[str, str]],
        max_tokens: int = 2048,
    ) -> str:
        all_messages = [{"role": "system", "content": system}] + messages
        response = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=all_messages,
        )
        return response.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# OpenRouter — OpenAI-compatible SDK
# ---------------------------------------------------------------------------
class OpenRouterProvider(AIProvider):
    """OpenRouter via AsyncOpenAI client."""

    def __init__(self, api_key: str, model: str) -> None:
        from openai import AsyncOpenAI
        self._client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self._model = model

    async def complete(
        self,
        system: str,
        messages: list[dict[str, str]],
        max_tokens: int = 2048,
    ) -> str:
        all_messages = [{"role": "system", "content": system}] + messages
        response = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=all_messages,
        )
        return response.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# Anthropic — native SDK
# ---------------------------------------------------------------------------
class AnthropicProvider(AIProvider):
    """Anthropic Claude via native AsyncAnthropic client."""

    def __init__(self, api_key: str, model: str) -> None:
        from anthropic import AsyncAnthropic
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = model

    async def complete(
        self,
        system: str,
        messages: list[dict[str, str]],
        max_tokens: int = 2048,
    ) -> str:
        message = await self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return message.content[0].text  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------
def _create_provider() -> AIProvider | None:
    """Instantiate the correct provider based on AI_PROVIDER env var."""
    provider = settings.AI_PROVIDER.lower()

    if provider == "groq":
        if not settings.GROQ_API_KEY:
            return None
        return GroqProvider(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
        )

    if provider == "openrouter":
        if not settings.OPENROUTER_API_KEY:
            return None
        return OpenRouterProvider(
            api_key=settings.OPENROUTER_API_KEY,
            model=settings.OPENROUTER_MODEL,
        )

    if provider == "anthropic":
        if not settings.ANTHROPIC_API_KEY:
            return None
        return AnthropicProvider(
            api_key=settings.ANTHROPIC_API_KEY,
            model=settings.ANTHROPIC_MODEL,
        )

    return None


# ---------------------------------------------------------------------------
# Brain orchestrator
# ---------------------------------------------------------------------------
class AIBrain:
    """Orchestrates LLM calls with conversation memory, budget, and market data."""

    def __init__(self) -> None:
        self._provider = _create_provider()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def ask(
        self,
        user_id: int,
        user_message: str,
        user_profile: dict[str, Any] | None = None,
        market_context: dict[str, Any] | None = None,
        skills_context: str = "",
        conversation_history: list[dict[str, str]] | None = None,
    ) -> str:
        """Send a user message to the active provider and return plain text.

        Now supports:
        - conversation_history: prior messages injected for multi-turn context
        - market_context: live price data in system prompt
        """
        if self._provider is None:
            return (
                f"[MOCK RESPONSE — no API key set for provider '{settings.AI_PROVIDER}']\n"
                f"You asked: {user_message}\n"
                f"Profile: {user_profile}\n"
                f"Market: {market_context}"
            )

        system = _build_system_prompt(user_profile, market_context, skills_context)

        messages: list[dict[str, str]] = []
        if conversation_history:
            messages.extend(truncate_history(conversation_history))
        messages.append({"role": "user", "content": user_message})

        return await self._provider.complete(system, messages)

    async def suggest_trades(
        self,
        user_id: int,
        user_profile: dict[str, Any] | None = None,
        market_context: dict[str, Any] | None = None,
        skills_context: str = "",
        conversation_history: list[dict[str, str]] | None = None,
    ) -> str:
        """Ask the LLM to generate trade ideas."""
        prompt = (
            "Based on the user profile, current market context, and the skills below, "
            "generate 1–3 high-quality trade ideas. For each idea include:\n"
            "- Asset & direction (long/short)\n"
            "- Entry trigger\n"
            "- Stop loss\n"
            "- Take profit target(s)\n"
            "- Rationale (1 sentence)\n"
            "- Risk note\n\n"
            "Only suggest ideas that align with the user's risk profile and experience."
        )
        return await self.ask(
            user_id=user_id,
            user_message=prompt,
            user_profile=user_profile,
            market_context=market_context,
            skills_context=skills_context,
            conversation_history=conversation_history,
        )
