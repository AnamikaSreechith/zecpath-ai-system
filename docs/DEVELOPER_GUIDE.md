
# Zecpath ATS — Developer Guide

## 1. Introduction

This guide explains how to set up, run, test, and extend the Zecpath Applicant Tracking System (ATS).

The project includes resume-processing modules, semantic matching, weighted ATS scoring, candidate ranking, and a FastAPI application.

## 2. Prerequisites

Before starting development, ensure that you have:

- Python 3.10+ installed.
- Git installed.
- Visual Studio Code or another Python-compatible editor.
- Access to the Zecpath ATS repository.

## 3. Project Setup

### Step 1: Open the Repository

Open PowerShell and navigate to the project directory.

```powershell
cd C:\Users\HP\Documents\zecpath\zecpath-ai-system
```

### Step 2: Create and Activate Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. Running the ATS Ranking Pipeline

The main candidate-ranking pipeline is located at:

`matching/candidate_ranking_pipeline.py`

Run the pipeline from the repository root:

```powershell
python -m matching.candidate_ranking_pipeline
```

### Generated Output Files

- `data/candidate_scores.json` — Candidate scoring results.
- `data/ranked_candidates.json` — Ranked candidates with recruitment statuses.

## 5. Running the FastAPI Application

The main application file is:

`api/main.py`

Start the development server:

```powershell
python -m uvicorn api.main:app --reload
```

### API Documentation

- API Base: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## 6. API Endpoints

| Method | Endpoint                   | Purpose 

| GET    | `/` | Health check         |
| POST   | `/resume/upload`           | Validate and save a resume 
| POST   | `/resume/process`          | Create a background-processing job 
| POST   | `/resume/parse`            | Validate supplied text and return parsed text 
| POST   | `/candidate/score`         | Calculate an individual candidate's ATS score 
| POST   | `/candidate/shortlist`     | Rank and classify candidate records 

## 7. Understanding the Scoring Logic

### 7.1 ATS Scoring

File: `matching/ats_scoring_engine.py`

```text
Final Score =
(
    Skill Match × 0.30
  + Experience Relevance × 0.25
  + Education Alignment × 0.20
  + Semantic Similarity × 0.25
) × 100
```

### 7.2 Recruitment Status Classification

- **Shortlisted:** Score >= 80
- **Review:** Score >= 50 and < 80
- **Rejected:** Score < 50

### 7.3 Candidate Match Levels

- **Excellent Match:** Score >= 80
- **Good Match:** Score >= 65 and < 80
- **Moderate Match:** Score >= 50 and < 65
- **Low Match:** Score < 50

## 8. Running Automated Tests and Benchmarks

### 8.1 Run the Complete Test Suite

Execute all available automated tests:

```powershell
python -m pytest -q
```

### 8.2 Day 17 — Multi-Job Ground Truth Testing

Run the 50-pair resume-to-job-description testing matrix:

```powershell
python data/testing/day17_testing.py
```

This test evaluates:

- Resume-to-job-description matching.
- Job-specific candidate evaluation.
- Matching accuracy against expected results.
- Candidate ranking and scoring consistency.

### 8.3 Day 18 — Production Performance Benchmarks

#### Actual Resume Performance Benchmark

```powershell
python data/testing/day18_actual_resume_benchmark.py
```

Evaluates latency and throughput using 10 PDF resumes.

#### Noisy Resume Handling Test

```powershell
python data/testing/day18_noisy_resume_test.py
```

Evaluates how the system handles noisy and unformatted resumes.

#### Candidate Ranking Benchmark

```powershell
python data/testing/day18_ranking_benchmark.py
```

Evaluates candidate ranking and sorting performance.

## 9. Development Guidelines

- Maintain the existing modular project architecture.
- Keep resume parsing, matching, scoring, and ranking responsibilities separate.
- Validate input data before processing.
- Implement appropriate exception handling.
- Maintain consistent JSON response structures.
- Use logging to monitor application execution and errors.
- Write automated tests for newly implemented features.
- Avoid modifying existing modules without checking their dependencies.
- Maintain Git version control and commit changes regularly.


## 10. Conclusion

The Zecpath ATS Developer Guide provides the essential instructions for setting up the development environment, executing the candidate-ranking pipeline, running the FastAPI application, understanding the ATS scoring mechanism, and performing automated tests and performance benchmarks.

Following these guidelines helps developers maintain, test, and extend the Zecpath ATS system while ensuring consistency, reliability, and maintainability throughout development.
