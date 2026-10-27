from matching.fairness_normalization import (
    normalize_skill,
    normalize_skill_list,
    normalize_text,
    mask_non_essential_attributes,
    normalize_candidate_for_scoring
)


print("=" * 80)
print("DAY 15 - FAIRNESS, NORMALIZATION & BIAS REDUCTION")
print("=" * 80)


# =========================================================
# 1. SKILL NORMALIZATION
# =========================================================

test_skills = [
    "Python 3",
    "Python3",
    "Py",
    "JS",
    "PowerBI",
    "Postgres",
    "React.js",
    "NodeJS",
    "RESTful API",
    "AWS"
]

print("\nSkill Normalization:")
print("-" * 80)

for skill in test_skills:

    print(
        f"{skill:20} -> {normalize_skill(skill)}"
    )


# =========================================================
# 2. SKILL LIST NORMALIZATION
# =========================================================

skills = [
    "Python 3",
    "python",
    "Py",
    "JS",
    "javascript",
    "PowerBI"
]

normalized_skills = normalize_skill_list(
    skills
)

print("\nNormalized Skill List:")
print("-" * 80)
print(normalized_skills)


# =========================================================
# 3. TEXT NORMALIZATION
# =========================================================

sample_text = """
    Python Developer   with   REST APIs
    and SQL experience.
"""

print("\nText Normalization:")
print("-" * 80)
print(
    normalize_text(sample_text)
)


# =========================================================
# 4. PERSONAL ATTRIBUTE MASKING
# =========================================================

candidate = {
    "candidate_id": "CAND001",
    "name": "Test Candidate",
    "age": 24,
    "gender": "Female",
    "email": "test@example.com",
    "phone": "9876543210",
    "address": "Test Address",
    "skills": [
        "Python 3",
        "SQL",
        "RESTful API"
    ],
    "professional_summary":
        "Python developer with API experience."
}

masked_candidate = mask_non_essential_attributes(
    candidate
)

print("\nMasked Candidate:")
print("-" * 80)
print(masked_candidate)


# =========================================================
# 5. COMPLETE FAIRNESS NORMALIZATION
# =========================================================

normalized_candidate = normalize_candidate_for_scoring(
    candidate
)

print("\nFinal Normalized Candidate:")
print("-" * 80)
print(normalized_candidate)


# =========================================================
# 6. VERIFICATION
# =========================================================

assert normalize_skill("Python 3") == "python"
assert normalize_skill("Py") == "python"
assert normalize_skill("JS") == "javascript"
assert normalize_skill("PowerBI") == "power bi"
assert normalize_skill("Postgres") == "postgresql"

assert "name" not in normalized_candidate
assert "age" not in normalized_candidate
assert "gender" not in normalized_candidate
assert "email" not in normalized_candidate
assert "phone" not in normalized_candidate
assert "address" not in normalized_candidate

assert "normalized_skills" in normalized_candidate

print("\n" + "=" * 80)
print("DAY 15 FAIRNESS & NORMALIZATION TEST PASSED")
print("=" * 80)