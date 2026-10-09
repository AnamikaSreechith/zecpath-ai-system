from utils.logger import get_logger

logger = get_logger(__name__)


def evaluate_screening_response(answer, required_keywords):
    """Match required keywords against a candidate's answer."""

    if not answer or not answer.strip():
        raise ValueError("Screening answer cannot be empty.")

    matched_keywords = [
        keyword
        for keyword in required_keywords
        if keyword.lower() in answer.lower()
    ]

    logger.info("Screening response processed")

    return {
        "matched_keywords": matched_keywords,
        "keyword_match_count": len(matched_keywords)
    }