DEFAULT_SHORTLIST_THRESHOLD = 80
DEFAULT_REVIEW_THRESHOLD = 50


def validate_candidate(candidate):
    """
    Validate that a candidate contains a valid score.
    """

    if not isinstance(candidate, dict):
        raise ValueError("Candidate must be a dictionary.")

    if "candidate_id" not in candidate:
        raise ValueError("Candidate must contain candidate_id.")

    if "score" not in candidate:
        raise ValueError("Candidate must contain score.")

    try:
        score = float(candidate["score"])
    except (TypeError, ValueError):
        raise ValueError("Candidate score must be numeric.")

    if score < 0 or score > 100:
        raise ValueError("Candidate score must be between 0 and 100.")

    return True


def classify_candidate_status(
    score,
    shortlist_threshold=DEFAULT_SHORTLIST_THRESHOLD,
    review_threshold=DEFAULT_REVIEW_THRESHOLD
):
    """
    Classify a candidate into Shortlisted, Review, or Rejected.
    """

    if score >= shortlist_threshold:
        return "Shortlisted"

    elif score >= review_threshold:
        return "Review"

    return "Rejected"


def rank_candidates(candidates):
    """
    Rank candidates based on their ATS score.

    Candidates are sorted from highest score
    to lowest score.
    """

    if not candidates:
        return []

    for candidate in candidates:
        validate_candidate(candidate)

    sorted_candidates = sorted(
        candidates,
        key=lambda candidate: float(candidate["score"]),
        reverse=True
    )

    ranked_candidates = []

    for rank, candidate in enumerate(
        sorted_candidates,
        start=1
    ):
        ranked_candidate = candidate.copy()

        ranked_candidate["rank"] = rank

        ranked_candidates.append(
            ranked_candidate
        )

    return ranked_candidates


def shortlist_candidates(
    candidates,
    shortlist_threshold=DEFAULT_SHORTLIST_THRESHOLD,
    review_threshold=DEFAULT_REVIEW_THRESHOLD
):
    """
    Rank candidates and assign each candidate
    to a recruitment decision zone.
    """

    ranked_candidates = rank_candidates(
        candidates
    )

    results = []

    for candidate in ranked_candidates:

        score = float(
            candidate["score"]
        )

        candidate_result = candidate.copy()

        candidate_result["status"] = (
            classify_candidate_status(
                score,
                shortlist_threshold,
                review_threshold
            )
        )

        results.append(
            candidate_result
        )

    return results


def get_top_candidates(
    candidates,
    limit=5
):
    """
    Return the top N candidates based on ATS score.
    """

    if limit <= 0:
        return []

    ranked_candidates = rank_candidates(
        candidates
    )

    return ranked_candidates[:limit]


def get_shortlisted_candidates(
    candidates,
    shortlist_threshold=DEFAULT_SHORTLIST_THRESHOLD
):
    """
    Return candidates who meet the shortlist threshold.
    """

    ranked_candidates = shortlist_candidates(
        candidates,
        shortlist_threshold=shortlist_threshold
    )

    return [
        candidate
        for candidate in ranked_candidates
        if candidate["status"] == "Shortlisted"
    ]


def get_review_candidates(
    candidates,
    shortlist_threshold=DEFAULT_SHORTLIST_THRESHOLD,
    review_threshold=DEFAULT_REVIEW_THRESHOLD
):
    """
    Return candidates who require recruiter review.
    """

    ranked_candidates = shortlist_candidates(
        candidates,
        shortlist_threshold,
        review_threshold
    )

    return [
        candidate
        for candidate in ranked_candidates
        if candidate["status"] == "Review"
    ]


def get_rejected_candidates(
    candidates,
    review_threshold=DEFAULT_REVIEW_THRESHOLD
):
    """
    Return candidates below the review threshold.
    """

    ranked_candidates = shortlist_candidates(
        candidates,
        review_threshold=review_threshold
    )

    return [
        candidate
        for candidate in ranked_candidates
        if candidate["status"] == "Rejected"
    ]