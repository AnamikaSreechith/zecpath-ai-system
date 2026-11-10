
import json
import logging
import argparse

from pathlib import Path
from typing import Any


# ============================================================
# 1. PROJECT PATHS AND LOGGING
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RULES_FILE = BASE_DIR / "data" / "job_configurations" / "eligibility_rules.json"

JOB_EVALUATIONS_DIR = BASE_DIR / "data" / "job_evaluations"

RESULTS_DIR = BASE_DIR / "data" / "eligibility_results"

RESULTS_FILE = RESULTS_DIR / "candidate_eligibility_results.json"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# 2. JSON LOADING AND SAVING
# ============================================================

def load_json(file_path: Path) -> Any:

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data: Any, file_path: Path) -> None:

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(file_path, "w", encoding="utf-8") as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    logger.info("Results saved to %s", file_path)


# ============================================================
# 3. LOAD ELIGIBILITY CONFIGURATION
# ============================================================

def load_eligibility_rules() -> dict:

    rules = load_json(RULES_FILE)

    if "default_rules" not in rules:
        raise ValueError("Missing default_rules configuration")

    if "job_overrides" not in rules:
        raise ValueError("Missing job_overrides configuration")

    return rules


def get_job_rules(job_id: str, all_rules: dict) -> dict:

    default_rules = all_rules["default_rules"]

    job_specific_rules = all_rules["job_overrides"].get(
        job_id, {}
    )

    # Job-specific configuration overrides defaults.
    return {
        **default_rules,
        **job_specific_rules
    }


# ============================================================
# 4. LOAD CANDIDATE PROFILE INFORMATION
# ============================================================

def load_candidate_profiles() -> dict:

    profile_directories = [
        BASE_DIR / "data" / "resumes",
        BASE_DIR / "data" / "extracted_resumes"
    ]

    profiles = {}

    for directory in profile_directories:

        if not directory.exists():
            continue

        for file_path in directory.glob("*.json"):

            try:

                profile = load_json(file_path)

                if not isinstance(profile, dict):
                    continue

                candidate_id = profile.get("candidate_id")

                if candidate_id:

                    # Keep structured candidate information.
                    profiles[candidate_id] = profile

            except (json.JSONDecodeError, OSError) as error:

                logger.warning(
                    "Could not read profile %s: %s",
                    file_path.name,
                    error
                )

    return profiles


def get_profile_value(profile: dict, field: str):

    if not profile:
        return None

    if profile.get(field) is not None:
        return profile[field]

    # Check common structured profile sections.
    for section_name in [
        "personal_info",
        "personal_details",
        "contact",
        "availability"
    ]:

        section = profile.get(section_name)

        if isinstance(section, dict):

            if section.get(field) is not None:
                return section[field]

    return None


# ============================================================
# 5. ATS SCORE EVALUATION
# ============================================================

def evaluate_ats_score(
    candidate: dict,
    rules: dict,
    review_flags: list,
    knockouts: list
) -> None:

    score = candidate.get("score")

    if score is None:
        knockouts.append("ATS score is unavailable.")
        return

    minimum_eligible = rules["minimum_eligible_score"]

    minimum_review = rules["minimum_review_score"]

    if score < minimum_review:

        knockouts.append(
            f"ATS score ({score}) is below the minimum "
            f"review threshold ({minimum_review})."
        )

    elif score < minimum_eligible:

        review_flags.append(
            f"ATS score ({score}) is below the eligible "
            f"threshold ({minimum_eligible})."
        )


# ============================================================
# 6. MANDATORY SKILL EVALUATION
# ============================================================

def evaluate_mandatory_skills(
    candidate: dict,
    rules: dict,
    review_flags: list,
    knockouts: list
) -> None:

    evidence = candidate.get("evidence", {})

    matched_skills = {
        skill.strip().lower()
        for skill in evidence.get("matched_skills", [])
    }

    reported_missing = {
        skill.strip().lower()
        for skill in evidence.get("missing_required_skills", [])
    }

    required_skills = {
        skill.strip().lower()
        for skill in rules.get("required_skills", [])
    }

    # Combine the ATS engine's missing-skill evidence
    # with the configured mandatory skill requirements.
    missing_skills = (
        reported_missing |
        (required_skills - matched_skills)
    )

    for skill in sorted(missing_skills):

        message = f"Missing mandatory skill: {skill}"

        action = rules.get(
            "missing_required_skill_action",
            "review"
        )

        if action == "reject":
            knockouts.append(message)

        else:
            review_flags.append(message)


# ============================================================
# 7. EXPERIENCE EVALUATION
# ============================================================

