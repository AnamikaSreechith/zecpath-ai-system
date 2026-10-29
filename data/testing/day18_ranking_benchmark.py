
import json
import random
import statistics
import time
import sys
from pathlib import Path
from heapq import nlargest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data" / "resumes"
CANDIDATE_COUNT = 10
REPEATS = 1000
TOP_N = 5


def load_candidates():
    candidates = []

    for path in sorted(
        DATA_DIR.glob("resume*.json"),
        key=lambda p: int(p.stem.replace("resume", ""))
    )[:CANDIDATE_COUNT]:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)

        # Use an existing score if available.
        # Otherwise, benchmark the ranking algorithm with a
        # deterministic placeholder score for comparison only.
        score = data.get("score")

        if score is None:
            score = sum(
                len(data.get(field, []))
                for field in ("skills", "experience", "education")
                if isinstance(data.get(field, []), list)
            )

        candidates.append({
            "candidate_id": data.get("candidate_id", path.stem),
            "score": float(score),
        })

    return candidates


def full_sort_top(candidates):
    return sorted(
        candidates,
        key=lambda candidate: float(candidate["score"]),
        reverse=True
    )[:TOP_N]


def optimized_top(candidates):
    return nlargest(
        TOP_N,
        candidates,
        key=lambda candidate: float(candidate["score"])
    )


def measure(function, candidates):
    timings = []

    for _ in range(REPEATS):
        start = time.perf_counter()
        function(candidates)
        timings.append(time.perf_counter() - start)

    return statistics.median(timings)


def main():
    candidates = load_candidates()

    if len(candidates) != CANDIDATE_COUNT:
        print(
            f"Expected {CANDIDATE_COUNT} candidates; "
            f"found {len(candidates)}."
        )
        return

    # Warm up both implementations.
    full_sort_top(candidates)
    optimized_top(candidates)

    baseline = measure(full_sort_top, candidates)
    optimized = measure(optimized_top, candidates)

    print("\nDAY 18 - RANKING BENCHMARK")
    print("-" * 45)
    print(f"Candidates: {len(candidates)}")
    print(f"Top candidates requested: {TOP_N}")
    print(f"Repetitions per method: {REPEATS}")
    print(f"Full-sort median: {baseline:.9f} seconds")
    print(f"Heap-selection median: {optimized:.9f} seconds")

    if optimized < baseline:
        improvement = (baseline - optimized) / baseline * 100
        print(f"Measured time reduction: {improvement:.2f}%")
    else:
        print(
            "No measured speed improvement at this dataset size."
        )

    print(
        "\nNote: this measures ranking selection only, "
        "not the complete ATS pipeline."
    )


if __name__ == "__main__":
    main()
