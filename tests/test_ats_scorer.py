import pytest

from ats_engine.ats_scorer import calculate_ats_score


def test_all_skills_matched():
    result = calculate_ats_score(
        ["Python", "SQL"],
        ["Python", "SQL"]
    )

    assert result["score"] == 100.0
    assert result["missing_skills"] == []


def test_partial_skill_match():
    result = calculate_ats_score(
        ["Python"],
        ["Python", "SQL"]
    )

    assert result["score"] == 50.0
    assert result["missing_skills"] == ["sql"]


def test_empty_requirements():
    with pytest.raises(ValueError):
        calculate_ats_score(["Python"], [])