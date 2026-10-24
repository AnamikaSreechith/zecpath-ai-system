import json
from pathlib import Path

from matching.ats_scoring_engine import (
    generate_candidate_score
)

from matching.semantic_matching_engine import (
    calculate_resume_jd_similarity
)

from matching.fairness_normalization import (
    normalize_candidate_for_scoring
)

from matching.candidate_ranking_engine import (
    shortlist_candidates
)


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RESUME_DIR = BASE_DIR / "data" / "resumes"

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


# ---------------------------------------------------------
# LOAD RESUMES
# ---------------------------------------------------------

def load_resumes(resume_directory):
    """
    Load all JSON resumes from the resume directory.
    """

    resumes = []

    for file_path in sorted(
        Path(resume_directory).glob("*.json")
    ):
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            resume = json.load(file)

            resumes.append(resume)

    return resumes


# ---------------------------------------------------------
# LOAD JOB DESCRIPTION
# ---------------------------------------------------------

def load_job_description(jd_file):
    """
    Load the parsed job description.
    """

    with open(
        jd_file,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ---------------------------------------------------------
# EXTRACT RESUME SKILLS
# ---------------------------------------------------------

def extract_resume_skills(resume):
    """
    Extract normalized skills from a resume.
    """

    skills = resume.get(
        "normalized_skills",
        []
    )

    if not skills:
        skills = resume.get(
            "skills",
            []
        )

    extracted_skills = []

    for skill in skills:

        if isinstance(skill, dict):
            name = skill.get("name")

            if name:
                extracted_skills.append(
                    str(name).lower()
                )

        else:
            extracted_skills.append(
                str(skill).lower()
            )

    return extracted_skills


# ---------------------------------------------------------
# SKILL MATCH
# ---------------------------------------------------------

def calculate_skill_match(
    resume_skills,
    jd_required_skills,
    jd_preferred_skills
):
    """
    Calculate skill match between resume and JD.

    Required skills have higher importance than
    preferred skills.
    """

    resume_skill_set = set(
        skill.lower()
        for skill in resume_skills
    )

    required_skills = set(
        skill.lower()
        for skill in jd_required_skills
    )

    preferred_skills = set(
        skill.lower()
        for skill in jd_preferred_skills
    )

    if not required_skills and not preferred_skills:
        return 0.0

    required_match = (
        len(
            resume_skill_set
            & required_skills
        )
        / len(required_skills)
        if required_skills
        else 0
    )

    preferred_match = (
        len(
            resume_skill_set
            & preferred_skills
        )
        / len(preferred_skills)
        if preferred_skills
        else 0
    )

    if required_skills and preferred_skills:

        score = (
            required_match * 0.70
            + preferred_match * 0.30
        )

    elif required_skills:

        score = required_match

    else:

        score = preferred_match

    return round(
        score,
        4
    )


# ---------------------------------------------------------
# EXPERIENCE RELEVANCE
# ---------------------------------------------------------

def calculate_experience_relevance(
    resume,
    minimum_years,
    maximum_years
):
    """
    Estimate experience relevance based on the
    candidate's listed experience.
    """

    experience = resume.get(
        "experience",
        []
    )

    if not experience:
        return 0.0

    number_of_roles = len(experience)

    # Basic normalized estimate.
    # Detailed duration calculation can be
    # added later when required.

    estimated_years = number_of_roles * 0.5

    if estimated_years >= minimum_years:

        if maximum_years:
            if estimated_years <= maximum_years:
                return 1.0

            return 0.85

        return 1.0

    return round(
        estimated_years / max(
            minimum_years,
            1
        ),
        4
    )


# ---------------------------------------------------------
# EDUCATION ALIGNMENT
# ---------------------------------------------------------

def calculate_education_alignment(
    resume,
    education_requirements
):
    """
    Check whether the candidate's education aligns
    with the JD requirements.
    """

    education = resume.get(
        "education",
        []
    )

    if not education:
        return 0.0

    minimum_level = (
        education_requirements
        .get("minimum_level", "")
        .lower()
    )

    required_fields = [
        field.lower()
        for field in education_requirements.get(
            "fields",
            []
        )
    ]

    for qualification in education:

        degree = str(
            qualification.get(
                "degree",
                ""
            )
        ).lower()

        field = str(
            qualification.get(
                "field",
                ""
            )
        ).lower()

        degree_match = (
            "bachelor" in minimum_level
            and "bachelor" in degree
        )

        field_match = any(
            required_field in field
            for required_field in required_fields
        )

        if degree_match and field_match:
            return 1.0

        if field_match:
            return 0.8

        if degree_match:
            return 0.7

    return 0.0


# ---------------------------------------------------------
# BUILD EXPERIENCE TEXT
# ---------------------------------------------------------

def build_experience_text(resume):
    """
    Convert resume experience information
    into text for semantic matching.
    """

    experience = resume.get(
        "experience",
        []
    )

    text_parts = []

    for item in experience:

        designation = item.get(
            "designation",
            ""
        )

        company = item.get(
            "company",
            ""
        )

        text_parts.append(
            f"{designation} {company}"
        )

    return " ".join(
        text_parts
    )


# ---------------------------------------------------------
# BUILD PROJECT TEXT
# ---------------------------------------------------------

def build_project_text(resume):
    """
    Extract project descriptions from a resume.
    """

    projects = resume.get(
        "projects",
        []
    )

    text_parts = []

    for project in projects:

        if isinstance(project, dict):

            text_parts.append(
                str(
                    project.get(
                        "name",
                        ""
                    )
                )
            )

            text_parts.append(
                str(
                    project.get(
                        "description",
                        ""
                    )
                )
            )

        else:

            text_parts.append(
                str(project)
            )

    return " ".join(
        text_parts
    )


# ---------------------------------------------------------
# GENERATE CANDIDATE SCORES
# ---------------------------------------------------------

def generate_scores(
    resumes,
    jd
):
    """
    Generate ATS scores for all candidates.
    """

    candidate_scores = []

    jd_required_skills = jd.get(
        "required_skills",
        []
    )

    jd_preferred_skills = jd.get(
        "preferred_skills",
        []
    )

    experience_requirements = jd.get(
        "experience_required",
        {}
    )

    education_requirements = jd.get(
        "education_requirements",
        {}
    )

    jd_experience_text = jd.get(
        "normalized_text",
        ""
    )

    jd_project_text = jd.get(
        "normalized_text",
        ""
    )

    for resume in resumes:

        candidate_id = resume.get(
            "candidate_id",
            "UNKNOWN"
        )

        # ---------------------------------------------
        # SKILL MATCH
        # ---------------------------------------------

        resume_skills = extract_resume_skills(
            resume
        )

        skill_match = calculate_skill_match(
            resume_skills,
            jd_required_skills,
            jd_preferred_skills
        )

        # ---------------------------------------------
        # EXPERIENCE
        # ---------------------------------------------

        experience_relevance = (
            calculate_experience_relevance(
                resume,
                experience_requirements.get(
                    "minimum_years",
                    0
                ),
                experience_requirements.get(
                    "maximum_years",
                    0
                )
            )
        )

        # ---------------------------------------------
        # EDUCATION
        # ---------------------------------------------

        education_alignment = (
            calculate_education_alignment(
                resume,
                education_requirements
            )
        )

        # ---------------------------------------------
        # SEMANTIC MATCHING
        # ---------------------------------------------

        resume_experience_text = (
            build_experience_text(
                resume
            )
        )

        resume_project_text = (
            build_project_text(
                resume
            )
        )

        semantic_result = (
            calculate_resume_jd_similarity(
                " ".join(
                    resume_skills
                ),
                " ".join(
                    jd_required_skills
                    + jd_preferred_skills
                ),
                resume_experience_text,
                jd_experience_text,
                resume_project_text,
                jd_project_text
            )
        )

        semantic_similarity = (
            semantic_result[
                "overall_similarity"
            ]
        )

        # ---------------------------------------------
        # FINAL ATS SCORE
        # ---------------------------------------------

        score_result = generate_candidate_score(
            skill_match,
            experience_relevance,
            education_alignment,
            semantic_similarity
        )

        candidate_scores.append({

            "candidate_id": candidate_id,

            "score": score_result[
                "final_score"
            ],

            "match_level": score_result[
                "match_level"
            ],

            "score_breakdown": score_result[
                "score_breakdown"
            ],

            "weights": score_result[
                "weights"
            ]
        })

    return candidate_scores


# ---------------------------------------------------------
# MAIN RANKING PIPELINE
# ---------------------------------------------------------

def run_ranking_pipeline(
    resume_directory,
    jd_file,
    score_file,
    ranked_file
):
    """
    Complete candidate ranking pipeline.

    Flow:

    Resumes
        ↓
    Normalization
        ↓
    Bias reduction
        ↓
    ATS scoring
        ↓
    Ranking
        ↓
    Shortlisting
    """

    print("Loading resumes...")

    resumes = load_resumes(
        resume_directory
    )

    print(
        f"Loaded {len(resumes)} resumes."
    )

    # ---------------------------------------------
    # DAY 15 FAIRNESS NORMALIZATION
    # ---------------------------------------------

    resumes = [
        normalize_candidate_for_scoring(
            resume
        )
        for resume in resumes
    ]

    print(
        "Resume normalization completed."
    )

    # ---------------------------------------------
    # LOAD JD
    # ---------------------------------------------

    print(
        "Loading job description..."
    )

    jd = load_job_description(
        jd_file
    )

    # ---------------------------------------------
    # GENERATE SCORES
    # ---------------------------------------------

    print(
        "Generating ATS scores..."
    )

    candidate_scores = generate_scores(
        resumes,
        jd
    )

    with open(
        score_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            candidate_scores,
            file,
            indent=4
        )

    print(
        f"Candidate scores saved to: {score_file}"
    )

    # ---------------------------------------------
    # RANK + SHORTLIST
    # ---------------------------------------------

    print(
        "Ranking candidates..."
    )

    ranked_candidates = shortlist_candidates(
        candidate_scores
    )

    with open(
        ranked_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            ranked_candidates,
            file,
            indent=4
        )

    print(
        f"Ranked candidates saved to: {ranked_file}"
    )

    return ranked_candidates


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":

    results = run_ranking_pipeline(
        resume_directory=RESUME_DIR,
        jd_file=JD_FILE,
        score_file=SCORE_FILE,
        ranked_file=RANKED_FILE
    )

    print()
    print(
        "FINAL CANDIDATE RANKING"
    )
    print(
        "=" * 60
    )

    for candidate in results:

        print(
            f"Rank {candidate['rank']}: "
            f"{candidate['candidate_id']} | "
            f"Score: {candidate['score']} | "
            f"Status: {candidate['status']}"
        )