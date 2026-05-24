"""Tests for backend/services/skills_engine.py"""

import pytest
from backend.services.skills_engine import SkillsEngine, _parse_skill, _skill_path
from pathlib import Path


class TestSkillsEngine:
    """Test SkillsEngine methods."""

    def test_get_available_skills_returns_list(self):
        """get_available_skills should return a list of skill metadata."""
        skills = SkillsEngine.get_available_skills()
        assert isinstance(skills, list)
        assert len(skills) > 0

    def test_get_available_skills_structure(self):
        """Each skill should have required metadata fields."""
        skills = SkillsEngine.get_available_skills()
        required_fields = {"category", "name", "title", "description", "tags"}

        for skill in skills:
            assert required_fields.issubset(skill.keys()), f"Missing fields in {skill}"
            assert isinstance(skill["tags"], list)

    def test_match_skills_with_matching_message(self):
        """match_skills should return content for relevant messages."""
        result = SkillsEngine.match_skills("trend following strategy")
        assert isinstance(result, str)
        assert len(result) > 0
        assert "trend" in result.lower() or "strategy" in result.lower()

    def test_match_skills_with_no_match(self):
        """match_skills should return empty string for no matches."""
        result = SkillsEngine.match_skills("xyz123 random nonsense abc")
        assert result == ""

    def test_match_skills_with_empty_string(self):
        """match_skills should return empty string for empty input."""
        result = SkillsEngine.match_skills("")
        assert result == ""

    def test_match_skills_whitespace_only(self):
        """match_skills should return empty string for whitespace."""
        result = SkillsEngine.match_skills("   ")
        assert result == ""

    def test_match_skills_max_3_skills(self):
        """match_skills should return at most 3 skills."""
        test_messages = [
            "strategy technical momentum swing trading risk leverage",
            "on-chain metrics funding rate MVRV SOPR support resistance",
        ]

        for msg in test_messages:
            result = SkillsEngine.match_skills(msg)
            skill_headers = result.count("# [")
            assert skill_headers <= 3, f"Expected max 3 skills, got {skill_headers}"

    def test_load_single_skill(self):
        """load() should return markdown body for valid skill."""
        body = SkillsEngine.load("strategies", "trend_following")
        assert isinstance(body, str)
        assert len(body) > 0

    def test_load_invalid_category_raises(self):
        """load() should raise ValueError for invalid category."""
        with pytest.raises(ValueError):
            SkillsEngine.load("invalid_category", "trend_following")

    def test_load_nonexistent_skill_raises(self):
        """load() should raise FileNotFoundError for missing skill."""
        with pytest.raises(FileNotFoundError):
            SkillsEngine.load("strategies", "nonexistent_skill")

    def test_load_with_meta(self):
        """load_with_meta() should return (meta, body) tuple."""
        meta, body = SkillsEngine.load_with_meta("risk_management", "position_sizing")
        assert isinstance(meta, dict)
        assert isinstance(body, str)
        assert "position" in meta.get("title", "").lower()

    def test_load_multi(self):
        """load_multi() should concatenate multiple skills."""
        selections = [
            {"category": "strategies", "name": "trend_following"},
            {"category": "risk_management", "name": "position_sizing"},
        ]
        result = SkillsEngine.load_multi(selections)
        assert isinstance(result, str)
        assert "trend" in result.lower()
        assert "position" in result.lower()

    def test_list_skills(self):
        """list_skills() should return skill names for category."""
        skills = SkillsEngine.list_skills("strategies")
        assert isinstance(skills, list)
        assert "trend_following" in skills

    def test_list_skills_invalid_category_raises(self):
        """list_skills() should raise ValueError for invalid category."""
        with pytest.raises(ValueError):
            SkillsEngine.list_skills("invalid_category")

    def test_load_category(self):
        """load_category() should load all skills in category."""
        result = SkillsEngine.load_category("strategies")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_load_all(self):
        """load_all() should load all skills across categories."""
        result = SkillsEngine.load_all()
        assert isinstance(result, str)
        assert "CATEGORY:" in result or "strategies" in result.lower()


class TestParseSkill:
    """Test _parse_skill helper function."""

    def test_parse_skill_with_yaml_frontmatter(self):
        """Should parse YAML frontmatter and body correctly."""
        import tempfile
        content = """---
title: Test Skill
tags: [test, sample]
---
# Body content
Some text here.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            meta, body = _parse_skill(path)
            assert meta["title"] == "Test Skill"
            assert "test" in meta["tags"]
            assert "Body content" in body
        finally:
            path.unlink()

    def test_parse_skill_without_frontmatter(self):
        """Should handle files without YAML frontmatter."""
        import tempfile
        content = "Plain markdown without frontmatter."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        try:
            meta, body = _parse_skill(path)
            assert meta == {}
            assert body == content
        finally:
            path.unlink()