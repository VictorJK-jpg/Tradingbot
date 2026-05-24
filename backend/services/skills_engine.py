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
"""

from pathlib import Path
from typing import Iterable

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
    # Metadata and matching
    # ------------------------------------------------------------------
    @staticmethod
    def get_available_skills() -> list[dict]:
        """Return metadata for all skills without loading content.

        Returns: list of {"category": str, "name": str, "title": str,
                         "description": str, "tags": list[str]}
        """
        results: list[dict] = []
        for category in sorted(_VALID_CATEGORIES):
            folder = _SKILLS_BASE / category
            if not folder.exists():
                continue
            for skill_dir in sorted(folder.iterdir()):
                if not skill_dir.is_dir():
                    continue
                skill_path = skill_dir / "SKILL.md"
                if not skill_path.exists():
                    continue
                meta, _ = _parse_skill(skill_path)
                results.append({
                    "category": category,
                    "name": skill_dir.name,
                    "title": meta.get("title", skill_dir.name.replace("_", " ").title()),
                    "description": meta.get("description", ""),
                    "tags": meta.get("tags", []),
                })
        return results

    @staticmethod
    def match_skills(user_message: str) -> str:
        """Intelligently match user message to relevant skills.

        Scans YAML frontmatter only (tags, title, description).
        Scores by keyword matches (tags weighted 2x).
        Returns top 3 skills max as concatenated content.
        Returns empty string if no matches.
        """
        if not user_message.strip():
            return ""

        user_words = set(user_message.lower().split())
        scored: list[tuple[float, dict]] = []

        for skill in SkillsEngine.get_available_skills():
            score = 0.0
            title = skill["title"].lower()
            desc = skill["description"].lower()
            tags = [t.lower() for t in skill["tags"]]

            for word in user_words:
                if word in title:
                    score += 1
                if word in desc:
                    score += 0.5
                if any(word in tag for tag in tags):
                    score += 2

            if score > 0:
                scored.append((score, skill))

        if not scored:
            return ""

        scored.sort(key=lambda x: x[0], reverse=True)
        top_skills = scored[:3]

        selections = [
            {"category": s[1]["category"], "name": s[1]["name"]}
            for s in top_skills
        ]
        return SkillsEngine.load_multi(selections)
