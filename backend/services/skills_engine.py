"""SkillsEngine — load SKILL.md files using Anthropic folder structure.

Folder layout:
    skills/
      <category>/
        <skill-name>/
          SKILL.md        ← YAML frontmatter + markdown body

Usage:
    engine = SkillsEngine()
    context = engine.load("strategies", "trend_following")
    multi = engine.load_multi([
        {"category": "strategies", "name": "trend_following"},
        {"category": "risk_management", "name": "position_sizing"},
    ])
    matched = engine.match_skills("Should I long BTC with proper risk?")
    metadata = engine.get_available_skills()
"""

from pathlib import Path
from typing import Iterable
import re

import yaml

_SKILLS_BASE = Path(__file__).resolve().parent.parent / "skills"

_VALID_CATEGORIES = {
    "strategies",
    "risk_management",
    "market_reading",
    "fundamental",
    "weekly_outlook",
}


def _skill_path(category: str, name: str) -> Path:
    if category not in _VALID_CATEGORIES:
        raise ValueError(f"Invalid category '{category}'. Must be one of: {_VALID_CATEGORIES}")
    return _SKILLS_BASE / category / name / "SKILL.md"


def _parse_skill(path: Path) -> tuple[dict, str]:
    """Parse a SKILL.md file. Returns (frontmatter_dict, body_text)."""
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("---"):
        _, front, body = raw.split("---", 2)
        meta = yaml.safe_load(front.strip()) or {}
        return meta, body.strip()
    return {}, raw.strip()


class SkillsEngine:
    """Loads SKILL.md files and formats them as AI context strings."""

    # ------------------------------------------------------------------
    # Single skill
    # ------------------------------------------------------------------
    @staticmethod
    def load(category: str, name: str) -> str:
        """Return the markdown body of a single skill file."""
        path = _skill_path(category, name)
        if not path.exists():
            raise FileNotFoundError(f"Skill not found: {path}")
        _, body = _parse_skill(path)
        return body

    @staticmethod
    def load_with_meta(category: str, name: str) -> tuple[dict, str]:
        """Return (frontmatter, body) for a single skill."""
        path = _skill_path(category, name)
        if not path.exists():
            raise FileNotFoundError(f"Skill not found: {path}")
        return _parse_skill(path)

    # ------------------------------------------------------------------
    # Multiple skills
    # ------------------------------------------------------------------
    @staticmethod
    def load_multi(selections: Iterable[dict[str, str]]) -> str:
        """Load several skills and concatenate them with headers.

        selections: list of {"category": "...", "name": "..."}
        """
        parts: list[str] = []
        for item in selections:
            cat = item["category"]
            name = item["name"]
            meta, body = SkillsEngine.load_with_meta(cat, name)
            title = meta.get("title", name.replace("_", " ").title())
            parts.append(f"# [{cat.upper()}] {title}\n\n{body}")
        return "\n\n---\n\n".join(parts)

    # ------------------------------------------------------------------
    # Discovery helpers
    # ------------------------------------------------------------------
    @staticmethod
    def list_skills(category: str) -> list[str]:
        """Return sorted skill folder names (not file names) in a category."""
        if category not in _VALID_CATEGORIES:
            raise ValueError(f"Invalid category '{category}'.")
        folder = _SKILLS_BASE / category
        if not folder.exists():
            return []
        return sorted(
            p.name for p in folder.iterdir() if p.is_dir() and (p / "SKILL.md").exists()
        )

    @staticmethod
    def load_category(category: str) -> str:
        """Load every skill in a category and concatenate them."""
        names = SkillsEngine.list_skills(category)
        if not names:
            return ""
        selections = [{"category": category, "name": n} for n in names]
        return SkillsEngine.load_multi(selections)

    @staticmethod
    def load_all() -> str:
        """Load every skill across all categories."""
        parts: list[str] = []
        for category in sorted(_VALID_CATEGORIES):
            chunk = SkillsEngine.load_category(category)
            if chunk:
                parts.append(f"## CATEGORY: {category.upper().replace('_', ' ')}\n\n{chunk}")
        return "\n\n===\n\n".join(parts)

    # ------------------------------------------------------------------
    # Metadata discovery (no content loading)
    # ------------------------------------------------------------------
    @staticmethod
    def get_available_skills() -> list[dict]:
        """Return metadata for all skills without loading full content.

        Returns list of: {
            "category": str,
            "name": str,
            "title": str,
            "description": str,
            "tags": list[str],
        }
        """
        skills: list[dict] = []
        for category in sorted(_VALID_CATEGORIES):
            folder = _SKILLS_BASE / category
            if not folder.exists():
                continue
            for skill_folder in folder.iterdir():
                if not skill_folder.is_dir():
                    continue
                skill_file = skill_folder / "SKILL.md"
                if not skill_file.exists():
                    continue
                try:
                    meta, _ = _parse_skill(skill_file)
                    skills.append({
                        "category": category,
                        "name": skill_folder.name,
                        "title": meta.get("title", skill_folder.name.replace("_", " ").title()),
                        "description": meta.get("description", ""),
                        "tags": meta.get("tags", []),
                    })
                except Exception:
                    # Skip malformed skill files
                    continue
        return skills

    # ------------------------------------------------------------------
    # Intelligent matching
    # ------------------------------------------------------------------
    @staticmethod
    def match_skills(user_message: str) -> str:
        """Match user message against skill metadata and return top 3 skills.

        Logic:
        1. Scan YAML frontmatter only (tags, title, description)
        2. Score each skill by keyword matches
        3. Return top 3 skills max
        4. If no matches, return empty string

        Args:
            user_message: The user's query/message

        Returns:
            Formatted context string with matched skills, or empty string
        """
        # Normalize user message for matching
        user_lower = user_message.lower()
        user_words = set(re.findall(r"\b\w+\b", user_lower))

        if not user_words:
            return ""

        # Get all skill metadata
        all_skills = SkillsEngine.get_available_skills()

        # Score each skill
        scored_skills: list[tuple[int, dict]] = []
        for skill in all_skills:
            score = 0

            # Match against tags
            for tag in skill.get("tags", []):
                if tag.lower() in user_lower:
                    score += 2  # Tags are weighted higher

            # Match against title words
            title_words = set(re.findall(r"\b\w+\b", skill["title"].lower()))
            if user_words & title_words:  # Intersection
                score += len(user_words & title_words)

            # Match against description words
            desc_words = set(re.findall(r"\b\w+\b", skill["description"].lower()))
            if user_words & desc_words:  # Intersection
                score += len(user_words & desc_words)

            if score > 0:
                scored_skills.append((score, skill))

        # Sort by score descending
        scored_skills.sort(key=lambda x: x[0], reverse=True)

        # Take top 3 max
        top_skills = scored_skills[:3]

        if not top_skills:
            return ""

        # Load and format the matched skills
        selections = [
            {"category": s["category"], "name": s["name"]}
            for _, s in top_skills
        ]
        return SkillsEngine.load_multi(selections)
