
# Day 17 – ATS Improvement Backlog

## Current Testing Findings

The ATS was evaluated against 10 candidates using the Day 14 ranking output and manually assigned decisions.

| Metric | Result |
|---|---:|
| Candidates evaluated | 10 |
| Accuracy | 100% |
| Precision | 100% |
| Recall | 100% |
| F1-score | 100% |
| Mismatches | 0 |

All 10 AI decisions matched the supplied manual labels. However, the test set contains only technical fresher profiles, with just one manually positive candidate. These results measure agreement on the current dataset and do not establish real-world ATS accuracy.

## 1. Expand Test Dataset

Increase the number and diversity of resumes used for ATS evaluation.

- Add more technical resumes.
- Add non-technical resumes.
- Include fresher, mid-level, and senior-level profiles.
- Include different resume formats and layouts.
- Include candidates with strong, partial, and weak job-description alignment.
- Maintain a separate evaluation set where practical.

## 2. Improve Ground-Truth Validation

Continue comparing ATS decisions with independent manual recruiter reviews.

- Maintain manually reviewed test labels.
- Record reasons for manual decisions.
- Have another reviewer validate labels where possible.
- Identify false positives and false negatives.
- Re-evaluate cases where human and AI decisions differ.
- Avoid using the same examples to tune thresholds and report final evaluation metrics.

## 3. Role Adaptability Testing

Test the ATS against multiple job descriptions.

- Python Developer
- Data Analyst
- Software Engineer
- Non-technical roles

Verify that scoring changes appropriately according to the selected job description. Record results separately for each role type.

## 4. Bias and Fairness Testing

Continue testing whether job-irrelevant personal attributes influence candidate scoring.

The system should focus on job-relevant criteria:

- Skills
- Experience
- Education alignment
- Job relevance
- Semantic similarity

Test equivalent resumes with irrelevant personal details changed while keeping job-relevant qualifications constant. Investigate score differences and document limitations. Normalization and masking alone do not guarantee unbiased decisions.

## 5. Threshold Optimization

Evaluate the current shortlist and review thresholds using a larger, representative validation dataset.

Future testing should determine whether the thresholds produce:

- Excessive false positives
- Excessive false negatives
- Appropriate candidate coverage
- Consistent outcomes across role and experience groups

Document threshold changes and evaluate them on separate test cases before adopting them.

## 6. Resume Parsing Improvements

Improve handling of:

- Different PDF layouts
- DOCX resumes
- Tables
- Multiple-column resumes
- Missing sections
- Different skill naming conventions

Track extraction failures and verify whether parsing errors affect downstream scoring.

## 7. Semantic Matching Improvements

Improve matching between equivalent skills and technologies.

Examples:

- Python 3 → Python
- JS → JavaScript
- PowerBI → Power BI
- Postgres → PostgreSQL
- ReactJS → React

Test whether equivalent skill names produce consistent matching results without incorrectly treating unrelated skills as equivalent.

## 8. Monitoring and Logging

Continue recording:

- API requests
- Parsing errors
- Scoring errors
- Shortlisting errors
- Processing failures

Monitor failures and unexpected outputs during testing and future deployment. Avoid logging unnecessary personal information from resumes.

## Priority Order

1. Expand the test dataset to include non-technical and experienced candidates.
2. Validate manual labels and increase the number of positive examples.
3. Test role adaptability and investigate false positives and false negatives.
4. Evaluate fairness and threshold behavior.
5. Improve parsing, semantic matching, and operational monitoring.

## Current Status

The initial 10-candidate comparison completed successfully with zero mismatches. Broader validation remains pending because the current dataset does not cover the required range of roles and experience levels.
