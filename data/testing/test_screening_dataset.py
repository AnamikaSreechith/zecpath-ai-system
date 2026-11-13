
import json
from pathlib import Path


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCREENING_DIR = PROJECT_ROOT / "data" / "screening"


def load_json(filename):
    """Load a JSON file from the screening directory."""
    file_path = SCREENING_DIR / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def test_all_json_files_are_valid():
    """Check that all four screening JSON files can be loaded."""
    filenames = [
        "hr_screening_questions.json",
        "question_category_mapping.json",
        "screening_question_templates.json",
        "conversation_question_objects.json"
    ]

    for filename in filenames:
        data = load_json(filename)
        assert isinstance(data, dict)


def test_question_ids_are_unique():
    """Ensure every question has a unique ID."""
    data = load_json("hr_screening_questions.json")
    questions = data["questions"]

    question_ids = [
        question["question_id"]
        for question in questions
    ]

    assert len(question_ids) == len(set(question_ids))


def test_required_question_fields_exist():
    """Validate the required metadata for every question."""
    data = load_json("hr_screening_questions.json")

    required_fields = [
        "question_id",
        "category",
        "question_text",
        "expected_answer_type",
        "mandatory",
        "scoring_importance",
        "applicable_roles",
        "language",
        "is_active"
    ]

    for question in data["questions"]:
        for field in required_fields:
            assert field in question, (
                f"{field} missing in {question.get('question_id')}"
            )


def test_all_seven_categories_exist():
    """Check that all required screening categories are present."""
    data = load_json("question_category_mapping.json")

    categories = {
        category["category_name"]
        for category in data["categories"]
    }

    expected_categories = {
        "Introduction",
        "Education",
        "Experience",
        "Skills",
        "Location",
        "Salary",
        "Notice Period"
    }

    assert categories == expected_categories


def test_category_mapping_references_valid_questions():
    """Check that category mappings contain existing question IDs."""
    question_data = load_json("hr_screening_questions.json")
    mapping_data = load_json("question_category_mapping.json")

    valid_ids = {
        question["question_id"]
        for question in question_data["questions"]
    }

    for category in mapping_data["categories"]:
        for question_id in category["question_ids"]:
            assert question_id in valid_ids, (
                f"Unknown question ID: {question_id}"
            )


def test_conversation_objects_reference_valid_questions():
    """Check that every conversation object refers to a question."""
    question_data = load_json("hr_screening_questions.json")
    conversation_data = load_json(
        "conversation_question_objects.json"
    )

    valid_ids = {
        question["question_id"]
        for question in question_data["questions"]
    }

    conversation_ids = [
        item["question_id"]
        for item in conversation_data["question_flow"]
    ]

    assert len(conversation_ids) == len(set(conversation_ids))

    for question_id in conversation_ids:
        assert question_id in valid_ids


def test_role_specific_questions_reference_valid_questions():
    """Validate role-specific question IDs."""
    question_data = load_json("hr_screening_questions.json")
    conversation_data = load_json(
        "conversation_question_objects.json"
    )

    valid_ids = {
        question["question_id"]
        for question in question_data["questions"]
    }

    role_questions = conversation_data["role_specific_question_ids"]

    expected_roles = {
        "JOB001",
        "JOB002",
        "JOB003",
        "JOB004",
        "JOB005"
    }

    assert set(role_questions.keys()) == expected_roles

    for role_id, question_ids in role_questions.items():
        for question_id in question_ids:
            assert question_id in valid_ids, (
                f"{question_id} is invalid for {role_id}"
            )


def test_question_metadata_values_are_valid():
    """Validate answer types, importance tags, and mandatory flags."""
    data = load_json("hr_screening_questions.json")

    allowed_answer_types = {
        "text",
        "long_text",
        "number",
        "list",
        "list_with_details",
        "boolean_with_details",
        "date_or_text"
    }

    allowed_importance = {
        "low",
        "medium",
        "high"
    }

    for question in data["questions"]:
        assert question["expected_answer_type"] in allowed_answer_types
        assert question["scoring_importance"] in allowed_importance
        assert isinstance(question["mandatory"], bool)
        assert isinstance(question["applicable_roles"], list)


def test_salary_questions_are_not_direct_suitability_scores():
    """Ensure salary questions are marked as informational or budget checks."""
    data = load_json("hr_screening_questions.json")

    salary_questions = [
        question
        for question in data["questions"]
        if question["category"] == "Salary"
    ]

    assert len(salary_questions) > 0

    for question in salary_questions:
        assert question["scoring_policy"] in {
            "informational_only",
            "compare_with_salary_budget"
        }


def test_templates_have_required_fields():
    """Validate reusable question templates."""
    data = load_json("screening_question_templates.json")

    for template in data["templates"]:
        assert "template_id" in template
        assert "category" in template
        assert "template_text" in template
        assert "placeholders" in template
        assert "expected_answer_type" in template
        assert "language" in template


if __name__ == "__main__":
    print("Running Day 22 screening dataset validation...")

    test_all_json_files_are_valid()
    test_question_ids_are_unique()
    test_required_question_fields_exist()
    test_all_seven_categories_exist()
    test_category_mapping_references_valid_questions()
    test_conversation_objects_reference_valid_questions()
    test_role_specific_questions_reference_valid_questions()
    test_question_metadata_values_are_valid()
    test_salary_questions_are_not_direct_suitability_scores()
    test_templates_have_required_fields()

    print("All Day 22 validation checks passed!")
