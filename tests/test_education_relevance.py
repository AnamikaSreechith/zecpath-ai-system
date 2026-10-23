from parsers.education_relevance import (
    normalize_text,
    calculate_education_relevance
)


def test_normalize_text():

    result = normalize_text(
        "  Computer   Science  "
    )

    assert result == "computer science"


def test_education_relevance():

    education = [
        {
            "degree": "B.Tech",
            "field_of_study": "Computer Science and Engineering",
            "institution": "Lourdes Matha College",
            "graduation_year": 2026
        }
    ]

    certifications = [
        {
            "name": "AI-900",
            "category": "AI/ML"
        },
        {
            "name": "Power BI",
            "category": "Data"
        }
    ]

    job_description = """
    We are looking for a Computer Science graduate
    with AI-900 certification and Power BI knowledge.
    """

    result = calculate_education_relevance(
        education,
        certifications,
        job_description
    )

    assert result["score"] > 0
    assert "Computer Science and Engineering" in (
        result["matched_education"]
    )

    assert "AI-900" in (
        result["matched_certifications"]
    )

    assert "Power BI" in (
        result["matched_certifications"]
    )


def test_no_job_description():

    result = calculate_education_relevance(
        [],
        [],
        ""
    )

    assert result["score"] == 0.0