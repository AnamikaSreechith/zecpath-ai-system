# Zecpath ATS — Technical Documentation

## 1. Overview

The Zecpath Applicant Tracking System (ATS) is a Python-based system designed to support resume processing, candidate-job matching, candidate scoring, ranking, and shortlisting.

The project contains modular components for resume parsing, skill extraction, experience and education analysis, semantic matching, scoring, and candidate ranking. A FastAPI application also exposes REST endpoints for interacting with selected ATS capabilities.

### Objectives

- Evaluate candidate profiles against job requirements.
- Calculate explainable ATS scores using weighted criteria.
- Compare candidate profiles using semantic similarity.
- Rank candidates and assign recruitment statuses.
- Provide API endpoints for scoring, ranking, and resume-related operations.
- Keep components modular so developers can maintain and extend the system.

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core implementation |
| FastAPI | REST API |
| Pydantic | API request and response schemas |
| Sentence Transformers | Semantic text embeddings |
| `all-MiniLM-L6-v2` | Semantic embedding model |
| scikit-learn | Cosine similarity |
| `functools.lru_cache` | Embedding-result caching |
| pytest | Automated testing |
| JSON | Resume, job-description, and result storage |

The current `requirements.txt` lists `pytest==7.4.4` and `python-dotenv==1.0.1`. These are not the complete runtime dependency list for the project. Dependencies imported by other modules must also be installed in the development environment.

## 3. Project Structure

```text
zecpath-ai-system/
├── api/
│   ├── main.py
│   ├── services.py
│   ├── schemas.py
│   └── logger.py
├── ats_engine/
│   ├── ats_scorer.py
│   └── data/
├── data/
│   ├── resumes/
│   ├── job_descriptions/
│   └── schemas/
├── matching/
│   ├── ats_scoring_engine.py
│   ├── candidate_ranking_engine.py
│   ├── candidate_ranking_pipeline.py
│   ├── fairness_normalization.py
│   └── semantic_matching_engine.py
├── parsers/
│   ├── resume_parser.py
│   ├── job_description_parser.py
│   ├── skill_extraction_engine.py
│   ├── experience_parser.py
│   ├── education_parser.py
│   └── resume_section_classifier.py
├── scoring/
│   ├── decision_engine.py
│   └── experience_relevance.py
├── screening_ai/
│   └── screening_service.py
├── interview_ai/
│   └── question_generator.py
├── tests/
├── utils/
├── logs/
├── docs/
└── requirements.txt
```

This structure describes the main project modules. Individual files may contain additional functionality not listed here.

## 4. Core Components

### 4.1 Resume Parsing

The `parsers/` package contains modules responsible for extracting and interpreting resume information.

Relevant modules include:

- `resume_parser.py`: resume text extraction and processing.
- `skill_extraction_engine.py`: skill extraction.
- `experience_parser.py`: experience-related information.
- `education_parser.py`: education information.
- `resume_section_classifier.py`: resume section classification.
- `job_description_parser.py`: job-description processing.

The resume parser includes error-handling tests for empty and corrupted PDF and DOCX files.

### 4.2 Semantic Matching Engine

File: `matching/semantic_matching_engine.py`

The semantic matching engine compares resume content with job-description content using sentence embeddings and cosine similarity.

The embedding model is:

`all-MiniLM-L6-v2`

The embedding function uses an LRU cache with a maximum size of 512 entries:

```python
@lru_cache(maxsize=512)
def generate_embedding(text):
    if not text or not text.strip():
        return None

    return model.encode(
        text,
        convert_to_numpy=True
    )
```

Caching allows repeated requests for identical text to reuse previously generated embeddings while the corresponding entries remain in the cache.

#### Semantic score weights

| Component | Weight |
|---|---:|
| Skills similarity | 40% |
| Experience similarity | 35% |
| Projects similarity | 25% |

The overall semantic similarity is calculated as:

```python
overall_score = (
    skills_score * 0.40
    + experience_score * 0.35
    + projects_score * 0.25
)
```

The semantic match classification is:

| Similarity score | Classification |
|---|---|
| 0.80 or above | Strong Match |
| 0.60 to below 0.80 | Moderate Match |
| Below 0.60 | Low Match |

These classifications describe semantic similarity only. They are different from the final ATS match classifications.

### 4.3 ATS Scoring Engine

File: `matching/ats_scoring_engine.py`

The ATS scoring engine combines four component scores into one final score.

#### Default weights

| Scoring component | Weight |
|---|---:|
| Skill match | 30% |
| Experience relevance | 25% |
| Education alignment | 20% |
| Semantic similarity | 25% |
| **Total** | **100%** |

The calculation is:

```python
final_score = (
    skill_match * 0.30
    + experience_relevance * 0.25
    + education_alignment * 0.20
    + semantic_similarity * 0.25
) * 100
```

