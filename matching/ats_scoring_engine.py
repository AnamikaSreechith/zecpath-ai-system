DEFAULT_WEIGHTS = {
    "skill_match": 0.30,
    "experience_relevance": 0.25,
    "education_alignment": 0.20,
    "semantic_similarity": 0.25
}


def validate_weights(weights):
    """
    Validate that ATS scoring weights are valid
    and add up to 1.0.
    """

    required_keys = {
        "skill_match",
        "experience_relevance",
        "education_alignment",
        "semantic_similarity"
    }

    if set(weights.keys()) != required_keys:
        raise ValueError(
            "Weights must contain all required scoring parameters."
        )

    if any(
        weight < 0 or weight > 1
        for weight in weights.values()
    ):
        raise ValueError(
            "Each weight must be between 0 and 1."
        )

    if round(sum(weights.values()), 4) != 1.0:
        raise ValueError(
            "Weights must add up to 1.0."
        )

    return True


def get_score(value):
    """
    Return a valid score between 0 and 1.
    Missing values are treated as 0.
    """

    if value is None:
        return 0.0

    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0

    return max(0.0, min(score, 1.0))


def calculate_candidate_score(
    skill_match,
    experience_relevance,
    education_alignment,
    semantic_similarity,
    weights=None
):
    """
    Calculate the final ATS candidate score.
    """

    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()

    validate_weights(weights)

    skill_score = get_score(skill_match)

    experience_score = get_score(
        experience_relevance
    )

    education_score = get_score(
        education_alignment
    )

    semantic_score = get_score(
        semantic_similarity
    )

    final_score = (
        skill_score * weights["skill_match"]
        + experience_score * weights["experience_relevance"]
        + education_score * weights["education_alignment"]
        + semantic_score * weights["semantic_similarity"]
    )

    return round(
        final_score * 100,
        2
    )


def generate_candidate_score(
    skill_match,
    experience_relevance,
    education_alignment,
    semantic_similarity,
    weights=None
):
    """
    Generate an explainable ATS candidate score.
    """

    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()

    final_score = calculate_candidate_score(
        skill_match,
        experience_relevance,
        education_alignment,
        semantic_similarity,
        weights
    )

    return {
        "final_score": final_score,

        "match_level": classify_candidate(
            final_score
        ),

        "score_breakdown": {
            "skill_match": round(
                get_score(skill_match) * 100,
                2
            ),

            "experience_relevance": round(
                get_score(experience_relevance) * 100,
                2
            ),

            "education_alignment": round(
                get_score(education_alignment) * 100,
                2
            ),

            "semantic_similarity": round(
                get_score(semantic_similarity) * 100,
                2
            )
        },

        "weights": weights
    }


def classify_candidate(score):
    """
    Classify a candidate based on the final ATS score.
    """

    if score >= 80:
        return "Excellent Match"

    elif score >= 65:
        return "Good Match"

    elif score >= 50:
        return "Moderate Match"

    else:
        return "Low Match"