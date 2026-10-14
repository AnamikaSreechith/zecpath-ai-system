import re

from utils.logger import get_logger

logger = get_logger(__name__)


# Different headings that can represent the same resume section.
SECTION_SYNONYMS = {
    "skills": [
        "skills",
        "technical skills",
        "core skills",
        "key skills",
        "technical expertise",
        "skills & technologies",
    ],

    "work_experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
        "career history",
    ],

    "education": [
        "education",
        "educational background",
        "academic background",
        "academic qualifications",
        "qualifications",
    ],

    "certifications": [
        "certifications",
        "certificates",
        "professional certifications",
        "training & certifications",
        "certification",
    ],

    "projects": [
        "projects",
        "academic projects",
        "personal projects",
        "technical projects",
        "project experience",
    ],
}


def normalize_heading(text):
    """Normalize a possible resume heading."""

    text = text.strip().lower()

    # Remove common punctuation.
    text = re.sub(r"[:\-|]+$", "", text)

    # Replace multiple spaces with one.
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def detect_section_heading(line):
    """
    Check whether a line is a known resume section heading.

    Returns the standardized section name or None.
    """

    normalized_line = normalize_heading(line)

    if not normalized_line:
        return None

    for section_name, headings in SECTION_SYNONYMS.items():

        for heading in headings:

            if normalized_line == heading:
                return section_name

    return None


def segment_resume(text):
    """
    Divide resume text into recognized sections.

    Returns a dictionary containing the detected sections.
    """

    if not text or not text.strip():
        raise ValueError("Resume text cannot be empty.")

    lines = text.splitlines()

    sections = {}
    current_section = "other"

    sections[current_section] = []

    for line in lines:

        stripped_line = line.strip()

        if not stripped_line:
            continue

        detected_section = detect_section_heading(stripped_line)

        if detected_section:
            current_section = detected_section

            if current_section not in sections:
                sections[current_section] = []

            continue

        sections[current_section].append(stripped_line)

    # Convert lists of lines into readable text.
    for section_name in sections:
        sections[section_name] = "\n".join(sections[section_name]).strip()

    # Remove empty sections.
    sections = {
        section: content
        for section, content in sections.items()
        if content
    }

    logger.info(
        "Resume segmented into %d sections",
        len(sections)
    )

    return sections