def evaluate_experience(
    candidate: dict,
    rules: dict,
    review_flags: list,
    knockouts: list
) -> None:

    experience = candidate.get(
        "evidence", {}
    ).get("experience", {})

    measured_years = experience.get("measured_years")

    if measured_years is None:
        review_flags.append(
            "Candidate experience information is unavailable."
        )
        return
    
    minimum_years = rules.get(
    "minimum_experience_years",
    experience.get("minimum_required_years")
)

    maximum_years = rules.get("maximum_experience_years")

    if minimum_years is not None and measured_years < minimum_years:

        message = (
            f"Experience ({measured_years} years) is below "
            f"the minimum requirement ({minimum_years} years)."
        )

        action = rules.get(
            "experience_outside_range_action",
            "reject"
        )

        if action == "reject":
            knockouts.append(message)
        else:
            review_flags.append(message)

    elif maximum_years is not None and measured_years > maximum_years:

        message = (
            f"Experience ({measured_years} years) exceeds "
            f"the maximum range ({maximum_years} years)."
        )

        action = rules.get(
            "experience_outside_range_action",
            "reject"
        )

        if action == "reject":
            knockouts.append(message)
        else:
            review_flags.append(message)


# ============================================================
# 8. NOTICE PERIOD EVALUATION
# ============================================================

def evaluate_notice_period(
    profile: dict,
    rules: dict,
    review_flags: list
) -> None:

    notice_period = get_profile_value(
        profile,
        "notice_period_days"
    )

    if notice_period is None:
        return

    maximum_notice = rules.get(
        "maximum_notice_period_days"
    )

    if maximum_notice is None:
        return

    if notice_period > maximum_notice:

        message = (
            f"Notice period ({notice_period}d) exceeds "
            f"target ({maximum_notice}d)."
        )

        action = rules.get(
            "notice_period_exceeded_action",
            "review"
        )

        if action == "review":
            review_flags.append(message)


# ============================================================
# 9. LOCATION EVALUATION
# ============================================================

def evaluate_location(
    profile: dict,
    rules: dict,
    review_flags: list,
    knockouts: list
) -> None:

    if not rules.get("location_restriction_enabled", False):
        return

    candidate_location = get_profile_value(
        profile,
        "location"
    )

    allowed_locations = {
        location.strip().lower()
        for location in rules.get("allowed_locations", [])
    }

    if candidate_location is None:

        review_flags.append(
            "Candidate location information is unavailable."
        )

    elif candidate_location.strip().lower() not in allowed_locations:

        knockouts.append(
            f"Candidate location '{candidate_location}' "
            "does not meet the job location requirements."
        )


# ============================================================
# 10. DETERMINE ELIGIBILITY STATUS
# ============================================================

def determine_eligibility(
    candidate: dict,
    rules: dict,
    profile: dict
) -> dict:

    review_flags = []

    knockouts = []

    # Check evaluation completeness.
    coverage = candidate.get(
        "evaluation_coverage", {}
    ).get("coverage_percentage")

    minimum_coverage = rules.get(
        "minimum_evaluation_coverage", 80
    )

    if coverage is None or coverage < minimum_coverage:

        review_flags.append(
            "Insufficient or unavailable ATS evaluation coverage."
        )

    # Evaluate each eligibility parameter.
    evaluate_ats_score(
        candidate, rules, review_flags, knockouts
    )

    evaluate_mandatory_skills(
        candidate, rules, review_flags, knockouts
    )

    evaluate_experience(
        candidate, rules, review_flags, knockouts
    )

    evaluate_notice_period(
        profile, rules, review_flags
    )

    evaluate_location(
        profile, rules, review_flags, knockouts
    )

    # Final decision priority:
    # Rejected > Review > Eligible

    if knockouts:

        status = "Rejected"

    elif review_flags:

        status = "Review"

    else:

        status = "Eligible"

    return {
        "eligibility_status": status,
        "review_flags": review_flags,
        "knockouts": knockouts
    }


# ============================================================
# 11. GENERATE AUTOMATED RECRUITMENT ACTION
# ============================================================

def generate_automated_action(status: str) -> dict:

    actions = {

        "Eligible": {
            "type": "ai_screening_queue",
            "status": "pending",
            "description": (
                "Queue candidate for AI Voice/Video Screening "
                "and prepare calendar scheduling link."
            )
        },

        "Review": {
            "type": "recruiter_review",
            "status": "pending",
            "description": (
                "Route candidate to recruiter triage with "
                "review exceptions highlighted."
            )
        },

        "Rejected": {
            "type": "rejection_workflow",
            "status": "pending",
            "description": (
                "Record knockout reasons for compliance and "
                "prepare rejection email draft."
            )
        }
    }

    return actions[status].copy()


