from matching.ats_scoring_engine import (
    generate_candidate_score
)

from matching.candidate_ranking_engine import (
    shortlist_candidates
)


def calculate_ats_score(
    skill_match,
    experience_relevance,
    education_alignment,
    semantic_similarity
):
    """
    Generate an ATS score using the existing
    ATS scoring engine.
    """

    return generate_candidate_score(
        skill_match=skill_match,
        experience_relevance=experience_relevance,
        education_alignment=education_alignment,
        semantic_similarity=semantic_similarity
    )


def rank_and_shortlist(candidates):
    """
    Rank and shortlist candidates using the
    existing candidate ranking engine.
    """

    return shortlist_candidates(candidates)