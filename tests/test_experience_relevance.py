from scoring.experience_relevance import (
    normalize_role,
    calculate_role_similarity,
    calculate_experience_relevance,
)


def test_normalize_role():
    result = normalize_role(
        "  Python   Developer  "
    )

    assert result == "python developer"


def test_exact_role_similarity():
    score = calculate_role_similarity(
        "Python Developer",
        "Python Developer"
    )

    assert score == 1.0


def test_partial_role_similarity():
    score = calculate_role_similarity(
        "Python Developer",
        "Python Developer Intern"
    )

    assert score > 0.0
    assert score < 1.0


def test_no_role_similarity():
    score = calculate_role_similarity(
        "Graphic Designer",
        "Python Developer"
    )

    assert score == 0.0


def test_experience_relevance():
    experiences = [
        {
            "company": "ABC Technologies",
            "job_title": "Python Developer",
            "duration_months": 12
        }
    ]

    result = calculate_experience_relevance(
        experiences,
        "Python Developer"
    )

    assert result["target_role"] == "Python Developer"
    assert result["relevance_score"] == 1.0
    assert len(result["relevant_roles"]) == 1


def test_no_experience():
    result = calculate_experience_relevance(
        [],
        "Python Developer"
    )

    assert result["relevance_score"] == 0.0
    assert result["relevant_roles"] == []