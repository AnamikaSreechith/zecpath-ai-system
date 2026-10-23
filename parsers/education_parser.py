import re


DEGREE_NORMALIZATION = {
    "b.tech": "B.Tech",
    "btech": "B.Tech",
    "b.e": "B.E",
    "be": "B.E",
    "m.tech": "M.Tech",
    "mtech": "M.Tech",
    "m.e": "M.E",
    "me": "M.E",
    "b.sc": "B.Sc",
    "bsc": "B.Sc",
    "m.sc": "M.Sc",
    "msc": "M.Sc",
    "bca": "BCA",
    "mca": "MCA",
    "bba": "BBA",
    "mba": "MBA",
    "ph.d": "Ph.D",
    "phd": "Ph.D"
}


def normalize_degree(degree):
    """Normalize degree names."""

    if not degree:
        return None

    key = degree.strip().lower()

    return DEGREE_NORMALIZATION.get(
        key,
        degree.strip()
    )


def extract_graduation_year(text):
    """Extract a four-digit graduation year."""

    if not text:
        return None

    match = re.search(
        r"\b(19|20)\d{2}\b",
        text
    )

    if match:
        return int(match.group(0))

    return None


def extract_degree(text):
    """Extract and normalize a degree type."""

    if not text:
        return None

    patterns = [
        r"\bB\.?\s*Tech\b",
        r"\bB\.?\s*E\b",
        r"\bM\.?\s*Tech\b",
        r"\bM\.?\s*E\b",
        r"\bB\.?\s*Sc\b",
        r"\bM\.?\s*Sc\b",
        r"\bBCA\b",
        r"\bMCA\b",
        r"\bBBA\b",
        r"\bMBA\b",
        r"\bPh\.?\s*D\b"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return normalize_degree(
                match.group(0)
            )

    return None


def extract_field_of_study(text):
    """Extract a common field of study."""

    if not text:
        return None

    # Keep longer/more specific fields before shorter ones.
    patterns = [
        r"computer science and engineering",
        r"electronics and communication engineering",
        r"electronics and communication",
        r"electrical engineering",
        r"mechanical engineering",
        r"civil engineering",
        r"information technology",
        r"data science",
        r"artificial intelligence",
        r"business administration",
        r"computer science"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(0).title()

    return None


def extract_institution(text):
    """Extract a likely educational institution."""

    if not text:
        return None

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    institution_keywords = [
        "university",
        "college",
        "institute",
        "school"
    ]

    for line in lines:
        if any(
            keyword in line.lower()
            for keyword in institution_keywords
        ):
            return line

    return None


CERTIFICATION_CATEGORIES = {
    "AI/ML": [
        "AI-900",
        "AI-102",
        "Artificial Intelligence",
        "Machine Learning",
        "Deep Learning"
    ],

    "Cloud": [
        "AWS",
        "Azure",
        "Google Cloud",
        "Microsoft Azure"
    ],

    "Data": [
        "Power BI",
        "Data Analytics",
        "Data Science",
        "SQL"
    ],

    "Programming": [
        "Python",
        "Java",
        "C++",
        "C"
    ],

    "Project Management": [
        "Project Management",
        "PMP",
        "Scrum",
        "Agile"
    ]
}


def normalize_certification(certification):
    """Normalize certification names."""

    if not certification:
        return None

    certification = certification.strip()

    normalization = {
        "microsoft azure": "Microsoft Azure",
        "azure": "Microsoft Azure",
        "power bi": "Power BI",
        "artificial intelligence": "Artificial Intelligence",
        "machine learning": "Machine Learning",
        "deep learning": "Deep Learning"
    }

    return normalization.get(
        certification.lower(),
        certification
    )


def categorize_certification(certification):
    """Assign a relevance category to a certification."""

    if not certification:
        return "Other"

    certification_lower = certification.strip().lower()

    for category, certifications in CERTIFICATION_CATEGORIES.items():

        for item in certifications:

            item_lower = item.lower()

            # Exact match.
            if certification_lower == item_lower:
                return category

            # Safe partial match for longer names.
            # Prevents "C" from matching words such as
            # "B.Tech", "College", etc.
            if len(item_lower) > 2:
                pattern = r"\b" + re.escape(item_lower) + r"\b"

                if re.search(
                    pattern,
                    certification_lower
                ):
                    return category

    return "Other"


def extract_certifications(text):
    """Extract recognized certifications and assign categories."""

    if not text or not text.strip():
        return []

    certifications = []

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    for line in lines:

        certification = re.sub(
            r"^[•●▪◦‣⁃\-\*]\s*",
            "",
            line
        ).strip()

        if not certification:
            continue

        # Ignore degree information.
        if extract_degree(certification):
            continue

        # Ignore graduation years.
        if extract_graduation_year(certification):
            continue

        # Ignore educational institutions.
        if any(
            keyword in certification.lower()
            for keyword in [
                "university",
                "college",
                "institute",
                "school"
            ]
        ):
            continue

        normalized = normalize_certification(
            certification
        )

        category = categorize_certification(
            normalized
        )

        # Only keep recognized certifications.
        if category != "Other":
            certifications.append({
                "name": normalized,
                "category": category
            })

    return certifications


def parse_education(text, candidate_id=None):
    """Create a structured academic profile."""

    if not text or not text.strip():
        return {
            "candidate_id": candidate_id,
            "education": [],
            "certifications": []
        }

    education = {
        "degree": extract_degree(text),
        "field_of_study": extract_field_of_study(text),
        "institution": extract_institution(text),
        "graduation_year": extract_graduation_year(text)
    }

    certifications = extract_certifications(text)

    return {
        "candidate_id": candidate_id,
        "education": [education],
        "certifications": certifications
    }