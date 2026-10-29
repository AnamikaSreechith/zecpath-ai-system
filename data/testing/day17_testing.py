
import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parents[2]

AI_RESULTS_FILE = (
    BASE_DIR / "data" / "testing" / "day14_candidate_ranking.json"
)
MANUAL_REVIEW_FILE = (
    BASE_DIR / "data" / "testing" / "ats_test_cases.json"
)
OUTPUT_FILE = (
    BASE_DIR / "data" / "testing" / "ats_testing_results.json"
)


def load_json(file_path):
    """Load JSON data and report a clear error if it is unavailable."""
    if not file_path.exists():
        raise FileNotFoundError(f"Required file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def calculate_metrics(tp, tn, fp, fn):
    total = tp + tn + fp + fn

    accuracy = (tp + tn) / total if total else 0
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1_score = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0
    )

    return {
        "total_candidates": total,
        "accuracy": round(accuracy * 100, 2),
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "f1_score": round(f1_score * 100, 2),
    }


def main():
    ai_results = load_json(AI_RESULTS_FILE)
    manual_reviews = load_json(MANUAL_REVIEW_FILE)

    # Build lookup tables and detect duplicate IDs.
    ai_ids = [item["candidate_id"] for item in ai_results]
    manual_ids = [item["candidate_id"] for item in manual_reviews]

    if len(ai_ids) != len(set(ai_ids)):
        raise ValueError("Duplicate candidate IDs found in Day 14 results.")

    if len(manual_ids) != len(set(manual_ids)):
        raise ValueError("Duplicate candidate IDs found in manual test cases.")

    ai_lookup = {item["candidate_id"]: item for item in ai_results}
    manual_lookup = {item["candidate_id"]: item for item in manual_reviews}

    ai_only = sorted(set(ai_lookup) - set(manual_lookup))
    manual_only = sorted(set(manual_lookup) - set(ai_lookup))

    if ai_only or manual_only:
        raise ValueError(
            "Candidate ID mismatch.\n"
            f"AI-only candidates: {ai_only}\n"
            f"Manual-only candidates: {manual_only}"
        )

    tp = tn = fp = fn = 0
    comparisons = []
    mismatches = []

    # Positive means Review; negative means Rejected.
    positive_statuses = {"Review", "Shortlisted"}

    for candidate_id, ai in ai_lookup.items():
        manual = manual_lookup[candidate_id]

        ai_status = ai["status"]
        manual_status = manual["manual_decision"]

        if ai_status not in positive_statuses | {"Rejected"}:
            raise ValueError(
                f"Unexpected AI status for {candidate_id}: {ai_status}"
            )

        if manual_status not in positive_statuses | {"Rejected"}:
            raise ValueError(
                f"Unexpected manual decision for {candidate_id}: "
                f"{manual_status}"
            )

        ai_positive = ai_status in positive_statuses
        manual_positive = manual_status in positive_statuses

        if ai_positive and manual_positive:
            classification = "True Positive"
            tp += 1
        elif not ai_positive and not manual_positive:
            classification = "True Negative"
            tn += 1
        elif ai_positive and not manual_positive:
            classification = "False Positive"
            fp += 1
        else:
            classification = "False Negative"
            fn += 1

        comparison = {
            "candidate_id": candidate_id,
            "role_type": manual.get("role_type", "Not specified"),
            "experience_level": manual.get(
                "experience_level", "Not specified"
            ),
            "ai_score": ai["score"],
            "ai_status": ai_status,
            "manual_status": manual_status,
            "classification": classification,
            "manual_reason": manual.get("reason", "")
        }

        comparisons.append(comparison)

        if ai_status != manual_status:
            mismatches.append(comparison)

    metrics = calculate_metrics(tp, tn, fp, fn)

    # Report how many test examples belong to each category.
    role_distribution = dict(
        Counter(item.get("role_type", "Not specified")
                for item in manual_reviews)
    )
    experience_distribution = dict(
        Counter(item.get("experience_level", "Not specified")
                for item in manual_reviews)
    )

    results = {
        "test_summary": metrics,
        "confusion_matrix": {
            "true_positive": tp,
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn
        },
        "mismatch_count": len(mismatches),
        "mismatch_cases": mismatches,
        "coverage": {
            "ai_results_source": str(AI_RESULTS_FILE.relative_to(BASE_DIR)),
            "manual_labels_source": str(
                MANUAL_REVIEW_FILE.relative_to(BASE_DIR)
            ),
            "role_type_distribution": role_distribution,
            "experience_level_distribution": experience_distribution,
            "note": (
                "Metrics measure agreement with the supplied manual labels. "
                "They do not establish real-world hiring accuracy."
            )
        },
        "candidate_comparison": comparisons
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    print("Day 17 ATS testing completed.")
    print(f"Candidates evaluated: {metrics['total_candidates']}")
    print(f"Accuracy: {metrics['accuracy']}%")
    print(f"Precision: {metrics['precision']}%")
    print(f"Recall: {metrics['recall']}%")
    print(f"F1-score: {metrics['f1_score']}%")
    print(f"Mismatches: {len(mismatches)}")
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
