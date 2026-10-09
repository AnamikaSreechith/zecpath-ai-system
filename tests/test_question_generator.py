import pytest

from interview_ai.question_generator import generate_sample_questions


def test_generate_questions():
    questions = generate_sample_questions("Python Developer")

    assert len(questions) == 3
    assert all("Python Developer" in question for question in questions)


def test_empty_role():
    with pytest.raises(ValueError):
        generate_sample_questions("")