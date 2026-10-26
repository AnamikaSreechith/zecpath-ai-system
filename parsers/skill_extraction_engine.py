import re

from utils.logger import get_logger


logger = get_logger(__name__)


# ============================================================
# SKILL DICTIONARY
# ============================================================

SKILL_DICTIONARY = {
    "Python": {
        "category": "Technical",
        "synonyms": [
            "python",
            "python programming",
            "python developer"
        ]
    },

    "SQL": {
        "category": "Technical",
        "synonyms": [
            "sql",
            "structured query language"
        ]
    },

    "FastAPI": {
        "category": "Technical",
        "synonyms": [
            "fastapi",
            "fast api"
        ]
    },

    "REST APIs": {
        "category": "Technical",
        "synonyms": [
            "rest api",
            "rest apis",
            "restful api",
            "restful apis"
        ]
    },

    "Git": {
        "category": "Technical",
        "synonyms": [
            "git",
            "git version control"
        ]
    },

    "Docker": {
        "category": "Technical",
        "synonyms": [
            "docker",
            "containerization"
        ]
    },

    "AWS": {
        "category": "Technical",
        "synonyms": [
            "aws",
            "amazon web services"
        ]
    },

    "React": {
        "category": "Technical",
        "synonyms": [
            "react",
            "react.js",
            "reactjs"
        ]
    },

    "Node.js": {
        "category": "Technical",
        "synonyms": [
            "node",
            "node.js",
            "nodejs"
        ]
    },

    "MongoDB": {
        "category": "Technical",
        "synonyms": [
            "mongodb",
            "mongo db"
        ]
    },

    "Express.js": {
        "category": "Technical",
        "synonyms": [
            "express",
            "express.js",
            "expressjs"
        ]
    },

    "Communication": {
        "category": "Non-Technical",
        "synonyms": [
            "communication",
            "communication skills"
        ]
    },

    "Leadership": {
        "category": "Business",
        "synonyms": [
            "leadership",
            "team leadership"
        ]
    },

    "Microsoft Excel": {
        "category": "Business",
        "synonyms": [
            "excel",
            "microsoft excel",
            "ms excel"
        ]
    }
}


# ============================================================
# SKILL STACKS
# ============================================================

SKILL_STACKS = {
    "MERN": [
        "MongoDB",
        "Express.js",
        "React",
        "Node.js"
    ],

    "MEAN": [
        "MongoDB",
        "Express.js",
        "Angular",
        "Node.js"
    ]
}


# ============================================================
# PRE-COMPILED SKILL PATTERNS
# ============================================================

SKILL_PATTERNS = {}

for standard_skill, details in SKILL_DICTIONARY.items():

    patterns = []

    for synonym in details["synonyms"]:

        pattern = re.compile(
            r"(?<!\w)"
            + re.escape(
                synonym.lower()
            )
            + r"(?!\w)"
        )

        patterns.append(pattern)

    SKILL_PATTERNS[standard_skill] = patterns


# ============================================================
# PRE-COMPILED STACK PATTERNS
# ============================================================

STACK_PATTERNS = {}

for stack_name in SKILL_STACKS:

    STACK_PATTERNS[stack_name] = re.compile(
        r"(?<!\w)"
        + re.escape(
            stack_name.lower()
        )
        + r"(?!\w)"
    )


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize text before performing skill matching.
    """

    if not text or not text.strip():

        raise ValueError(
            "Text cannot be empty."
        )

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# FIND SKILL MENTIONS
# ============================================================

def find_skill_mentions(text):
    """
    Find known skills and return their
    standardized names.

    Uses pre-compiled regular expressions
    to reduce repeated pattern creation.
    """

    normalized_text = normalize_text(
        text
    )

    found_skills = []

    for standard_skill, patterns in SKILL_PATTERNS.items():

        for pattern in patterns:

            if pattern.search(
                normalized_text
            ):

                found_skills.append(
                    standard_skill
                )

                break

    return found_skills


# ============================================================
# EXPAND SKILL STACKS
# ============================================================

def expand_skill_stacks(
    skills,
    text
):
    """
    Expand technology stacks such as
    MERN and MEAN.

    The input text is expected to already
    be normalized when used internally.
    """

    normalized_text = normalize_text(
        text
    )

    expanded_skills = list(
        skills
    )

    for stack_name, stack_skills in SKILL_STACKS.items():

        pattern = STACK_PATTERNS[
            stack_name
        ]

        if pattern.search(
            normalized_text
        ):

            for skill in stack_skills:

                if skill not in expanded_skills:

                    expanded_skills.append(
                        skill
                    )

    return expanded_skills


# ============================================================
# INTERNAL STACK EXPANSION
# ============================================================

def _expand_skill_stacks_normalized(
    skills,
    normalized_text
):
    """
    Internal optimized version of stack
    expansion that avoids normalizing
    already-normalized text.
    """

    expanded_skills = list(
        skills
    )

    for stack_name, stack_skills in SKILL_STACKS.items():

        pattern = STACK_PATTERNS[
            stack_name
        ]

        if pattern.search(
            normalized_text
        ):

            for skill in stack_skills:

                if skill not in expanded_skills:

                    expanded_skills.append(
                        skill
                    )

    return expanded_skills


# ============================================================
# CONFIDENCE CALCULATION
# ============================================================

def calculate_confidence(
    skill,
    text
):
    """
    Calculate a simple confidence score
    for a detected skill.
    """

    normalized_text = normalize_text(
        text
    )

    return calculate_confidence_normalized(
        skill,
        normalized_text
    )


def calculate_confidence_normalized(
    skill,
    normalized_text
):
    """
    Optimized confidence calculation for
    already-normalized text.
    """

    details = SKILL_DICTIONARY.get(
        skill
    )

    if not details:

        return 0.0

    patterns = SKILL_PATTERNS.get(
        skill,
        []
    )

    for pattern in patterns:

        if pattern.search(
            normalized_text
        ):

            return 0.95

    return 0.80


# ============================================================
# MAIN SKILL EXTRACTION
# ============================================================

def extract_skills(text):
    """
    Extract, normalize, deduplicate
    and score skills.
    """

    # Normalize once.
    normalized_text = normalize_text(
        text
    )

    # Detect skills.
    skills = find_skill_mentions(
        normalized_text
    )

    # Expand technology stacks without
    # normalizing the text again.
    skills = _expand_skill_stacks_normalized(
        skills,
        normalized_text
    )

    # Preserve order while removing duplicates.
    skills = list(
        dict.fromkeys(skills)
    )

    extracted_skills = []

    # Calculate confidence using the
    # already-normalized text.
    for skill in skills:

        details = SKILL_DICTIONARY[
            skill
        ]

        confidence = (
            calculate_confidence_normalized(
                skill,
                normalized_text
            )
        )

        extracted_skills.append({

            "name": skill,

            "category":
                details["category"],

            "confidence":
                confidence
        })

    logger.info(
        "Skills extracted: %d",
        len(extracted_skills)
    )

    return extracted_skills