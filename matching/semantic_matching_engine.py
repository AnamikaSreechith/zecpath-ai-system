
from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load the semantic embedding model once.
model = SentenceTransformer("all-MiniLM-L6-v2")


@lru_cache(maxsize=512)
def generate_embedding(text):
    """
    Generate and cache embeddings for repeated text.
    Reusing cached embeddings avoids repeated model inference.
    """

    if not text or not text.strip():
        return None

    return model.encode(
        text,
        convert_to_numpy=True
    )


def calculate_similarity(text1, text2):
    """
    Calculate semantic similarity between two texts.
    Returns a score between 0 and 1.
    """

    if not text1 or not text2:
        return 0.0

    embedding1 = generate_embedding(text1)
    embedding2 = generate_embedding(text2)

    similarity = cosine_similarity(
        [embedding1],
        [embedding2]
    )[0][0]

    return round(float(similarity), 4)


def calculate_section_similarity(
    resume_section,
    jd_section
):
    """
    Calculate semantic similarity between
    a resume section and its corresponding JD section.
    """

    if not resume_section or not jd_section:
        return 0.0

    return calculate_similarity(
        resume_section,
        jd_section
    )


def calculate_resume_jd_similarity(
    resume_skills,
    jd_skills,
    resume_experience,
    jd_experience,
    resume_projects,
    jd_projects
):
    """
    Calculate semantic similarity for skills,
    experience, and projects.
    """

    skills_score = calculate_section_similarity(
        resume_skills,
        jd_skills
    )

    experience_score = calculate_section_similarity(
        resume_experience,
        jd_experience
    )

    projects_score = calculate_section_similarity(
        resume_projects,
        jd_projects
    )

    overall_score = (
        skills_score * 0.40
        + experience_score * 0.35
        + projects_score * 0.25
    )

    return {
        "skills_similarity": skills_score,
        "experience_similarity": experience_score,
        "projects_similarity": projects_score,
        "overall_similarity": round(
            overall_score,
            4
        ),
        "match_level": classify_match(
            overall_score
        )
    }


def classify_match(similarity_score):
    """
    Classify the overall semantic similarity score.
    """

    if similarity_score >= 0.80:
        return "Strong Match"

    elif similarity_score >= 0.60:
        return "Moderate Match"

    else:
        return "Low Match"