Each component is expected to be a normalized value between 0 and 1. The engine validates the weight configuration and normalizes invalid or missing component scores to 0.0. Valid numeric component scores are clamped to the interval [0, 1].

The final score is rounded to two decimal places.

#### Example

Suppose a candidate receives the following component scores:

- Skill match: 0.90
- Experience relevance: 0.80
- Education alignment: 0.70
- Semantic similarity: 0.85

The final score is:

```text
(0.90 × 0.30
 + 0.80 × 0.25
 + 0.70 × 0.20
 + 0.85 × 0.25) × 100

= 82.75
```

The result is classified as an Excellent Match.

#### Final ATS match classifications

| Final score | Match level |
|---|---|
| 80 or above | Excellent Match |
| 65 to below 80 | Good Match |
| 50 to below 65 | Moderate Match |
| Below 50 | Low Match |

The scoring result contains the final score, match level, score breakdown, and weights.

### 4.4 Candidate Ranking and Shortlisting

File: `matching/candidate_ranking_engine.py`

The ranking engine validates candidate records, orders candidates by score, assigns ranks, and determines recruitment statuses.

#### Recruitment thresholds

| Score | Recruitment status |
|---|---|
| 80 or above | Shortlisted |
| 50 to below 80 | Review |
| Below 50 | Rejected |

These are recruitment statuses, not the same as the ATS match classifications.

The `rank_candidates()` function sorts candidates in descending order of score. The `shortlist_candidates()` function adds the recruitment status to each ranked candidate.

The `get_top_candidates()` helper selects up to a specified number of candidates, using `heapq.nlargest`.

### 4.5 Candidate Ranking Pipeline

File: `matching/candidate_ranking_pipeline.py`

The ranking pipeline connects resume data, job-description data, component scoring, semantic similarity, and candidate ranking.

Default inputs and outputs:

| Purpose | Path |
|---|---|
| Resume directory | `data/resumes/` |
| Job description | `data/job_descriptions/parsed_jds/python_developer.json` |
| Candidate scores | `data/candidate_scores.json` |
| Ranked candidates | `data/ranked_candidates.json` |

The pipeline loads resume JSON files, loads the selected job description, calculates component scores, generates candidate scores, saves the score records, ranks the candidates, and saves the ranked output.

#### Current scoring heuristics

The current implementation uses the following approximations:

- **Skill match:** required and preferred skills are compared separately. When both groups are present, required skills contribute 70% and preferred skills contribute 30%.
- **Experience relevance:** estimates experience using the number of experience entries multiplied by 0.5. This is a heuristic, not a calculation from actual employment dates.
- **Education alignment:** checks the implemented degree and field-matching conditions. It is not a comprehensive qualification-equivalency engine.
- **Semantic similarity:** compares resume skills, experience text, and project text with text derived from the job description.

The experience and education rules should be reviewed before using the scores for high-impact recruitment decisions.

## 5. API Architecture

The FastAPI application is defined in `api/main.py`.

Application title: `Zecpath ATS AI API`

Version: `1.0.0`

The API service functions in `api/services.py` delegate ATS scoring to `matching.ats_scoring_engine` and candidate ranking to `matching.candidate_ranking_engine`.

### API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Health check |
| POST | `/resume/upload` | Validate and save a resume file |
| POST | `/resume/process` | Save a resume and queue a background job |
| GET | `/resume/process/{job_id}` | Retrieve background job status |
| POST | `/resume/parse` | Validate supplied text and return it as parsed text |
| POST | `/candidate/score` | Calculate an ATS score from supplied component scores |
| POST | `/candidate/shortlist` | Rank candidates and assign recruitment statuses |

### Resume upload

The upload endpoint accepts PDF, DOCX, and TXT extensions, rejects empty filenames and empty files, and saves the file under `data/uploads/`.

It also sanitizes the filename using `Path(filename).name`.

### Background processing

The `/resume/process` endpoint creates a job ID, saves the uploaded file, and schedules a FastAPI background task.

**Important limitation:** the current `process_resume_job()` function records job status and a placeholder result. Its comments identify resume extraction, normalization, matching, scoring, ranking, and shortlisting as future integration steps. Therefore, this endpoint should not be documented as a completed end-to-end resume-processing workflow.

Job state is stored in an in-memory dictionary. Job records are not persistent across application restarts.

### Resume parsing endpoint

The `/resume/parse` endpoint validates non-empty text and returns that text with a parsed status. Its current implementation does not invoke the PDF/DOCX extraction engine.

### API service layer

File: `api/services.py`

The service layer provides two functions:

- `calculate_ats_score()`: delegates to `generate_candidate_score()`.
- `rank_and_shortlist()`: delegates to `shortlist_candidates()`.

