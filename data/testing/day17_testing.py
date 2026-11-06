import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

CSV_EVAL_FILE = (
    BASE_DIR / "data" / "testing" / "day17_candidate_job_evaluation.csv"
)
OUTPUT_FILE = (
    BASE_DIR / "data" / "testing" / "ats_testing_results.json"
)

# Ground truth expected suitable pairings across the 50 candidate-job pairs
EXPECTED_SUITABLE_PAIRS = {
    ("CAND001", "JOB001"),  # Software Eng -> Python Dev
    ("CAND001", "JOB005"),  # Software Eng -> Java Dev
    ("CAND006", "JOB002"),  # HR Recruiter -> HR Recruiter
    ("CAND010", "JOB002"),  # HR Recruiter -> HR Recruiter
    ("CAND007", "JOB003"),  # Data Analyst -> Data Analyst
    ("CAND009", "JOB004"),  # AI/ML Engineer -> ML Engineer
    ("CAND009", "JOB001"),  # AI/ML Engineer -> Python Dev (Secondary fit)
}

POSITIVE_STATUSES = {"Review", "Shortlisted", "Moderate Match", "Good Match"}


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
        "total_evaluations": total,
        "accuracy": round(accuracy * 100, 2),
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "f1_score": round(f1_score * 100, 2),
    }


def main():
    if not CSV_EVAL_FILE.exists():
        raise FileNotFoundError(f"Required CSV evaluation file not found: {CSV_EVAL_FILE}")

    evaluations = []
    with CSV_EVAL_FILE.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for raw_row in reader:
            row = {
                k.strip(): (v.strip() if v else "")
                for k, v in raw_row.items()
                if k is not None
            }
            if row.get("candidate_id") and row.get("job_id"):
                evaluations.append(row)

    tp = tn = fp = fn = 0
    comparisons = []
    mismatches = []
    job_metrics = {}

    for row in evaluations:
        cand_id = row["candidate_id"]
        job_id = row["job_id"]
        job_title = row.get("job_title", job_id)
        ai_score = float(row.get("ats_score", 0))
        ai_status = row.get("ats_status", "Rejected")

        # Determine ground truth status
        is_ground_truth_suitable = (cand_id, job_id) in EXPECTED_SUITABLE_PAIRS
        manual_decision = "Review" if is_ground_truth_suitable else "Rejected"

        ai_positive = ai_status in POSITIVE_STATUSES
        manual_positive = is_ground_truth_suitable

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

        comp = {
            "candidate_id": cand_id,
            "job_id": job_id,
            "job_title": job_title,
            "designation": row.get("resume_designation", ""),
            "ai_score": ai_score,
            "ai_status": ai_status,
            "manual_status": manual_decision,
            "classification": classification,
        }
        comparisons.append(comp)

        if ai_positive != manual_positive:
            mismatches.append(comp)

    overall_metrics = calculate_metrics(tp, tn, fp, fn)

    results = {
        "overall_summary": overall_metrics,
        "confusion_matrix": {
            "true_positive": tp,
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn
        },
        "mismatch_count": len(mismatches),
        "mismatch_cases": mismatches,
        "all_evaluations": comparisons
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    print("==================================================")
    print("Day 17 ATS Full Matrix Testing (All 50 Pairs)")
    print("==================================================")
    print(f"Total Evaluations: {overall_metrics['total_evaluations']}")
    print(f"Accuracy:  {overall_metrics['accuracy']}%")
    print(f"Precision: {overall_metrics['precision']}%")
    print(f"Recall:    {overall_metrics['recall']}%")
    print(f"F1-score:  {overall_metrics['f1_score']}%")
    print(f"Total Mismatches Found: {len(mismatches)}")
    print("--------------------------------------------------")
    print("Mismatch Cases Breakdown:")
    for m in mismatches:
        print(f"  [{m['job_title']}] {m['candidate_id']} ({m['designation']}): AI gave {m['ai_status']} ({m['ai_score']}%), Expected {m['manual_status']} -> {m['classification']}")
    print("--------------------------------------------------")
    print(f"Detailed output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()