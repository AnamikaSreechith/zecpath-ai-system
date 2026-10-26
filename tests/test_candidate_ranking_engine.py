from matching.candidate_ranking_engine import (
    rank_candidates,
    classify_candidate_status,
    shortlist_candidates,
    get_top_candidates,
    get_shortlisted_candidates,
    get_review_candidates,
    get_rejected_candidates
)


def test_rank_candidates():

    candidates = [
        {"candidate_id": "CAND-001", "score": 72},
        {"candidate_id": "CAND-002", "score": 91},
        {"candidate_id": "CAND-003", "score": 85}
    ]

    result = rank_candidates(candidates)

    assert result[0]["candidate_id"] == "CAND-002"
    assert result[0]["rank"] == 1

    assert result[1]["candidate_id"] == "CAND-003"
    assert result[1]["rank"] == 2

    assert result[2]["candidate_id"] == "CAND-001"
    assert result[2]["rank"] == 3


def test_classify_candidate_status():

    assert classify_candidate_status(85) == "Shortlisted"
    assert classify_candidate_status(65) == "Review"
    assert classify_candidate_status(40) == "Rejected"


def test_shortlist_candidates():

    candidates = [
        {"candidate_id": "CAND-001", "score": 85},
        {"candidate_id": "CAND-002", "score": 65},
        {"candidate_id": "CAND-003", "score": 40}
    ]

    result = shortlist_candidates(candidates)

    assert result[0]["status"] == "Shortlisted"
    assert result[1]["status"] == "Review"
    assert result[2]["status"] == "Rejected"


def test_get_top_candidates():

    candidates = [
        {"candidate_id": "CAND-001", "score": 70},
        {"candidate_id": "CAND-002", "score": 95},
        {"candidate_id": "CAND-003", "score": 85}
    ]

    result = get_top_candidates(
        candidates,
        limit=2
    )

    assert len(result) == 2
    assert result[0]["candidate_id"] == "CAND-002"
    assert result[1]["candidate_id"] == "CAND-003"


def test_get_shortlisted_candidates():

    candidates = [
        {"candidate_id": "CAND-001", "score": 85},
        {"candidate_id": "CAND-002", "score": 65},
        {"candidate_id": "CAND-003", "score": 40}
    ]

    result = get_shortlisted_candidates(
        candidates
    )

    assert len(result) == 1
    assert result[0]["candidate_id"] == "CAND-001"


def test_get_review_candidates():

    candidates = [
        {"candidate_id": "CAND-001", "score": 85},
        {"candidate_id": "CAND-002", "score": 65},
        {"candidate_id": "CAND-003", "score": 40}
    ]

    result = get_review_candidates(
        candidates
    )

    assert len(result) == 1
    assert result[0]["candidate_id"] == "CAND-002"


def test_get_rejected_candidates():

    candidates = [
        {"candidate_id": "CAND-001", "score": 85},
        {"candidate_id": "CAND-002", "score": 65},
        {"candidate_id": "CAND-003", "score": 40}
    ]

    result = get_rejected_candidates(
        candidates
    )

    assert len(result) == 1
    assert result[0]["candidate_id"] == "CAND-003"