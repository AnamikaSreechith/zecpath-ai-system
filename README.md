# Zecpath AI System

## 1. Project Overview

Zecpath is an AI-powered hiring platform designed to support the recruitment lifecycle, including resume screening, candidate screening, interview preparation, scoring, and hiring workflow automation.

This repository establishes a modular Python foundation for developing and integrating Zecpath AI components.

The current version contains sample implementations for demonstrating the architecture. It is not yet a production-ready hiring system.

## 2. Project Objectives

- Organize AI components into reusable Python modules.
- Establish a foundation for resume parsing and ATS scoring.
- Demonstrate initial candidate-screening functionality.
- Generate sample interview questions.
- Provide preliminary score-based recommendations.
- Implement centralized logging and automated testing.
- Follow consistent coding and documentation standards.

## 3. Project Structure

The project is organized into modular folders, with each folder responsible for a specific part of the Zecpath AI system.

zecpath-ai-system/
├── data/ # Dataset documentation and sample data
├── parsers/ # Resume parsing
├── ats_engine/ # ATS scoring and skill matching
├── screening_ai/ # Candidate screening
├── interview_ai/ # Interview question generation
├── scoring/ # Scoring and recommendations
├── utils/ # Shared utilities and logging
├── tests/ # Automated test cases
├── logs/ # Application log files
├── main.py # Application entry point
├── requirements.txt # Python dependencies
├── .gitignore # Files excluded from Git
└── README.md # Project documentation

Folder Responsibilities

    data/ — Stores dataset documentation and approved sample data.

    parsers/ — Handles resume-text parsing.

    ats_engine/ — Calculates resume skill-matching scores.

    screening_ai/ — Processes candidate screening responses.

    interview_ai/ — Generates sample interview questions.

    scoring/ — Produces preliminary score-based recommendations.

    utils/ — Contains shared utilities, including the logging system.

    tests/ — Contains automated tests for project components.

    logs/ — Stores application log files.                        |

## 4. Prerequisites

- Python 3.8 or a compatible version supported by the project's dependencies
- Git
- Visual Studio Code or another Python editor

## 5. Environment Setup

Create a virtual environment from the project root:

```powershell
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the required dependencies:

```powershell
python -m pip install -r requirements.txt
```

On Linux or macOS, activate the environment with:

```bash
source venv/bin/activate
```

## 6. Run the Application

From the project root, run:

```powershell
python main.py
```

The sample application demonstrates resume-text handling, ATS skill matching, screening keyword matching, interview question generation, and preliminary recommendations.

## 7. Run Automated Tests

Execute:

```powershell
python -m pytest -v
```

The tests check the behavior of the sample modules and validate selected error conditions.

## 8. Logging

The project uses Python's built-in logging module.

Log files are stored in:

```text
logs/zecpath.log
```

Logs are also displayed in the terminal. Avoid logging passwords, API keys, or unnecessary sensitive candidate information.

## 9. Coding Standards

- Follow PEP 8 Python coding conventions.
- Use descriptive names for variables and functions.
- Add docstrings to public functions.
- Keep each module focused on a specific responsibility.
- Validate inputs and raise meaningful exceptions.
- Add automated tests for new functionality.
- Update `requirements.txt` when dependencies change.
- Keep secrets in environment variables rather than source code.
- Use clear Git commit messages.
- Document significant changes to the project.

## 10. Current Limitations and Future Scope

The current version uses basic rule-based examples and predefined interview-question templates.

The following capabilities require further development:

- Direct PDF/DOCX resume extraction.
- Automatic extraction of skills and experience.
- LLM-based screening and adaptive interview questions.
- Voice calls, speech recognition, and video interview processing.
- Behavioral analysis and machine-test evaluation.
- Production-grade scoring, security, backend integration, and deployment.

The sample scoring and recommendation logic must not be treated as a complete or validated hiring decision system.

## 11. Project Status

**Day 3 – Environment and Repository Setup**

The repository provides an initial modular Python structure with sample components, centralized logging, automated tests, dependency instructions, and project documentation. Further AI functionality can be added incrementally.
