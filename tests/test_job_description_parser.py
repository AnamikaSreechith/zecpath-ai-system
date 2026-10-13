
import json
import pytest

from parsers.job_description_parser import (
    normalize_jd_text,
    detect_role,
    extract_skills,
    extract_experience,
    extract_education,
    parse_job_description,
    parse_jd_file,
)


def test_normalize_jd_text():
    result = normalize_jd_text("Python   Developer\n\n\nSQL")
    assert result == "Python Developer\n\nSQL"


def test_empty_jd_text():
    with pytest.raises(ValueError):
        normalize_jd_text("   ")


def test_detect_role():
    assert detect_role("We need a Python Programmer") == "Python Developer"


def test_required_and_preferred_skills():
    text = """
    Job Title: Python Developer

    Requirements:
    Python, SQL, REST APIs and Git.

    Preferred Skills:
    FastAPI, Docker and AWS.

    Responsibilities:
    Develop applications.
    """

    result = extract_skills(text)

    assert result["required_skills"] == [
        "python", "sql", "rest apis", "git"
    ]
    assert result["preferred_skills"] == [
        "fastapi", "docker", "aws"
    ]


def test_extract_experience_range():
    result = extract_experience(
        "Requires 1 to 3 years of experience."
    )

    assert result == {
        "minimum_years": 1,
        "maximum_years": 3
    }


def test_extract_minimum_experience():
    result = extract_experience(
        "Requires 2+ years of experience."
    )

    assert result == {
        "minimum_years": 2,
        "maximum_years": None
    }


def test_extract_education():
    result = extract_education(
        "Bachelor's degree in Computer Science."
    )

    assert result["minimum_level"] == "Bachelor's degree"
    assert "Computer Science" in result["fields"]


def test_parse_job_description():
    result = parse_job_description(
        "Python Developer with 2 years of experience and Python skills.",
        job_id="TEST001"
    )

    assert result["job_id"] == "TEST001"
    assert result["job_title"] == "Python Developer"
    assert result["status"] == "processed"
    assert "python" in result["required_skills"]


def test_parse_jd_file_saves_json(tmp_path):
    input_file = tmp_path / "sample_jd.txt"
    output_file = tmp_path / "output" / "sample_jd.json"

    input_file.write_text(
        "Python Developer with Python and SQL skills.",
        encoding="utf-8"
    )

    parse_jd_file(input_file, output_file)

    assert output_file.exists()

    saved_data = json.loads(
        output_file.read_text(encoding="utf-8")
    )

    assert saved_data["job_title"] == "Python Developer"
    assert saved_data["status"] == "processed"
