from parsers.resume_parser import parse_resume_text
from ats_engine.ats_scorer import calculate_ats_score
from screening_ai.screening_service import evaluate_screening_response
from interview_ai.question_generator import generate_sample_questions
from scoring.decision_engine import make_preliminary_recommendation
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    logger.info("Zecpath AI workflow started")

    # 1. Resume parsing
    resume_text = (
        "Python developer with experience in SQL "
        "and Machine Learning."
    )

    resume = parse_resume_text(resume_text)
    print("\nResume status:", resume["status"])

    # 2. ATS scoring
    # Skills are manually supplied for this prototype.
    candidate_skills = ["Python", "SQL", "Machine Learning"]
    required_skills = ["Python", "SQL", "Machine Learning", "AWS"]

    ats_result = calculate_ats_score(
        candidate_skills, required_skills
    )
    print("\nATS result:", ats_result)

    # 3. Screening response evaluation
    screening_result = evaluate_screening_response(
        "I have experience in Python and SQL.",
        ["Python", "SQL", "AWS"]
    )
    print("\nScreening result:", screening_result)

    # 4. Interview question generation
    questions = generate_sample_questions("Python Developer")
    print("\nSample interview questions:")

    for question in questions:
        print("-", question)

    # 5. Preliminary recommendation
    recommendation = make_preliminary_recommendation(
        ats_result["score"]
    )
    print("\nPreliminary recommendation:", recommendation)

    logger.info("Zecpath AI workflow completed")


if __name__ == "__main__":
    main()