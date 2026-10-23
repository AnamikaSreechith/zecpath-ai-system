import re


def normalize_text(text):
    """Normalize text for comparison."""

    if not text:
        return ""

    return re.sub(
        r"\s+",
        " ",
        text.lower().strip()
    )


def field_matches_job(field, job_text):
    """Check whether the field of study is relevant to the job description."""

    if not field:
        return False

    field = normalize_text(field)
    job_text = normalize_text(job_text)

    # Exact full-field match.
    if field in job_text:
        return True

    # Match important words from the field.
    important_words = [
        word
        for word in re.findall(r"\b[a-z]+\b", field)
        if word not in {
            "and",
            "of",
            "the"
        }
    ]

    if not important_words:
        return False

    matched_words = sum(
        1
        for word in important_words
        if re.search(
            r"\b" + re.escape(word) + r"\b",
            job_text
        )
    )

    # Consider the field relevant when most important
    # field terms appear in the job description.
    return (
        matched_words / len(important_words)
    ) >= 0.5


def calculate_education_relevance(
    education,
    certifications,
    job_description
):
    """
    Calculate education relevance against a job description.
    """

    if not job_description:
        return {
            "score": 0.0,
            "matched_education": [],
            "matched_certifications": []
        }

    job_text = normalize_text(job_description)

    matched_education = []
    matched_certifications = []

    # Check degree and field of study.
    for item in education or []:

        degree = item.get("degree")
        field = item.get("field_of_study")

        if degree:
            if normalize_text(degree) in job_text:
                matched_education.append(degree)

        if field:
            if field_matches_job(
                field,
                job_text
            ):
                matched_education.append(field)

    # Check certifications.
    for certification in certifications or []:

        name = certification.get("name")

        if name and normalize_text(name) in job_text:
            matched_certifications.append(name)

    total_items = (
        len(matched_education)
        + len(matched_certifications)
    )

    score = min(
        total_items * 0.25,
        1.0
    )

    return {
        "score": round(score, 2),
        "matched_education": matched_education,
        "matched_certifications": matched_certifications
    }