This separation keeps the API routes distinct from the scoring and ranking implementation.

## 6. Data Storage

The project uses JSON files for resume records, job descriptions, scoring results, and ranking results.

The ranking pipeline writes:

- `data/candidate_scores.json`
- `data/ranked_candidates.json`

These files are generated by running the ranking pipeline. They should not be assumed to exist before the pipeline has been executed.

Uploaded files are stored under `data/uploads/`. The API's background-job state is held in memory rather than in a database.

## 7. Logging and Error Handling

The API uses the logger defined in `api/logger.py`.

The application records events such as health-check requests, resume uploads, job creation, scoring requests, and ranking operations. Several API operations catch exceptions, log them, and return HTTP error responses.

The resume parser also has tests covering empty and corrupted document inputs.

For production deployment, review error-message exposure, log retention, uploaded-file access, and input validation.

## 8. Testing and Verification

The repository contains automated tests for scoring, candidate ranking, parsing, education and experience relevance, skill extraction, decision logic, logging, and other modules.

Run the test suite from the repository root:

```powershell
python -m pytest -q
```

A previous Day 18 run reported 97 passing tests. This is a historical result, not a guarantee that every future code change will pass.

After changing scoring rules, ranking behavior, parsing logic, or API schemas, rerun the relevant tests and then the full suite.

## 9. Troubleshooting Notes

### Import errors

**Symptoms:** `ModuleNotFoundError` or failed imports.

**Checks:**
1. Confirm the terminal is in the repository root.
2. Confirm the intended Python environment is active.
3. Install the project's required runtime dependencies.
4. Verify that imports use the expected package paths.

### Semantic model loading problems

**Symptoms:** errors when initializing `SentenceTransformer` or generating embeddings.

**Checks:**
1. Verify that the relevant Python packages are installed.
2. Check model availability and network access if the model must be downloaded.
3. Confirm the Python environment is the same one used to install the dependencies.

### Missing input JSON

**Symptoms:** `FileNotFoundError` while running the ranking pipeline.

**Checks:**
1. Run the command from the repository root.
2. Verify that the resume directory contains JSON files.
3. Verify that the configured parsed job-description file exists.
4. Confirm the input paths match the current project structure.

### Invalid scoring weights

**Symptoms:** weight validation raises an exception.

**Checks:**
1. Use exactly the four expected component keys.
2. Keep every weight between 0 and 1.
3. Ensure the weights sum to 1.0.

### Invalid candidate records

**Symptoms:** ranking fails during candidate validation.

**Checks:**
1. Confirm every candidate is a dictionary.
2. Include a valid `candidate_id`.
3. Include a numeric score between 0 and 100.

### Resume parsing errors

**Symptoms:** PDF or DOCX extraction fails.

**Checks:**
1. Confirm the file is not empty or corrupted.
2. Verify the appropriate parsing dependency is installed.
3. Inspect parser logs and error-handling tests.

### API background job not found

**Symptoms:** `/resume/process/{job_id}` returns HTTP 404.

**Checks:**
1. Confirm that the job ID came from a successful `/resume/process` response.
2. Confirm the API process has not restarted since the job was created.
3. Remember that job records are stored in memory.

## 10. Known Limitations

The current implementation has several limitations that should be considered during maintenance and extension:

1. Experience relevance is based on the number of experience entries, not verified employment durations.
2. Education alignment uses simplified degree and field checks.
3. The background resume-processing function is a placeholder rather than a complete pipeline integration.
4. The API parsing endpoint accepts text rather than extracting text directly from uploaded documents.
5. Background job state is in memory and is not durable.
6. The API upload endpoints save files using a sanitized filename, but repeated uploads with the same filename can overwrite an existing file.
7. The current requirements file does not enumerate every runtime dependency imported across the repository.
8. ATS scores and shortlisting statuses are decision-support outputs and should be reviewed alongside human judgment and appropriate fairness checks.

## 11. Extension Guidelines

When extending the ATS:

- Keep parsing, matching, scoring, ranking, and API responsibilities separated.
- Update the relevant tests whenever scoring or ranking rules change.
- Document changes to score weights and classification thresholds.
- Validate input data before calculating scores.
- Preserve the distinction between semantic similarity, final ATS match level, and recruitment status.
- Avoid describing placeholder functionality as fully integrated.
- Review privacy, security, and fairness before using the system with real candidate data.

## 12. Summary

The Zecpath ATS combines modular resume-processing components, semantic similarity, weighted candidate scoring, candidate ranking, and a FastAPI interface.

The scoring and ranking engines provide defined formulas and thresholds, while the API exposes selected capabilities. Some API processing steps and several scoring heuristics remain limited and should be improved before production use.

This document describes the implementation reviewed for the Day 19 documentation work. Update it whenever the code, configuration, or system architecture changes.
