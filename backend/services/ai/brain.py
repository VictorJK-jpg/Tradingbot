"""Provider-agnostic AI Brain — Groq (default), OpenRouter, Anthropic.

Usage:
    from backend.services.ai.brain import AIBrain
    brain = AIBrain()
    response = await brain.ask(
        user_id=1,
        user_message="Should I long BTC here?",
        user_profile={"style": "swing_trader"},
        market_context={"btc_price": 65000},
        skills_context="[STRATEGIES] Trend Following...",
    )

All providers return plain text strings in identical format.
"""

from abc import ABC, abstractmethod
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
questions."""


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
# Provider ABC
# ---------------------------------------------------------------------------
class AIProvider(ABC):
    """Abstract base for all LLM providers."""

    @abstractmethod
    async def complete(self, system: str, user_message: str, max_tokens: int = 2048) -> str:
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

    async def complete(self, system: str, user_message: str, max_tokens: int = 2048) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message},
            ],
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

    async def complete(self, system: str, user_message: str, max_tokens: int = 2048) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message},
            ],
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

    async def complete(self, system: str, user_message: str, max_tokens: int = 2048) -> str:
        message = await self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_message}],
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
    """Orchestrates LLM calls. Falls back to mock responses if no key is set."""

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
    ) -> str:
        """Send a user message to the active provider and return plain text."""
        if self._provider is None:
            return (
                f"[MOCK RESPONSE — no API key set for provider '{settings.AI_PROVIDER}']\n"
                f"You asked: {user_message}\n"
                f"Profile: {user_profile}\n"
                f"Market: {market_context}"
            )

        system = _build_system_prompt(user_profile, market_context, skills_context)
        return await self._provider.complete(system, user_message)

    async def suggest_trades(
        self,
        user_id: int,
        user_profile: dict[str, Any] | None = None,
        market_context: dict[str, Any] | None = None,
        skills_context: str = "",
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
        )
