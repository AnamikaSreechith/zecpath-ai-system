from parsers.education_parser import (
    normalize_degree,
    extract_graduation_year,
    extract_degree,
    extract_field_of_study,
    extract_institution,
    normalize_certification,
    categorize_certification,
    extract_certifications,
    parse_education,
)


def test_normalize_degree():
    assert normalize_degree("btech") == "B.Tech"
    assert normalize_degree("B.Tech") == "B.Tech"


def test_extract_graduation_year():
    assert extract_graduation_year(
        "B.Tech Computer Science 2026"
    ) == 2026


def test_extract_degree():
    result = extract_degree(
        "B.Tech Computer Science and Engineering"
    )

    assert result == "B.Tech"


def test_extract_field_of_study():
    result = extract_field_of_study(
        "B.Tech Computer Science and Engineering"
    )

    assert result == "Computer Science And Engineering"


def test_extract_institution():
    result = extract_institution(
        "B.Tech Computer Science\n"
        "Lourdes Matha College of Science and Technology"
    )

    assert result == (
        "Lourdes Matha College of Science and Technology"
    )


def test_normalize_certification():
    assert normalize_certification(
        "power bi"
    ) == "Power BI"


def test_categorize_certification():
    assert categorize_certification(
        "Power BI"
    ) == "Data"

    assert categorize_certification(
        "AI-900"
    ) == "AI/ML"


def test_extract_certifications():
    text = """
    AI-900
    Power BI
    AWS
    """

    certifications = extract_certifications(text)

    names = [
        certification["name"]
        for certification in certifications
    ]

    assert "AI-900" in names
    assert "Power BI" in names
    assert "AWS" in names


def test_parse_education():
    text = """
    B.Tech Computer Science and Engineering
    Lourdes Matha College of Science and Technology
    2026

    AI-900
    Power BI
    """

    result = parse_education(
        text,
        candidate_id="CAND-001"
    )

    assert result["candidate_id"] == "CAND-001"
    assert len(result["education"]) == 1
    assert result["education"][0]["degree"] == "B.Tech"
    assert result["education"][0]["graduation_year"] == 2026
    assert len(result["certifications"]) == 2