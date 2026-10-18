import pytest

from parsers.skill_extraction_engine import (
    normalize_text,
    find_skill_mentions,
    expand_skill_stacks,
    calculate_confidence,
    extract_skills,
)


def test_normalize_text():
    result = normalize_text("  Python   Developer  ")

    assert result == "python developer"


def test_find_python_skill():
    skills = find_skill_mentions(
        "Experienced Python developer"
    )

    assert "Python" in skills


def test_skill_synonym():
    skills = find_skill_mentions(
        "Strong knowledge of Python programming"
    )

    assert "Python" in skills


def test_aws_synonym():
    skills = find_skill_mentions(
        "Experience with Amazon Web Services"
    )

    assert "AWS" in skills


def test_fastapi_synonym():
    skills = find_skill_mentions(
        "Experience with Fast API"
    )

    assert "FastAPI" in skills


def test_rest_api_synonym():
    skills = find_skill_mentions(
        "Knowledge of RESTful APIs"
    )

    assert "REST APIs" in skills


def test_mern_stack_expansion():
    skills = expand_skill_stacks(
        [],
        "Experienced with MERN stack"
    )

    assert "MongoDB" in skills
    assert "Express.js" in skills
    assert "React" in skills
    assert "Node.js" in skills


def test_mean_stack_expansion():
    skills = expand_skill_stacks(
        [],
        "Experienced with MEAN stack"
    )

    assert "MongoDB" in skills
    assert "Express.js" in skills
    assert "Angular" in skills
    assert "Node.js" in skills


def test_duplicate_removal():
    skills = extract_skills(
        "Python Python Python SQL SQL"
    )

    skill_names = [
        skill["name"]
        for skill in skills
    ]

    assert skill_names.count("Python") == 1
    assert skill_names.count("SQL") == 1


def test_confidence_score():
    confidence = calculate_confidence(
        "Python",
        "Experienced Python developer"
    )

    assert confidence >= 0.90
    assert confidence <= 1.0


def test_structured_skill_output():
    skills = extract_skills(
        "Python, SQL, Fast API and AWS"
    )

    assert len(skills) == 4

    for skill in skills:
        assert "name" in skill
        assert "category" in skill
        assert "confidence" in skill

        assert 0.0 <= skill["confidence"] <= 1.0


def test_realistic_resume_skills():
    text = """
    Technical Skills:
    Python Programming
    SQL
    Fast API
    Amazon Web Services
    Git
    MERN Stack

    Soft Skills:
    Communication Skills
    Leadership
    """

    skills = extract_skills(text)

    skill_names = [
        skill["name"]
        for skill in skills
    ]

    assert "Python" in skill_names
    assert "SQL" in skill_names
    assert "FastAPI" in skill_names
    assert "AWS" in skill_names
    assert "Git" in skill_names

    assert "MongoDB" in skill_names
    assert "Express.js" in skill_names
    assert "React" in skill_names
    assert "Node.js" in skill_names

    assert "Communication" in skill_names
    assert "Leadership" in skill_names