# ============================================================
# 12. PROCESS A SINGLE CANDIDATE
# ============================================================

def process_candidate(
    candidate: dict,
    all_rules: dict,
    profiles: dict
) -> dict:

    job_id = candidate.get("job_id")

    candidate_id = candidate.get("candidate_id")

    if not job_id or not candidate_id:
        raise ValueError(
            "Candidate record must contain job_id and candidate_id."
        )

    rules = get_job_rules(job_id, all_rules)

    profile = profiles.get(candidate_id, {})

    decision = determine_eligibility(
        candidate,
        rules,
        profile
    )

    status = decision["eligibility_status"]

    return {

        "candidate_id": candidate_id,

        "job_id": job_id,

        "job_title": candidate.get(
            "job_title",
            rules.get("job_title", "Unknown")
        ),

        "ats_score": candidate.get("score"),

        "match_level": candidate.get("match_level"),

        "ats_status": candidate.get("status"),

        "eligibility_status": status,

        "summary": (
            "Candidate qualifies for AI screening."
            if status == "Eligible"
            else
            "Candidate requires recruiter review."
            if status == "Review"
            else
            "Candidate failed one or more mandatory eligibility conditions."
        ),

        "review_flags": decision["review_flags"],

        "knockouts": decision["knockouts"],

        "automated_action": generate_automated_action(status)

    }


# ============================================================
# 13. PROCESS MULTIPLE JOBS AND CANDIDATES
# ============================================================

def run_eligibility_pipeline(job_id: str = None) -> list:

    all_rules = load_eligibility_rules()

    profiles = load_candidate_profiles()

    if job_id:

        job_ids = [job_id]

    else:

        job_ids = sorted(
            all_rules["job_overrides"].keys()
        )

        # Also process any additional job files using defaults.
        for file_path in JOB_EVALUATIONS_DIR.glob(
            "JOB*_ranked_candidates.json"
        ):

            discovered_job_id = file_path.name.split("_")[0]

            if discovered_job_id not in job_ids:
                job_ids.append(discovered_job_id)

    all_results = []

    for current_job_id in job_ids:

        input_file = (
            JOB_EVALUATIONS_DIR /
            f"{current_job_id}_ranked_candidates.json"
        )

        if not input_file.exists():

            logger.warning(
                "Ranking file not found for %s",
                current_job_id
            )

            continue

        logger.info(
            "Processing candidates for %s",
            current_job_id
        )

        candidates = load_json(input_file)

        if not isinstance(candidates, list):

            logger.error(
                "Invalid candidate ranking format: %s",
                input_file
            )

            continue

        for candidate in candidates:

            try:

                result = process_candidate(
                    candidate,
                    all_rules,
                    profiles
                )

                all_results.append(result)

            except (ValueError, TypeError, KeyError) as error:

                logger.error(
                    "Could not process candidate %s for %s: %s",
                    candidate.get("candidate_id"),
                    current_job_id,
                    error
                )

    save_json(all_results, RESULTS_FILE)

    logger.info(
        "Eligibility evaluation completed. Total records: %d",
        len(all_results)
    )

    return all_results


# ============================================================
# 14. DISPLAY ELIGIBILITY SUMMARY
# ============================================================

def display_summary(results: list) -> None:

    counts = {
        "Eligible": 0,
        "Review": 0,
        "Rejected": 0
    }

    for result in results:

        counts[result["eligibility_status"]] += 1

    print("\n" + "=" * 60)

    print("ZECpath ATS - ELIGIBILITY DECISION REPORT")

    print("=" * 60)

    print(f"Total Evaluated : {len(results)}")

    print(f"Eligible        : {counts['Eligible']}")

    print(f"Review          : {counts['Review']}")

    print(f"Rejected        : {counts['Rejected']}")

    print("=" * 60)

    print("\nCANDIDATE RESULTS")

    for result in results:

        print(
            f"{result['candidate_id']} | "
            f"{result['job_id']} | "
            f"Score: {result['ats_score']} | "
            f"Eligibility: {result['eligibility_status']}"
        )


# ============================================================
# 15. MAIN EXECUTION
# ============================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Zecpath ATS Eligibility Decision Engine"
    )

    parser.add_argument(
        "--job-id",
        type=str,
        help="Process a specific job ID. Default: all available jobs."
    )

    args = parser.parse_args()

    results = run_eligibility_pipeline(
        job_id=args.job_id
    )

    display_summary(results)
