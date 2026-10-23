import re


def normalize_role(text):
    """Normalize a job role for comparison."""

    return re.sub(
        r"\s+",
        " ",
        text.lower().strip()
    )


def calculate_role_similarity(
    candidate_role,
    target_role
):
    """Calculate similarity between two job roles."""

    candidate_role = normalize_role(
        candidate_role
    )

    target_role = normalize_role(
        target_role
    )

    if not candidate_role or not target_role:
        return 0.0

    if candidate_role == target_role:
        return 1.0

    candidate_words = set(
        candidate_role.split()
    )

    target_words = set(
        target_role.split()
    )

    common_words = (
        candidate_words & target_words
    )

    if not target_words:
        return 0.0

    return len(common_words) / len(
        target_words
    )


def calculate_experience_relevance(
    experiences,
    target_role
):
    """Calculate relevance of candidate experience to a target role."""

    if not experiences:
        return {
            "target_role": target_role,
            "relevance_score": 0.0,
            "relevant_roles": []
        }

    relevant_roles = []

    for experience in experiences:

        score = calculate_role_similarity(
            experience["job_title"],
            target_role
        )

        if score > 0:
            relevant_roles.append({
                "job_title": experience["job_title"],
                "company": experience["company"],
                "similarity_score": round(
                    score,
                    2
                )
            })

    if relevant_roles:

        relevance_score = sum(
            role["similarity_score"]
            for role in relevant_roles
        ) / len(relevant_roles)

    else:
        relevance_score = 0.0

    return {
        "target_role": target_role,
        "relevance_score": round(
            relevance_score,
            2
        ),
        "relevant_roles": relevant_roles
    }