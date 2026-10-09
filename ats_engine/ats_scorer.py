from utils.logger import get_logger

logger = get_logger(__name__)


def calculate_ats_score(candidate_skills, required_skills):
    """
    Compare candidate skills with required job skills.

    Returns a score, matched skills, and missing skills.
    """

    if not required_skills:
        raise ValueError("Required skills cannot be empty.")

    candidate_set = {
        skill.strip().lower() for skill in candidate_skills
    }

    required_set = {
        skill.strip().lower() for skill in required_skills
    }

    matched_skills = sorted(candidate_set & required_set)
    missing_skills = sorted(required_set - candidate_set)

    score = round(
        len(matched_skills) / len(required_set) * 100, 2
    )

    logger.info("ATS score calculated: %.2f%%", score)

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }