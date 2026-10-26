
import json
import pytest

from parsers.resume_parser import (
    clean_resume_text,
    parse_resume_text,
    extract_resume,
)


def test_valid_resume_text():
    result = parse_resume_text(
        "Python developer with SQL skills"
    )

    assert result["status"] == "processed"
    assert result["raw_text"] == "Python developer with SQL skills"
    assert result["cleaned_text"] == "Python developer with SQL skills"


def test_empty_resume_text():
    with pytest.raises(ValueError):
        parse_resume_text("")


def test_whitespace_resume_text():
    with pytest.raises(ValueError):
        parse_resume_text("   ")


def test_bullet_normalization():
    text = "Skills\n• Python\n● SQL\n▪ Git"

    cleaned = clean_resume_text(text)

    assert cleaned == "Skills\n- Python\n- SQL\n- Git"


def test_whitespace_cleanup():
    text = "Python    Developer\n\n\nSQL   Analyst"

    cleaned = clean_resume_text(text)

    assert cleaned == "Python Developer\n\nSQL Analyst"


def test_extract_resume_missing_file(tmp_path):
    missing_file = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        extract_resume(missing_file)


def test_extract_resume_unsupported_format(tmp_path):
    unsupported_file = tmp_path / "resume.txt"
    unsupported_file.write_text(
        "Sample resume",
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_resume(unsupported_file)


def test_extract_resume_saves_json(tmp_path, monkeypatch):
    from parsers import resume_parser

    # Simulate text extracted from a PDF.
    monkeypatch.setattr(
        resume_parser,
        "extract_pdf_text",
        lambda file_path: "Python Developer\n• SQL"
    )

    pdf_file = tmp_path / "resume.pdf"
    pdf_file.touch()

    output_dir = tmp_path / "output"

    result = extract_resume(
        pdf_file,
        output_dir=str(output_dir)
    )

    output_file = output_dir / "resume.json"

    assert output_file.exists()
    assert result["status"] == "processed"

    with open(output_file, "r", encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data["source_file"] == "resume.pdf"
    assert saved_data["cleaned_text"] == "Python Developer\n- SQL"

def test_resume_extraction_contains_sections(tmp_path):
    resume_text = """
    ANAMIKA TEST RESUME

    Skills
    Python
    SQL

    Education
    B.Tech Computer Science

    Experience
    Python Developer Intern

    Projects
    Resume Parser
    """

    result = parse_resume_text(resume_text)

    from parsers.resume_section_classifier import segment_resume

    sections = segment_resume(result["cleaned_text"])

    assert "skills" in sections
    assert "education" in sections
    assert "work_experience" in sections
    assert "projects" in sections

    assert "Python" in sections["skills"]
    assert "B.Tech Computer Science" in sections["education"]


def test_noisy_resume_text_cleanup():
    text = """
    
    
    ANAMIKA SREECHITH    
    
    
    Python     SQL       Power BI
    
    
    • Data Analysis
    ● Machine Learning
    ▪ Deep Learning
    
    
    
    """

    cleaned = clean_resume_text(text)

    assert "ANAMIKA SREECHITH" in cleaned
    assert "Python SQL Power BI" in cleaned
    assert "- Data Analysis" in cleaned
    assert "- Machine Learning" in cleaned
    assert "- Deep Learning" in cleaned


def test_control_characters_are_removed():
    text = "Python\x00\x01 SQL\x02 Power BI"

    cleaned = clean_resume_text(text)

    assert "\x00" not in cleaned
    assert "\x01" not in cleaned
    assert "\x02" not in cleaned


def test_multiple_blank_lines_are_reduced():
    text = "Skills\n\n\n\n\nPython\n\n\nSQL"

    cleaned = clean_resume_text(text)

    assert cleaned == "Skills\n\nPython\n\nSQL"