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

| Technology            |       Purpose 

| Python 3.10+          | Core implementation                              
| FastAPI               | REST API framework  
| Pydantic              | API request and response schemas 
| Sentence Transformers | Semantic text embeddings 
| `all-MiniLM-L6-v2`    | Pretrained semantic embedding model 
| scikit-learn          | Cosine similarity calculation 
| `functools.lru_cache` | Embedding-result caching 
| PyPDF / python-docx   | Text extraction from PDF and DOCX files 
| pytest                | Automated testing 
| JSON / SQLite3        | Storage for profiles, job descriptions, and evaluation outputs 

The current `requirements.txt` lists base testing dependencies. Dependencies imported by other modules (FastAPI, Uvicorn, Sentence Transformers, scikit-learn) must also be installed in the active development environment.

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
│   ├── testing/
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