
import re
import json
from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)


# Map skill variations to standard names.
SKILL_SYNONYMS = {
    "python": ["python", "python programming"],
    "sql": ["sql", "structured query language"],
    "rest apis": [
        "rest api", "rest apis", "restful api", "restful apis"
    ],
    "git": ["git", "version control using git"],
    "fastapi": ["fastapi", "fast api"],
    "docker": ["docker", "containerization"],
    "aws": ["aws", "amazon web services"],
    "candidate sourcing": ["candidate sourcing", "talent sourcing"],
    "resume screening": ["resume screening", "cv screening"],
    "interview coordination": [
        "interview coordination", "interview scheduling"
    ],
    "communication": ["communication", "communication skills"],
    "linkedin recruiter": ["linkedin recruiter"],
    "applicant tracking systems": [
        "applicant tracking system",
        "applicant tracking systems",
        "ats"
    ],
    "microsoft excel": ["microsoft excel", "ms excel", "excel"],
}


# Map role variations to standard job titles.
ROLE_SYNONYMS = {
    "Python Developer": [
        "python developer",
        "python programmer",
        "python software developer"
    ],
    "HR Recruiter": [
        "hr recruiter",
        "human resources recruiter",
        "recruiter",
        "talent acquisition specialist"
    ],
}


def normalize_jd_text(text):
    """Clean whitespace and normalize JD text."""
    if not text or not text.strip():
        raise ValueError("Job description text cannot be empty.")

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def detect_role(text):
    """Detect a recognized role variation."""
    normalized = text.lower()

    for standard_role, variations in ROLE_SYNONYMS.items():
        for variation in variations:
            pattern = r"(?<!\w)" + re.escape(variation) + r"(?!\w)"

            if re.search(pattern, normalized):
                return standard_role

    return None


def extract_skills(text):
    """Extract required and preferred skills separately."""
    normalized = text.lower()

    # Match the preferred skills section until the next known heading.
    preferred_pattern = re.compile(
        r"^\s*preferred\s+skills\s*:?\s*$\n?"
        r"(.*?)"
        r"(?=^\s*(?:responsibilities|qualifications|education|"
        r"requirements|certifications)\s*:?\s*$|\Z)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL
    )

    preferred_match = preferred_pattern.search(normalized)

    if preferred_match:
        preferred_text = preferred_match.group(1)

        # Remove the preferred section before searching for required skills.
        required_text = preferred_pattern.sub("", normalized)
    else:
        preferred_text = ""
        required_text = normalized

    def find_skills(section_text):
        """Find known skills and return standard names."""
        found = []

        for standard_skill, variations in SKILL_SYNONYMS.items():
            for variation in variations:
                pattern = (
                    r"(?<!\w)" + re.escape(variation) + r"(?!\w)"
                )

                if re.search(pattern, section_text):
                    found.append(standard_skill)
                    break

        return found

    return {
        "required_skills": find_skills(required_text),
        "preferred_skills": find_skills(preferred_text)
    }


def extract_experience(text):
    """Extract a basic experience range or minimum."""
    normalized = text.lower()

    # Examples: 1 to 3 years, 1-3 years.
    range_match = re.search(
        r"(\d+)\s*(?:to|-)\s*(\d+)\s*years?",
        normalized
    )

    if range_match:
        minimum = int(range_match.group(1))
        maximum = int(range_match.group(2))

        if minimum <= maximum:
            return {
                "minimum_years": minimum,
                "maximum_years": maximum
            }

    # Examples: 2+ years of experience, 2 years experience.
    minimum_match = re.search(
        r"(\d+)\s*\+?\s*years?\s+(?:of\s+)?experience",
        normalized
    )

    if minimum_match:
        return {
            "minimum_years": int(minimum_match.group(1)),
            "maximum_years": None
        }

    return {
        "minimum_years": None,
        "maximum_years": None
    }


def extract_education(text):
    """Identify common education levels and fields."""
    normalized = text.lower()

    levels = [
        ("PhD", ["phd", "doctorate", "doctoral degree"]),
        ("Master's degree", [
            "master's degree", "masters degree", "master degree",
            "postgraduate degree", "m.tech", "m.sc", "mba"
        ]),
        ("Bachelor's degree", [
            "bachelor's degree", "bachelors degree", "bachelor degree",
            "undergraduate degree", "b.tech", "b.e.", "b.sc", "bca"
        ]),
        ("Diploma", ["diploma"])
    ]

    minimum_level = None

    for standard_level, variations in levels:
        if any(term in normalized for term in variations):
            minimum_level = standard_level
            break

    field_variations = {
        "Computer Science": [
            "computer science", "computer engineering"
        ],
        "Human Resources": [
            "human resources", "human resource management"
        ],
        "Business Administration": ["business administration"],
        "Information Technology": ["information technology"]
    }

    fields = []

    for standard_field, variations in field_variations.items():
        if any(term in normalized for term in variations):
            fields.append(standard_field)

    return {
        "minimum_level": minimum_level,
        "fields": fields
    }


def parse_job_description(text, job_id="JD001"):
    """Convert raw JD text into a structured requirement object."""
    cleaned_text = normalize_jd_text(text)

    skills = extract_skills(cleaned_text)

    result = {
        "job_id": job_id,
        "job_title": detect_role(cleaned_text),
        "required_skills": skills["required_skills"],
        "preferred_skills": skills["preferred_skills"],
        "experience_required": extract_experience(cleaned_text),
        "education_requirements": extract_education(cleaned_text),
        "normalized_text": cleaned_text,
        "status": "processed"
    }

    logger.info("Job description parsed: %s", job_id)

    return result


def parse_jd_file(input_file, output_file):
    """Read a raw JD text file, parse it, and save JSON."""
    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.is_file():
        raise FileNotFoundError(
            f"Job description file not found: {input_path}"
        )

    text = input_path.read_text(encoding="utf-8")

    result = parse_job_description(
        text,
        job_id=input_path.stem
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(result, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    logger.info("Parsed JD saved: %s", output_path)

    return result
