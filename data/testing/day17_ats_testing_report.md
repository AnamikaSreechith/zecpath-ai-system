# Day 17 – Comprehensive ATS Full-Matrix Testing Report

## 1. Objective
The objective of Day 17 was to evaluate the ATS scoring engine against a complete multi-role matrix (10 diverse candidate resumes evaluated across 5 job roles = 50 total candidate-job evaluations), identifying real-world classification accuracy, precision, recall, and mismatch patterns.

## 2. Testing Scope
- **Evaluation Source:** `data/testing/day17_candidate_job_evaluation.csv`
- **Evaluated Pairs:** 50 total (10 candidates × 5 job descriptions)
- **Roles Tested:** Python Developer (`JOB001`), HR Recruiter (`JOB002`), Data Analyst (`JOB003`), Machine Learning Engineer (`JOB004`), Java Developer (`JOB005`)
- **Testing Script:** `data/testing/day17_testing.py`
- **Output Report:** `data/testing/ats_testing_results.json`

## 3. Evaluation Metrics

| Metric | Result |
|---|---:|
| Total Evaluations | 50 |
| Overall Accuracy | 76.0% |
| Precision | 30.77% |
| Recall | 57.14% |
| F1-Score | 40.0% |
| Total Mismatches | 12 |

## 4. Confusion Matrix

| Actual / Predicted | AI: Review (Positive) | AI: Rejected (Negative) | Total |
|---|---:|---:|---:|
| **Ground Truth: Suitable** | 4 (TP) | 3 (FN) | 7 |
| **Ground Truth: Not Suitable**| 9 (FP) | 34 (TN) | 43 |
| **Total** | 13 | 37 | 50 |

- **True Positives (4):** Accurate shortlisting of domain-matched candidates (e.g., HR candidates for HR Recruiter).
- **True Negatives (34):** Accurate rejection of completely out-of-domain applicants (e.g., Finance candidate rejected for technical roles).
- **False Positives (9):** Unqualified candidates reaching the Review band due to shared foundational keywords (SQL, Python, REST APIs).
- **False Negatives (3):** Qualified candidates missing cutoff by razor-thin margins (e.g., CAND009 scoring 49.76% against a 50% cutoff).

## 5. Mismatch Breakdown & Root Causes

1. **Threshold Boundary Failures (False Negatives):**
   - `CAND009` (AI Engineer Fresher) scored 49.76% for Python Developer. Missing the 50.00% threshold by 0.24% caused an automatic rejection.
2. **Generic Tech Keyword Bleed (False Positives):**
   - `CAND002` (Web Developer) was shortlisted for Python Developer (53.94%) and Java Developer (53.65%) due to generic full-stack and REST API keywords, despite zero Python/Java experience.
   - `CAND004` (Cyber Security) and `CAND005` (Project Manager) passed for Data Analyst (>50%) because of peripheral SQL and dashboarding terms.
3. **Domain Cross-Pollination (False Positives):**
   - `CAND007` (Data Analyst) and `CAND004` (Cyber Security) crossed into the Review threshold for Machine Learning Engineer due to shared Python and mathematics fundamentals.