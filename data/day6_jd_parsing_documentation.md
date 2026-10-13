# Day 6 – Job Description Parsing System

## 1. Objective

The objective of Day 6 was to develop a job description parser that converts raw job descriptions into structured, AI-readable data. The system extracts job roles, required skills, preferred skills, experience requirements, and education details.

## 2. Implementation

A Python module named `job_description_parser.py` was created inside the `parsers` folder.

The parser performs the following operations:

- **Text normalization:** Removes unnecessary spaces and extra blank lines.
- **Role detection:** Identifies job roles using predefined role names and synonyms.
- **Skill extraction:** Extracts required and preferred skills separately.
- **Experience extraction:** Identifies minimum and maximum years of experience.
- **Education extraction:** Identifies education levels and relevant fields.
- **JSON generation:** Saves the extracted information as a structured JSON file.

## 3. Synonym Mapping

Predefined dictionaries were used to recognize different names for the same role or skill.

Examples:

- Python Programmer → Python Developer
- Python Software Developer → Python Developer
- Talent Acquisition Specialist → HR Recruiter
- Amazon Web Services → AWS
- MS Excel → Microsoft Excel

This helps standardize job descriptions that use different terms for similar skills or roles.

## 4. Input and Output Files

The following raw job descriptions were used for testing:

- `data/job_descriptions/python_developer_raw.txt`
- `data/job_descriptions/hr_recruiter_raw.txt`

The parser generated these structured outputs:

- `data/job_descriptions/parsed_jds/python_developer.json`
- `data/job_descriptions/parsed_jds/hr_recruiter.json`

The output contains the job ID, job title, required skills, preferred skills, experience requirements, education requirements, normalized text, and processing status.

## 5. Testing

Automated tests were created in `tests/test_job_description_parser.py`.

The tests cover text normalization, empty input handling, role detection, skill extraction, experience extraction, education extraction, structured output generation, and JSON file saving.

The complete project test suite was executed using:

`python -m pytest -v`

**Result: 29 tests passed.**

## 6. Limitations

The current implementation uses rule-based extraction and predefined dictionaries. It may not recognize every job title, skill synonym, education requirement, or experience format. More advanced NLP or AI-based methods could improve its accuracy.

## 7. Conclusion

The Day 6 task established a basic job description parsing system that converts raw job descriptions into structured JSON profiles. These profiles can be used as input for later stages of the recruitment pipeline, including resume screening and candidate matching.