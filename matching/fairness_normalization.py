"""
Fairness, Normalization & Bias Reduction

Provides normalization utilities for standardizing resume data
and reducing unnecessary bias in candidate evaluation.
"""


# Common skill aliases
SKILL_NORMALIZATION_MAP = {
    "python 3": "python",
    "python3": "python",
    "py": "python",

    "javascript": "javascript",
    "js": "javascript",

    "typescript": "typescript",
    "ts": "typescript",

    "powerbi": "power bi",
    "power bi": "power bi",

    "postgres": "postgresql",
    "postgres sql": "postgresql",

    "reactjs": "react",
    "react.js": "react",

    "nodejs": "node.js",
    "node js": "node.js",

    "restful api": "rest api",
    "restful apis": "rest apis",
    "rest api": "rest api",

    "amazon web services": "aws",
}


def normalize_skill(skill):
    """
    Normalize a skill into a standard representation.

    Examples:
        Python 3 -> python
        JS -> javascript
        PowerBI -> power bi
    """

    if not skill:
        return None

    normalized = str(skill).strip().lower()

    # Remove unnecessary spaces
    normalized = " ".join(normalized.split())

    return SKILL_NORMALIZATION_MAP.get(
        normalized,
        normalized
    )


def normalize_skill_list(skills):
    """
    Normalize a list of skills.
    """

    if not skills:
        return []

    normalized_skills = []

    for skill in skills:

        normalized = normalize_skill(skill)

        if normalized and normalized not in normalized_skills:
            normalized_skills.append(normalized)

    return normalized_skills


def normalize_text(text):
    """
    Standardize text for consistent processing.
    """

    if not text:
        return ""

    text = str(text).strip().lower()
    text = " ".join(text.split())

    return text


def normalize_candidate(candidate):
    """
    Normalize important candidate fields
    while preserving the original structure.
    """

    normalized_candidate = candidate.copy()

    if "skills" in normalized_candidate:

        skills = normalized_candidate["skills"]

        if isinstance(skills, list):

            normalized_skill_names = []

            for skill in skills:

                if isinstance(skill, dict):

                    skill_name = skill.get("name")

                    normalized_name = normalize_skill(
                        skill_name
                    )

                    if normalized_name:
                        normalized_skill_names.append(
                            normalized_name
                        )

                else:

                    normalized_name = normalize_skill(
                        skill
                    )

                    if normalized_name:
                        normalized_skill_names.append(
                            normalized_name
                        )

            normalized_candidate[
                "normalized_skills"
            ] = normalize_skill_list(
                normalized_skill_names
            )

    if "professional_summary" in normalized_candidate:

        normalized_candidate[
            "normalized_summary"
        ] = normalize_text(
            normalized_candidate[
                "professional_summary"
            ]
        )

    return normalized_candidate


def mask_non_essential_attributes(candidate):
    """
    Remove non-essential personal attributes
    from candidate data before scoring.

    The goal is to ensure that candidate evaluation
    focuses on job-relevant information.
    """

    masked_candidate = candidate.copy()

    non_essential_attributes = [
        "name",
        "date_of_birth",
        "dob",
        "age",
        "gender",
        "photo",
        "profile_photo",
        "address",
        "phone",
        "email",
        "marital_status"
    ]

    for attribute in non_essential_attributes:

        masked_candidate.pop(
            attribute,
            None
        )

    return masked_candidate


def normalize_candidate_for_scoring(candidate):
    """
    Prepare a candidate for fair and consistent scoring.

    Steps:
    1. Normalize candidate skills.
    2. Normalize text fields.
    3. Mask non-essential personal attributes.
    """

    normalized_candidate = normalize_candidate(
        candidate
    )

    normalized_candidate = mask_non_essential_attributes(
        normalized_candidate
    )

    return normalized_candidate