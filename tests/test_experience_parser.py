from parsers.experience_parser import (
    parse_date,
    calculate_duration,
    extract_experience_entries,
    calculate_total_experience,
    detect_gaps,
    detect_overlaps,
    parse_experience,
)


def test_parse_date():
    date = parse_date("January 2025")

    assert date.year == 2025
    assert date.month == 1


def test_calculate_duration():
    start_date = parse_date("January 2025")
    end_date = parse_date("June 2025")

    duration = calculate_duration(
        start_date,
        end_date
    )

    assert duration == 6


def test_extract_experience_entries():
    text = """
    Python Developer Intern
    ABC Technologies
    January 2025 – June 2025
    """

    experiences = extract_experience_entries(text)

    assert len(experiences) == 1
    assert experiences[0]["job_title"] == "Python Developer Intern"
    assert experiences[0]["company"] == "ABC Technologies"
    assert experiences[0]["duration_months"] == 6


def test_total_experience():
    experiences = [
        {
            "company": "ABC",
            "job_title": "Developer",
            "start_date": parse_date("January 2024"),
            "end_date": parse_date("June 2024"),
            "duration_months": 6
        },
        {
            "company": "XYZ",
            "job_title": "Developer",
            "start_date": parse_date("July 2024"),
            "end_date": parse_date("December 2024"),
            "duration_months": 6
        }
    ]

    total = calculate_total_experience(
        experiences
    )

    assert total == 12


def test_detect_gaps():
    experiences = [
        {
            "company": "ABC",
            "job_title": "Developer",
            "start_date": parse_date("January 2024"),
            "end_date": parse_date("June 2024"),
            "duration_months": 6
        },
        {
            "company": "XYZ",
            "job_title": "Developer",
            "start_date": parse_date("September 2024"),
            "end_date": parse_date("December 2024"),
            "duration_months": 4
        }
    ]

    gaps = detect_gaps(experiences)

    assert len(gaps) == 1
    assert gaps[0]["duration_months"] == 2


def test_detect_overlaps():
    experiences = [
        {
            "company": "ABC",
            "job_title": "Developer",
            "start_date": parse_date("January 2024"),
            "end_date": parse_date("June 2024"),
            "duration_months": 6
        },
        {
            "company": "XYZ",
            "job_title": "Analyst",
            "start_date": parse_date("May 2024"),
            "end_date": parse_date("December 2024"),
            "duration_months": 8
        }
    ]

    overlaps = detect_overlaps(experiences)

    assert len(overlaps) == 1
    assert overlaps[0]["first_role"] == "Developer"
    assert overlaps[0]["second_role"] == "Analyst"


def test_parse_experience():
    text = """
    Python Developer Intern
    ABC Technologies
    January 2025 – June 2025
    """

    result = parse_experience(
        text,
        candidate_id="CAND-001"
    )

    assert result["candidate_id"] == "CAND-001"
    assert result["total_experience_months"] == 6
    assert len(result["experiences"]) == 1