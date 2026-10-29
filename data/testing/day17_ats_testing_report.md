
# Day 17 – ATS System Testing Report

## 1. Objective

The objective of Day 17 was to evaluate the existing Applicant Tracking System (ATS) by comparing AI-generated candidate decisions with manually assigned review decisions.

The testing focused on candidate ranking consistency, classification metrics, mismatch identification, and areas requiring further improvement.

## 2. Testing Scope

The test used the Day 14 candidate ranking output and the manually reviewed test cases.

- AI results: `data/testing/day14_candidate_ranking.json`
- Manual labels: `data/testing/ats_test_cases.json`
- Testing script: `data/testing/day17_testing.py`
- Generated results: `data/testing/ats_testing_results.json`

A total of 10 candidates were evaluated.

## 3. Testing Methodology

The testing script matched AI results with manual decisions using candidate IDs.

The decisions were compared using the following classification rules:

- True Positive (TP): AI and manual review both classify the candidate as Review.
- True Negative (TN): AI and manual review both classify the candidate as Rejected.
- False Positive (FP): AI classifies the candidate as Review, while manual review classifies the candidate as Rejected.
- False Negative (FN): AI classifies the candidate as Rejected, while manual review classifies the candidate as Review.

The script calculated accuracy, precision, recall, and F1-score from the resulting confusion matrix.

## 4. Evaluation Results

| Metric | Result |
|---|---:|
| Total candidates | 10 |
| Accuracy | 100% |
| Precision | 100% |
| Recall | 100% |
| F1-score | 100% |
| Mismatches | 0 |

All AI decisions matched the supplied manual labels for this test set.

## 5. Confusion Matrix

| Actual / Predicted | Review | Rejected |
|---|---:|---:|
| Manual Review | 1 | 0 |
| Manual Rejected | 0 | 9 |

- True Positives: 1
- True Negatives: 9
- False Positives: 0
- False Negatives: 0

The calculated metrics are correct for these 10 labeled cases.

## 6. Candidate Comparison

| Candidate ID | AI Score | AI Decision | Manual Decision | Result |
|---|---:|---|---|---|
| CAND001 | 60.28 | Review | Review | True Positive |
| CAND002 | 47.37 | Rejected | Rejected | True Negative |
| CAND009 | 47.22 | Rejected | Rejected | True Negative |
| CAND004 | 46.86 | Rejected | Rejected | True Negative |
| CAND010 | 42.68 | Rejected | Rejected | True Negative |
| CAND006 | 42.58 | Rejected | Rejected | True Negative |
| CAND005 | 41.17 | Rejected | Rejected | True Negative |
| CAND007 | 40.55 | Rejected | Rejected | True Negative |
| CAND003 | 40.09 | Rejected | Rejected | True Negative |
| CAND008 | 28.77 | Rejected | Rejected | True Negative |

## 7. Test Coverage and Limitations

The current test dataset contains:

- 10 technical-role candidates.
- 10 fresher-level profiles.
- 1 manually positive Review example.
- 9 manually negative Rejected examples.

The test does not yet establish performance across non-technical roles, senior-level candidates, or a broader range of job descriptions.

The 100% metrics represent agreement with the supplied manual labels. They should not be interpreted as proof of 100% real-world hiring accuracy because the dataset is small and has limited diversity.

## 8. Issues Identified

No mismatches were detected in the current test set.

However, additional validation is required to assess:

- Performance on non-technical job descriptions.
- Performance on experienced and senior candidates.
- False positives and false negatives across a larger dataset.
- Reliability of manual labels.
- Fairness and consistency across different candidate profiles.
- The suitability of current review and shortlisting thresholds.

## 9. Improvement Plan

The following improvements are recommended:

1. Expand the dataset with non-technical, mid-level, and senior profiles.
2. Increase the number of manually reviewed positive examples.
3. Validate labels and document recruiter decision reasons.
4. Test scoring against multiple job descriptions.
5. Evaluate thresholds on a larger validation dataset.
6. Conduct fairness and consistency tests.
7. Improve resume parsing and semantic skill matching.
8. Continue monitoring API, parsing, and scoring errors.

## 10. Conclusion

The Day 17 ATS comparison script executed successfully and evaluated all 10 candidates. The generated results reported 100% accuracy, precision, recall, and F1-score, with zero mismatches against the supplied manual labels.

The results confirm consistency on the current test dataset. Broader testing remains necessary before drawing conclusions about general ATS performance.

The generated results are available in `data/testing/ats_testing_results.json`, and future testing priorities are documented in `data/testing/improvement_backlog.md`.
