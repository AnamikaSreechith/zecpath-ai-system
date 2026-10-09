import pytest

from scoring.decision_engine import make_preliminary_recommendation


def test_high_score():
    assert make_preliminary_recommendation(85) == "REVIEW_FOR_SHORTLIST"


def test_medium_score():
    assert make_preliminary_recommendation(60) == "FURTHER_REVIEW"


def test_low_score():
    assert make_preliminary_recommendation(30) == "REVIEW_GAPS"


def test_invalid_score():
    with pytest.raises(ValueError):
        make_preliminary_recommendation(120)