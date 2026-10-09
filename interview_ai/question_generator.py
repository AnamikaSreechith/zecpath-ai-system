from utils.logger import get_logger

logger = get_logger(__name__)


def generate_sample_questions(role):
    """Generate basic interview questions for a job role."""

    if not role or not role.strip():
        raise ValueError("Job role cannot be empty.")

    logger.info("Generating sample questions for role: %s", role)

    questions = [
        f"What are the main responsibilities of a {role}?",
        f"What technical skills are important for a {role}?",
        f"Describe a project relevant to the {role}."
    ]

    return questions