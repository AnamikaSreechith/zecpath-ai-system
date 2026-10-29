# Zecpath ATS — Developer Guide

## 1. Introduction

This guide explains how to set up, run, test, and extend the Zecpath Applicant Tracking System (ATS).

The project includes resume-processing modules, semantic matching, weighted ATS scoring, candidate ranking, and a FastAPI application.

This guide distinguishes the existing implementation from functionality that still requires integration.

## 2. Prerequisites

Before starting development, ensure that you have:

- Python installed.
- Git installed.
- Visual Studio Code or another Python-compatible editor.
- Access to the Zecpath ATS repository.
- Internet access if required packages or the sentence-transformer model need to be downloaded.

Use the Python environment compatible with the dependencies installed for your project.

## 3. Project Setup

### Step 1: Open the repository

Open the project folder in VS Code.

The repository root should contain directories such as `api/`, `matching/`, `parsers/`, `data/`, and `tests/`, along with `requirements.txt`.

### Step 2: Open the terminal

In VS Code, select **Terminal → New Terminal**.

Navigate to the project root if necessary:

```powershell
cd C:\Users\HP\Documents\zecpath\zecpath-ai-system
```

### Step 3: Create a virtual environment

If you do not already have an appropriate environment:

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use an approved environment activation method or activate the environment from the VS Code Python interpreter selector.

### Step 4: Install the listed requirements

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Dependency note:** The current `requirements.txt` lists `pytest==7.4.4` and `python-dotenv==1.0.1` only. Other modules import packages such as FastAPI, Sentence Transformers, and scikit-learn. Install the additional runtime dependencies required by the modules you intend to run. The current requirements file should be reviewed and completed before using it as the sole environment setup source.

### Step 5: Verify the Python environment

```powershell
python --version
python -m pip list
```

Confirm that the interpreter and required packages belong to the intended environment.

## 4. Running the ATS Ranking Pipeline

The main candidate-ranking pipeline is located at:

`matching/candidate_ranking_pipeline.py`

From the repository root, run:

```powershell
python -m matching.candidate_ranking_pipeline
```

The default pipeline uses:

- Resume directory: `data/resumes/`
- Job description: `data/job_descriptions/parsed_jds/python_developer.json`

The pipeline reads resume JSON files, loads the job description, calculates component scores, generates final ATS scores, ranks candidates, and writes output files.

### Generated files

| File | Purpose |
|---|---|
| `data/candidate_scores.json` | Candidate scoring results |
| `data/ranked_candidates.json` | Ranked candidates with recruitment statuses |

The pipeline may overwrite these output files when run again. Back up any results that need to be retained.

### Changing the job description

To use another job description, update the `JD_FILE` configuration in `matching/candidate_ranking_pipeline.py` or use the function parameters when calling `run_ranking_pipeline()` programmatically.

Confirm that the selected JSON file follows the structure expected by the pipeline.

## 5. Running the FastAPI Application

The API application is defined in `api/main.py`.

After installing the required API dependencies, start the development server from the repository root:

```powershell
python -m uvicorn api.main:app --reload
```

If Uvicorn is not installed, install it in the active Python environment before running this command.

### Access the API

When the server starts successfully, the default local address is:

`http://127.0.0.1:8000`

FastAPI's interactive documentation is normally available at:

`http://127.0.0.1:8000/docs`

### Health check

Open the root endpoint:

`http://127.0.0.1:8000/`

The expected response is similar to:

```json
{
  "message": "Zecpath ATS AI API is running",
  "status": "healthy"
}
```

This checks that the API is responding. It does not verify that every ATS component or dependency is working correctly.

## 6. API Endpoints

The current API exposes the following endpoints.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Health check |
| POST | `/resume/upload` | Validate and save a resume |
| POST | `/resume/process` | Create a background-processing job |
| GET | `/resume/process/{job_id}` | Retrieve job status |
| POST | `/resume/parse` | Validate and return supplied resume text |
| POST | `/candidate/score` | Calculate a candidate's ATS score |
| POST | `/candidate/shortlist` | Rank and classify candidate records |

Use `/docs` to inspect the request schemas and try supported API operations.

### Important API limitations

- `/resume/parse` currently accepts text and returns it as parsed text. It does not call the document extraction engine.
- `/resume/process` schedules a background function that currently returns a placeholder result rather than performing the complete ATS workflow.
- Job records are stored in memory and are lost when the application restarts.
- The upload endpoint saves files under `data/uploads/`. Uploading another file with the same sanitized filename may overwrite the earlier file.

Do not treat these endpoints as a complete production resume-processing workflow.

## 7. Understanding the Scoring Logic

### 7.1 ATS scoring

File: `matching/ats_scoring_engine.py`

The final ATS score combines four normalized component scores:

| Component | Weight |
|---|---:|
| Skill match | 30% |
| Experience relevance | 25% |
| Education alignment | 20% |
| Semantic similarity | 25% |

Formula:

```text
Final Score =
(
    Skill Match × 0.30
  + Experience Relevance × 0.25
  + Education Alignment × 0.20
  + Semantic Similarity × 0.25
) × 100
```

The weights must contain exactly the four expected keys, each between 0 and 1, and sum to 1.0.

### 7.2 Match classifications

| Score | Match level |
|---|---|
| 80 or above | Excellent Match |
| 65 to below 80 | Good Match |
| 50 to below 65 | Moderate Match |
| Below 50 | Low Match |

### 7.3 Recruitment statuses

File: `matching/candidate_ranking_engine.py`

| Score | Status |
|---|---|
| 80 or above | Shortlisted |
| 50 to below 80 | Review |
| Below 50 | Rejected |

The match classification and recruitment status are separate outputs. A candidate scoring 70 is a Good Match and receives the status Review.

