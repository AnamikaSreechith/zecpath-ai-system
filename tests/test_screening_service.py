import pytest

from screening_ai.screening_service import (
    evaluate_screening_response
)


def test_screening_keyword_match():
    result = evaluate_screening_response(
        "I have experience in Python and SQL",
        ["Python", "SQL", "AWS"]
    )

    assert result["matched_keywords"] == ["Python", "SQL"]
    assert result["keyword_match_count"] == 2


def test_empty_screening_answer():
    with pytest.raises(ValueError):
        evaluate_screening_response("", ["Python"])


def test_no_keywords_matched():
    result = evaluate_screening_response(
        "I enjoy working with people",
        ["Python", "SQL"]
    )

    assert result["matched_keywords"] == []
    assert result["keyword_match_count"] == 0