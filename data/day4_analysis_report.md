# Zecpath – Day 4 Hiring Data Analysis Report

## 1. Objective

The objective of this analysis is to study resume information across different professional domains, identify common hiring data patterns, and understand how technical and non-technical job requirements can be organized into structured data.

## 2. Resume Analysis

Ten sample resumes were considered across different professional domains.

### Domains Covered

- Software Engineering
- Web Development
- Marketing
- Cybersecurity
- Project Management
- Human Resources
- Data Analytics
- Machine Learning
- Finance and Accounting
- Artificial Intelligence

### Key Observations

**Skills:** Technical resumes contain skills related to programming, development, databases, cybersecurity, data analysis, and machine learning. Non-technical resumes emphasize communication, recruitment, marketing, project coordination, and finance-related skills.

**Experience:** Candidate profiles may include internships, entry-level experience, or previous professional roles. Experience should be represented using consistent job titles, company names, and dates.

**Designations:** Job titles vary across domains, including Software Engineer, Web Developer, Data Analyst, HR Recruiter, and Project Manager.

**Education:** Educational information can include degree, field of study, institution, graduation year, and grade.

**Certifications:** Certifications should be stored separately so they can be compared with job requirements when relevant.

## 3. Job Description Analysis

Two sample job descriptions were considered: Python Developer and HR Recruiter. These are illustrative examples used to design the data structure, not verified live vacancies.

### Technical Job Description – Python Developer

- **Required skills:** Python, SQL, REST APIs, and Git.
- **Preferred skills:** FastAPI, Docker, and AWS.
- **Education:** A bachelor's degree in Computer Science or a related field.
- **Experience:** One to three years in the sample description.
- **Responsibilities:** Software development and API-related work.

### Non-Technical Job Description – HR Recruiter

- **Required skills:** Candidate sourcing, resume screening, interview coordination, and communication.
- **Preferred skills:** LinkedIn Recruiter, ATS, and Excel.
- **Education:** A degree related to Human Resources or Business.
- **Experience:** Zero to two years in the sample description.
- **Responsibilities:** Recruitment coordination and candidate management.

## 4. Common Data Patterns Identified

1. Candidate skills and job skills should use a consistent structure.
2. Required skills should be distinguished from preferred skills.
3. Experience should include start and end dates, with ongoing employment represented consistently.
4. Education and certifications should be stored as separate records.
5. Job descriptions should include responsibilities, experience requirements, and education requirements.
6. Technical and non-technical roles require different skill categories.

## 5. Standardization Approach

The following structured data files were designed:

- `resume_schema.json` – defines the expected structure of resume data.
- `job_description_schema.json` – defines the expected structure of job description data.
- `resume1.json` to `resume10.json` – store the sample candidate profiles.
- `technical_jd.json` and `non_technical_jd.json` – store the sample job descriptions.
- `ai_data_entities.md` – describes the Candidate Profile, Job Profile, Skill Object, and Experience Object.

JSON Schema validation was used to check that the resume records follow the defined structure. The ten resume records passed validation according to the reported test output.

## 6. Conclusion

This task established a standardized foundation for organizing candidate and job information. The resulting data structures can support future development of resume analysis, skill comparison, and candidate-job matching components. Actual AI-based extraction and matching would require further implementation and testing.