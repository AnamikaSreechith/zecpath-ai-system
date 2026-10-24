import json
from pathlib import Path

from matching.ats_scoring_engine import (
    generate_candidate_score
)

from matching.candidate_ranking_engine import (
    shortlist_candidates
)

from matching.semantic_matching_engine import (
    calculate_similarity
)


BASE_DIR = Path(__file__).resolve().parent.parent

RESUME_DIR = (
    BASE_DIR
    / "data"
    / "resumes"
)

JD_FILE = (
    BASE_DIR
    / "data"
    / "job_descriptions"
    / "parsed_jds"
    / "python_developer.json"
)

SCORE_FILE = (
    BASE_DIR
    / "data"
    / "candidate_scores.json"
)

RANKED_FILE = (
    BASE_DIR
    / "data"
    / "ranked_candidates.json"
)


def load_json(file_path):
    """Load a JSON file."""

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def load_resumes():
    """Load all resume JSON files."""

    resumes = []

    for file_path in sorted(
        RESUME_DIR.glob("resume*.json")
    ):
        resume = load_json(file_path)
        resumes.append(resume)

    return resumes


def extract_resume_skill_names(skills):
    """Extract skill names from resume skill objects."""

    if not skills:
        return []

    result = []

    for skill in skills:

        if isinstance(skill, dict):

            name = skill.get("name")

            if name:
                result.append(
                    name.strip().lower()
                )

        elif isinstance(skill, str):

            result.append(
                skill.strip().lower()
            )

    return result


def extract_jd_skills(job_description):
    """Extract required and preferred JD skills."""

    required_skills = job_description.get(
        "required_skills",
        []
    )

    preferred_skills = job_description.get(
        "preferred_skills",
        []
    )

    return [
        skill.strip().lower()
        for skill in (
            required_skills
            + preferred_skills
        )
        if skill
    ]


def calculate_skill_match(
    resume,
    job_description
):
    """
    Calculate skill match between
    resume skills and JD skills.
    """

    resume_skills = set(
        extract_resume_skill_names(
            resume.get(
                "skills",
                []
            )
        )
    )

    jd_skills = set(
        extract_jd_skills(
            job_description
        )
    )

    if not jd_skills:
        return 0.0

    matched_skills = (
        resume_skills.intersection(
            jd_skills
        )
    )

    return round(
        len(matched_skills)
        / len(jd_skills),
        4
    )


def build_resume_experience_text(resume):
    """Create text from resume experience."""

    experience = resume.get(
        "experience",
        []
    )

    experience_text = []

    for item in experience:

        designation = item.get(
            "designation",
            ""
        )

        company = item.get(
            "company",
            ""
        )

        experience_text.append(
            f"{designation} {company}"
        )

    return " ".join(
        experience_text
    )


def build_jd_experience_text(
    job_description
):
    """Create text from JD experience requirement."""

    experience_required = (
        job_description.get(
            "experience_required",
            {}
        )
    )

    minimum_years = experience_required.get(
        "minimum_years"
    )

    maximum_years = experience_required.get(
        "maximum_years"
    )

    if minimum_years is None:
        return ""

    if maximum_years is None:

        return (
            f"{minimum_years} years "
            "of software development experience"
        )

    return (
        f"{minimum_years} to "
        f"{maximum_years} years "
        "of software development experience"
    )


def calculate_experience_relevance(
    resume,
    job_description
):
    """
    Calculate semantic similarity between
    resume experience and JD experience.
    """

    resume_experience = (
        build_resume_experience_text(
            resume
        )
    )

    jd_experience = (
        build_jd_experience_text(
            job_description
        )
    )

    if (
        not resume_experience
        or not jd_experience
    ):
        return 0.0

    return calculate_similarity(
        resume_experience,
        jd_experience
    )


def calculate_education_alignment(
    resume,
    job_description
):
    """Calculate education alignment."""

    education = resume.get(
        "education",
        []
    )

    education_requirements = (
        job_description.get(
            "education_requirements",
            {}
        )
    )

    required_fields = (
        education_requirements.get(
            "fields",
            []
        )
    )

    if not education or not required_fields:
        return 0.0

    required_fields = [
        field.strip().lower()
        for field in required_fields
    ]

    matched = 0

    for education_item in education:

        resume_field = education_item.get(
            "field",
            education_item.get(
                "field_of_study",
                ""
            )
        )

        if not resume_field:
            continue

        resume_field = (
            resume_field.strip().lower()
        )

        for required_field in required_fields:

            if (
                required_field in resume_field
                or resume_field in required_field
            ):
                matched += 1
                break

    return round(
        matched / len(required_fields),
        4
    )


