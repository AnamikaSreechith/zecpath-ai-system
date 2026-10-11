# Zecpath AI Data Entity Design

## 1. Introduction

The purpose of this document is to define standardized data entities for the Zecpath AI hiring system. These entities organize resume and job description information into structured formats that can be processed consistently by software systems and used by future AI-based recruitment components.

## 2. Candidate Profile

The Candidate Profile stores information extracted or entered from a candidate's resume.

**Fields:**
- `candidate_id`: Unique identifier for the candidate.
- `designation`: Current or target professional designation.
- `professional_summary`: Brief description of the candidate's profile.
- `skills`: List of candidate skills.
- `experience`: List of previous or current work experiences.
- `education`: List of educational qualifications.
- `certifications`: List of professional certifications.

**Purpose:** To maintain candidate information in a consistent format for resume analysis and future candidate-job matching.

## 3. Job Profile

The Job Profile stores the requirements and responsibilities associated with a job opening.

**Fields:**
- `job_id`: Unique identifier for the job.
- `job_title`: Designation of the position.
- `department`: Department offering the position.
- `job_type`: Technical or Non-Technical.
- `experience_required`: Minimum and maximum required years of experience.
- `education_requirements`: Required educational qualifications.
- `required_skills`: Essential skills for the position.
- `preferred_skills`: Additional desirable skills.
- `responsibilities`: List of job responsibilities.
- `certifications`: Relevant certifications, if applicable.

**Purpose:** To represent job requirements in a standardized format for comparing candidates against job criteria.

## 4. Skill Object

The Skill Object represents an individual skill associated with a candidate or job.

**Fields:**
- `name`: Name of the skill, such as Python, SQL, Communication, or Recruitment.
- `category`: Classification of the skill, such as Programming, Database, or Soft Skill.

**Purpose:** To categorize skills consistently and support skill comparison between candidate profiles and job profiles.

## 5. Experience Object

The Experience Object represents one work experience entry.

**Fields:**
- `designation`: Job title held by the candidate.
- `company`: Organization where the candidate worked.
- `start_date`: Employment start date in YYYY-MM format.
- `end_date`: Employment end date in YYYY-MM format, or `null` if the role is ongoing.

**Purpose:** To organize employment history consistently and support future experience-based matching.

## 6. Relationships Between Entities

- A Candidate Profile contains multiple Skill Objects.
- A Candidate Profile can contain multiple Experience Objects.
- A Candidate Profile can contain multiple education records and certifications.
- A Job Profile contains required and preferred Skill Objects.
- Candidate skills and job skills can be compared to identify matching and missing skills.

## 7. Conclusion

These four core entities establish a foundation for structured hiring data in Zecpath. Standardizing candidate profiles, job profiles, skills, and experience makes the data easier to validate, maintain, compare, and prepare for future AI integration.

