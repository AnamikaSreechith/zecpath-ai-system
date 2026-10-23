from matching.ats_scoring_engine import (
    calculate_candidate_score,
    generate_candidate_score,
    classify_candidate,
    validate_weights
)


def test_calculate_candidate_score():
    score = calculate_candidate_score(
        skill_match=0.80,
        experience_relevance=0.90,
        education_alignment=0.75,
        semantic_similarity=0.85
    )

    assert score == 82.75


def test_generate_candidate_score():
    result = generate_candidate_score(
        skill_match=0.80,
        experience_relevance=0.90,
        education_alignment=0.75,
        semantic_similarity=0.85
    )

    assert result["final_score"] == 82.75
    assert result["match_level"] == "Excellent Match"

    assert result["score_breakdown"]["skill_match"] == 80.0
    assert result["score_breakdown"]["experience_relevance"] == 90.0
    assert result["score_breakdown"]["education_alignment"] == 75.0
    assert result["score_breakdown"]["semantic_similarity"] == 85.0


def test_custom_weights():

    weights = {
        "skill_match": 0.40,
        "experience_relevance": 0.30,
        "education_alignment": 0.10,
        "semantic_similarity": 0.20
    }

    score = calculate_candidate_score(
        skill_match=0.90,
        experience_relevance=0.80,
        education_alignment=0.70,
        semantic_similarity=0.85,
        weights=weights
    )

    assert score == 84.0


def test_missing_data():

    result = generate_candidate_score(
        skill_match=0.80,
        experience_relevance=None,
        education_alignment=0.70,
        semantic_similarity=0.90
    )

    assert result["score_breakdown"]["experience_relevance"] == 0.0
    assert result["final_score"] == 60.5


def test_invalid_weights():

    invalid_weights = {
        "skill_match": 0.50,
        "experience_relevance": 0.30,
        "education_alignment": 0.20,
        "semantic_similarity": 0.20
    }

    try:
        validate_weights(invalid_weights)
        assert False
    except ValueError:
        assert True


def test_match_classification():

    assert classify_candidate(85) == "Excellent Match"
    assert classify_candidate(70) == "Good Match"
    assert classify_candidate(55) == "Moderate Match"
    assert classify_candidate(40) == "Low Match"