### 7.4 Semantic matching

File: `matching/semantic_matching_engine.py`

The semantic engine uses the `all-MiniLM-L6-v2` model and cosine similarity.

| Component | Semantic weight |
|---|---:|
| Skills similarity | 40% |
| Experience similarity | 35% |
| Projects similarity | 25% |

Embedding generation is cached using `lru_cache(maxsize=512)`.

### 7.5 Important scoring limitations

The current ranking pipeline approximates experience years using the number of experience entries multiplied by 0.5. It does not calculate actual employment durations.

Education alignment also uses simplified degree and field checks. These heuristics should be evaluated before making consequential hiring decisions.

## 8. Running Automated Tests

Run the full test suite from the repository root:

```powershell
python -m pytest -q
```

To run a specific test module:

```powershell
python -m pytest tests/test_ats_scoring_engine.py -v
```

For ranking tests:

```powershell
python -m pytest tests/test_candidate_ranking_engine.py -v
```

For resume parser tests:

```powershell
python -m pytest tests/test_resume_parser.py -v
```

### Interpreting the results

- `PASSED`: the test succeeded.
- `FAILED`: an assertion or expected behavior did not match.
- `ERROR`: test setup or execution encountered an error.
- `SKIPPED`: the test was not executed.

After modifying a module, run its relevant tests first, followed by the full test suite.

A previous Day 18 test run reported 97 passing tests. Always use the current test output to verify the current code.

## 9. Extending the System

### Adding a scoring component

Before adding a new component:

1. Define how its input data will be obtained.
2. Normalize its output to the expected range of 0 to 1.
3. Decide its contribution to the final score.
4. Update the weight configuration and validation rules.
5. Update score-generation and API schemas where necessary.
6. Add tests for valid, missing, and invalid inputs.
7. Update the technical documentation.

Ensure that the weights continue to sum to 1.0.

### Changing ranking thresholds

The ranking thresholds are defined in `matching/candidate_ranking_engine.py`.

When changing them:

1. Update the relevant threshold constants.
2. Check the status-classification function.
3. Add boundary tests around the new thresholds.
4. Update documentation and API expectations.

Do not change recruitment statuses unintentionally when modifying match classifications.

### Extending resume parsing

The relevant modules are under `parsers/`.

When extending a parser:

1. Inspect the existing input and output structures.
2. Preserve compatibility with the resume JSON schema.
3. Handle empty and malformed input.
4. Add tests for successful extraction and failure cases.
5. Verify downstream modules that consume the parsed fields.

### Integrating background processing

The background-processing function in `api/main.py` is a current integration point.

A future implementation should connect the saved resume to the appropriate extraction, normalization, matching, scoring, and ranking components. It should also handle failures and result persistence.

Do not mark this integration complete until the function actually performs those steps and the behavior is covered by tests.

## 10. Troubleshooting

### `ModuleNotFoundError`

**Possible causes:** Missing dependency, wrong Python interpreter, or running the command outside the repository root.

**Resolution:**

```powershell
python -c "import sys; print(sys.executable)"
python -m pip list
```

Confirm the active interpreter and install the missing package in that environment.

### `FileNotFoundError`

**Possible causes:** Missing resume JSON, incorrect job-description path, or an unexpected working directory.

**Resolution:**

- Confirm that the terminal is in the repository root.
- Verify the input file exists.
- Check the configured paths in `matching/candidate_ranking_pipeline.py`.

### Sentence-transformer model errors

**Possible causes:** Missing dependencies, unavailable model files, or network restrictions during the initial download.

**Resolution:**

- Verify that Sentence Transformers and its dependencies are installed.
- Check network access if the model needs to be downloaded.
- Confirm the active environment is the intended one.

### Weight validation errors

**Possible causes:** Incorrect component keys, out-of-range weights, or weights that do not sum to 1.0.

**Resolution:** Check `DEFAULT_WEIGHTS` in `matching/ats_scoring_engine.py` and the `validate_weights()` function.

### Candidate validation errors

**Possible causes:** Missing candidate IDs, missing scores, non-numeric scores, or scores outside the permitted range.

**Resolution:** Inspect the candidate records before passing them to the ranking engine.

### API server errors

**Possible causes:** Missing FastAPI dependencies, invalid request data, or an exception in the service layer.

**Resolution:**

1. Read the terminal traceback.
2. Inspect the request schema in `api/schemas.py`.
3. Check the service functions in `api/services.py`.
4. Run the relevant automated tests.

### Background job returns a placeholder result

This is the current implementation of `process_resume_job()`, not necessarily a runtime failure. The complete resume-processing workflow has not yet been connected to that function.

## 11. Development Best Practices

- Run commands from the repository root unless a command requires another directory.
- Use the active virtual environment consistently.
- Keep parsing, scoring, ranking, and API responsibilities separated.
- Add tests whenever behavior changes.
- Avoid changing scoring weights without updating documentation.
- Keep generated outputs separate from source code.
- Do not commit real candidate personal information or credentials.
- Review uploaded-file handling, access controls, and privacy before production deployment.
- Document known limitations honestly.
- Verify test results before committing changes.

## 12. Day 19 Documentation Checklist

- [ ] ATS technical documentation created.
- [ ] Architecture diagrams documented.
- [ ] Developer guide created.
- [ ] Scoring logic and ranking thresholds documented.
- [ ] API endpoints documented.
- [ ] Troubleshooting notes included.
- [ ] Current implementation limitations identified.

## 13. Summary

This guide provides the basic development workflow for the Zecpath ATS repository. Developers can use it to set up the environment, execute the ranking pipeline, start the API, run tests, understand scoring rules, and extend the existing modules.

The code remains the source of truth. When implementation details change, update the developer guide, technical documentation, architecture diagrams, and relevant tests together.
