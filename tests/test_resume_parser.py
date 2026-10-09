import pytest

from parsers.resume_parser import parse_resume_text


def test_valid_resume_text():
    result = parse_resume_text(
        "Python developer with SQL skills"
    )

    assert result["status"] == "received"
    assert result["raw_text"] == "Python developer with SQL skills"


def test_empty_resume_text():
    with pytest.raises(ValueError):
        parse_resume_text("")


def test_whitespace_resume_text():
    with pytest.raises(ValueError):
        parse_resume_text("   ")