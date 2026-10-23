import re
from datetime import datetime


MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12
}


def parse_date(date_text):
    """Convert a month-year string or datetime into a datetime object."""

    if not date_text:
        return None

    if isinstance(date_text, datetime):
        return date_text

    date_text = str(date_text).strip().lower()

    match = re.search(
        r"(january|february|march|april|may|june|july|"
        r"august|september|october|november|december)\s+(\d{4})",
        date_text
    )

    if match:
        month = MONTHS[match.group(1)]
        year = int(match.group(2))

        return datetime(year, month, 1)

    match = re.search(
        r"(\d{4})-(\d{1,2})",
        date_text
    )

    if match:
        year = int(match.group(1))
        month = int(match.group(2))

        return datetime(year, month, 1)

    return None

def calculate_duration(start_date, end_date):
    """Calculate employment duration in months."""

    if not start_date or not end_date:
        return 0

    return (
        (end_date.year - start_date.year) * 12
        + (end_date.month - start_date.month)
        + 1
    )


def extract_experience_entries(text):
    """Extract company, job title, and employment dates."""

    if not text or not text.strip():
        return []

    entries = []

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    date_pattern = re.compile(
        r"(January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{4}"
        r"\s*[-–]\s*"
        r"(January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{4}",
        re.IGNORECASE
    )

    current_entry = None

    for line in lines:

        date_match = date_pattern.search(line)

        if date_match:
            date_range = date_match.group(0)

            dates = re.split(
                r"\s*[-–]\s*",
                date_range
            )

            start_date = parse_date(dates[0])
            end_date = parse_date(dates[1])

            if current_entry and start_date and end_date:

                # Store dates as strings so they can be
                # serialized safely into JSON.
                current_entry["start_date"] = (
                    start_date.strftime("%Y-%m")
                )

                current_entry["end_date"] = (
                    end_date.strftime("%Y-%m")
                )

                current_entry["duration_months"] = (
                    calculate_duration(
                        start_date,
                        end_date
                    )
                )

                entries.append(current_entry)

                current_entry = None

        else:
            if current_entry is None:
                current_entry = {
                    "company": None,
                    "job_title": line
                }

            elif current_entry["company"] is None:
                current_entry["company"] = line

    return entries


def calculate_total_experience(experiences):
    """Calculate total professional experience in months."""

    return sum(
        experience.get("duration_months", 0)
        for experience in experiences
    )


def detect_gaps(experiences):
    """Detect gaps between consecutive employment periods."""

    if len(experiences) < 2:
        return []

    sorted_experiences = sorted(
        experiences,
        key=lambda x: x["start_date"]
    )

    gaps = []

    for previous, current in zip(
        sorted_experiences,
        sorted_experiences[1:]
    ):

        if not previous["end_date"] or not current["start_date"]:
            continue

        previous_end = parse_date(
            previous["end_date"]
        )

        current_start = parse_date(
            current["start_date"]
        )

        if not previous_end or not current_start:
            continue

        gap_months = (
            (current_start.year - previous_end.year) * 12
            + (
                current_start.month
                - previous_end.month
            )
            - 1
        )

        if gap_months > 0:
            gaps.append({
                "from": previous["end_date"],
                "to": current["start_date"],
                "duration_months": gap_months
            })

    return gaps


def detect_overlaps(experiences):
    """Detect overlapping employment periods."""

    if len(experiences) < 2:
        return []

    sorted_experiences = sorted(
        experiences,
        key=lambda x: x["start_date"]
    )

    overlaps = []

    for previous, current in zip(
        sorted_experiences,
        sorted_experiences[1:]
    ):

        if not previous["end_date"] or not current["start_date"]:
            continue

        previous_end = parse_date(
            previous["end_date"]
        )

        current_start = parse_date(
            current["start_date"]
        )

        if not previous_end or not current_start:
            continue

        if current_start <= previous_end:
            overlaps.append({
                "first_role": previous["job_title"],
                "second_role": current["job_title"],
                "first_company": previous["company"],
                "second_company": current["company"]
            })

    return overlaps


def parse_experience(text, candidate_id=None):
    """Create a structured experience object."""

    experiences = extract_experience_entries(text)

    total_experience = calculate_total_experience(
        experiences
    )

    gaps = detect_gaps(
        experiences
    )

    overlaps = detect_overlaps(
        experiences
    )

    return {
        "candidate_id": candidate_id,
        "experiences": experiences,
        "total_experience_months": total_experience,
        "gaps": gaps,
        "overlaps": overlaps
    }