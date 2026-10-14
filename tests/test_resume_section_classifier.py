import pytest

from parsers.resume_section_classifier import (
    detect_section_heading,
    segment_resume,
)


def test_detect_skills_heading():
    assert detect_section_heading("Skills") == "skills"


def test_detect_skills_variation():
    assert detect_section_heading("Technical Skills") == "skills"


def test_detect_experience_heading():
    assert detect_section_heading("Professional Experience") == "work_experience"


def test_detect_education_variation():
    assert detect_section_heading("Academic Background") == "education"


def test_detect_certification_heading():
    assert detect_section_heading("Professional Certifications") == "certifications"


def test_detect_projects_variation():
    assert detect_section_heading("Personal Projects") == "projects"


def test_unknown_heading():
    assert detect_section_heading("Hobbies") is None


def test_empty_resume():
    with pytest.raises(ValueError):
        segment_resume("")


def test_resume_segmentation():
    resume_text = """
    ANAMIKA SREECHITH

    Skills
    Python
    SQL
    Power BI

    Education
    B.Tech Computer Science

    Projects
    Bone Fracture Classification

    Certifications
    AI-900
    """

    result = segment_resume(resume_text)

    assert "skills" in result
    assert "education" in result
    assert "projects" in result
    assert "certifications" in result

    assert "Python" in result["skills"]
    assert "B.Tech Computer Science" in result["education"]


def test_heading_variations():
    resume_text = """
    Technical Skills
    Python
    SQL

    Professional Experience
    Data Analyst Intern

    Academic Background
    B.Tech Computer Science

    Personal Projects
    House Price Prediction
    """

    result = segment_resume(resume_text)

    assert "skills" in result
    assert "work_experience" in result
    assert "education" in result
    assert "projects" in result