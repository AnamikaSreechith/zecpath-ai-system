from utils.logger import get_logger

logger = get_logger(__name__)


def parse_resume_text(text):
    """Validate resume text and return a basic structured result."""

    if not text or not text.strip():
        raise ValueError("Resume text cannot be empty.")

    logger.info("Resume text received for parsing")

    return {
        "raw_text": text.strip(),
        "status": "received"
    }