import sys
import json
import statistics
import time
from pathlib import Path

# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from parsers.resume_parser import extract_resume


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = DATA_DIR / "testing" / "day18_benchmark_output"
RESULT_FILE = DATA_DIR / "testing" / "day18_baseline_10_resumes.json"

TARGET_COUNT = 10
REPEATS = 3

EXCLUDED_DIRS = {
    "testing",
    "extracted_resumes",
    "day18_benchmark_output",
    "__pycache__",
}


def find_resumes():
    """Find up to 10 original PDF or DOCX resumes."""

    resumes = []

    for path in DATA_DIR.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in {".pdf", ".docx"}:
            continue

        relative_parts = path.relative_to(DATA_DIR).parts

        if any(part in EXCLUDED_DIRS for part in relative_parts):
            continue

        resumes.append(path)

    return sorted(
        resumes,
        key=lambda path: str(path).lower()
    )[:TARGET_COUNT]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    resumes = find_resumes()

    if not resumes:
        print("No PDF or DOCX resumes found inside data/.")
        return

    print("\nDAY 18 - ATS PERFORMANCE BASELINE")
    print("-" * 55)
    print(f"Resumes found: {len(resumes)}")
    print(f"Runs per resume: {REPEATS}\n")
    print(f"{'Resume':<28} {'Median time (seconds)':>22}")
    print("-" * 55)

    results = []

    for resume in resumes:
        timings = []

        try:
            for _ in range(REPEATS):
                start = time.perf_counter()

                extract_resume(
                    resume,
                    output_dir=OUTPUT_DIR
                )

                timings.append(time.perf_counter() - start)

            median_time = round(
                statistics.median(timings), 6
            )

            results.append({
                "resume": resume.name,
                "median_processing_seconds": median_time,
            })

            print(f"{resume.name:<28} {median_time:>22.6f}")

        except Exception as exc:
            print(f"{resume.name:<28} FAILED: {exc}")

    successful = len(results)

    report = {
        "benchmark": "Day 18 Baseline",
        "resume_count": len(resumes),
        "successful_count": successful,
        "runs_per_resume": REPEATS,
        "results": results,
    }

    if results:
        report["average_processing_seconds"] = round(
            statistics.mean(
                item["median_processing_seconds"]
                for item in results
            ),
            6,
        )

    with open(RESULT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("-" * 55)
    print(f"Successfully benchmarked: {successful}/{len(resumes)}")

    if results:
        print(
            "Average processing time: "
            f"{report['average_processing_seconds']:.6f} seconds"
        )

    print(f"\nBaseline saved to: {RESULT_FILE}")


if __name__ == "__main__":
    main()
