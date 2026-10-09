from utils.logger import get_logger

logger = get_logger(__name__)


def make_preliminary_recommendation(score):
    """Generate a preliminary recommendation from a score."""

    if not 0 <= score <= 100:
        raise ValueError("Score must be between 0 and 100.")

    if score >= 75:
        recommendation = "REVIEW_FOR_SHORTLIST"
    elif score >= 50:
        recommendation = "FURTHER_REVIEW"
    else:
        recommendation = "REVIEW_GAPS"

    logger.info("Preliminary recommendation generated")

    return recommendation