def build_resume_semantic_text(
    resume
):
    """Build important resume information into one text."""

    summary = resume.get(
        "professional_summary",
        ""
    )

    skills = " ".join(
        extract_resume_skill_names(
            resume.get(
                "skills",
                []
            )
        )
    )

    experience = (
        build_resume_experience_text(
            resume
        )
    )

    education_text = []

    for education in resume.get(
        "education",
        []
    ):

        degree = education.get(
            "degree",
            ""
        )

        field = education.get(
            "field",
            education.get(
                "field_of_study",
                ""
            )
        )

        education_text.append(
            f"{degree} {field}"
        )

    return " ".join([
        summary,
        skills,
        experience,
        " ".join(education_text)
    ])


def build_jd_semantic_text(
    job_description
):
    """Build important JD information into text."""

    job_title = job_description.get(
        "job_title",
        ""
    )

    required_skills = " ".join(
        job_description.get(
            "required_skills",
            []
        )
    )

    preferred_skills = " ".join(
        job_description.get(
            "preferred_skills",
            []
        )
    )

    normalized_text = job_description.get(
        "normalized_text",
        ""
    )

    return " ".join([
        job_title,
        required_skills,
        preferred_skills,
        normalized_text
    ])


def calculate_semantic_similarity(
    resume,
    job_description
):
    """Calculate resume-to-JD semantic similarity."""

    resume_text = (
        build_resume_semantic_text(
            resume
        )
    )

    jd_text = (
        build_jd_semantic_text(
            job_description
        )
    )

    if not resume_text or not jd_text:
        return 0.0

    return calculate_similarity(
        resume_text,
        jd_text
    )


def generate_scores(
    resumes,
    job_description
):
    """Generate ATS scores for all candidates."""

    candidates = []

    for resume in resumes:

        candidate_id = resume.get(
            "candidate_id"
        )

        skill_match = (
            calculate_skill_match(
                resume,
                job_description
            )
        )

        experience_relevance = (
            calculate_experience_relevance(
                resume,
                job_description
            )
        )

        education_alignment = (
            calculate_education_alignment(
                resume,
                job_description
            )
        )

        semantic_similarity = (
            calculate_semantic_similarity(
                resume,
                job_description
            )
        )

        score = generate_candidate_score(
            skill_match=skill_match,
            experience_relevance=experience_relevance,
            education_alignment=education_alignment,
            semantic_similarity=semantic_similarity
        )

        candidates.append({
            "candidate_id": candidate_id,
            "score": score["final_score"],
            "match_level": score["match_level"],
            "score_breakdown": score[
                "score_breakdown"
            ],
            "weights": score["weights"]
        })

    return candidates


def save_json(
    data,
    file_path
):
    """Save data as formatted JSON."""

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def run_ranking_pipeline():
    """Run the complete candidate ranking pipeline."""

    print("Loading resumes...")

    resumes = load_resumes()

    print(
        f"Loaded {len(resumes)} resumes."
    )

    print(
        "Loading job description..."
    )

    job_description = load_json(
        JD_FILE
    )

    print(
        "Generating ATS scores..."
    )

    candidates = generate_scores(
        resumes,
        job_description
    )

    save_json(
        candidates,
        SCORE_FILE
    )

    print(
        f"Candidate scores saved to: "
        f"{SCORE_FILE}"
    )

    print(
        "Ranking candidates..."
    )

    ranked_candidates = (
        shortlist_candidates(
            candidates
        )
    )

    save_json(
        ranked_candidates,
        RANKED_FILE
    )

    print(
        f"Ranked candidates saved to: "
        f"{RANKED_FILE}"
    )

    return ranked_candidates


if __name__ == "__main__":

    results = run_ranking_pipeline()

    print("\nFINAL CANDIDATE RANKING")
    print("=" * 60)

    for candidate in results:

        print(
            f"Rank {candidate['rank']}: "
            f"{candidate['candidate_id']} | "
            f"Score: {candidate['score']} | "
            f"Status: {candidate['status']}"
        )