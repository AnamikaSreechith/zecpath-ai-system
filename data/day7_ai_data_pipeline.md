# Day 7 – AI Data Pipeline & Storage Design

## 1. Objective

The objective of Day 7 is to design how data flows, connects, and evolves across the Zecpath AI recruitment platform.

The design covers data collection, storage, parsing, screening, interview analysis, decision support, metadata management, and dataset versioning.

The purpose is to maintain structured, traceable, and consistent data throughout the recruitment lifecycle.

## 2. AI Data Pipeline

The proposed pipeline consists of the following stages:

1. **Data Upload:** Candidates submit resumes, and recruiters provide job descriptions.
2. **Validation:** Check file types, file sizes, required fields, and input validity.
3. **Raw Data Storage:** Preserve original resumes and job descriptions.
4. **Data Parsing:** Extract relevant information using resume and job-description parsers.
5. **Structured Profile Storage:** Save parsed candidate profiles and job requirement profiles in JSON format.
6. **ATS Scoring:** Compare candidate information with job requirements and calculate matching scores.
7. **AI Screening:** Generate screening results and reports based on available candidate and job data.
8. **Interview Processing:** Store interview questions, responses, evaluation results, and related metadata.
9. **Decision Support:** Combine relevant results to support a hiring decision.
10. **Audit and Feedback:** Record processing history, model versions, corrections, and authorized hiring outcomes.

## 3. Data Flow

Raw data is collected first and preserved separately from processed data.

The parsers convert raw resumes and job descriptions into structured profiles. These profiles are used by the ATS and screening modules. Their outputs, along with interview results, can then be used by the decision-support module.

Each stage should retain references to the candidate, job, processing time, and applicable model or rule version.

## 4. Storage Design

The initial design uses JSON for structured records and files for original documents.

- **Resumes:** Original PDF or DOCX files, with access controls.
- **Parsed Profiles:** JSON records containing extracted skills, education, experience, and other supported fields.
- **ATS Scores:** JSON records containing candidate-job matching scores and scoring metadata.
- **Screening Reports:** JSON records containing screening findings, matched skills, missing skills, and processing status.
- **Interview Results:** JSON records containing interview evaluations, scores, feedback, and timestamps.
- **Hiring Decisions:** Structured records containing the final decision, decision-maker, date, and references to supporting assessments.

A database can be introduced later if the platform requires more advanced querying, concurrency, access control, and reporting.

## 5. Metadata Management

Each relevant record should include consistent metadata:

- Candidate ID
- Job ID
- Record ID
- Created timestamp
- Updated timestamp
- Processing status
- Parser or model version, where applicable
- Schema version

Candidate IDs identify candidates, while job IDs identify job openings. Model versions identify the implementation used to produce an AI result. Timestamps help establish the order of processing events.

## 6. Data Lifecycle

The lifecycle begins when a resume or job description is uploaded. The system validates the input, stores the original file, extracts structured information, and passes the resulting profiles to the relevant recruitment modules.

ATS scores, screening reports, and interview results are stored as separate records linked through candidate and job IDs.

The decision-support stage uses these records to assist the authorized recruiter or hiring manager. Corrections and final outcomes can be retained as feedback for future evaluation and model improvement.

Data retention, deletion, and access policies should be defined before production deployment.

## 7. Versioning and Retraining

The system should maintain versions for:

- Data schemas
- Parsing and scoring logic
- AI models
- Training and evaluation datasets

When a model or parser changes, new results should record the version that generated them. Existing records should not be silently overwritten.

Training datasets should be separated from evaluation datasets. Dataset snapshots should record their source, version, preparation date, and validation status. Sensitive candidate information must be protected, and its use for model training must follow applicable privacy and organizational policies.

## 8. Reliability and Security

The pipeline should validate data before processing, record errors, and avoid storing incomplete results as successful outputs.

Access to resumes, interview records, and hiring decisions should be restricted to authorized users. Sensitive information should be protected in storage and transit. Audit records should support traceability without unnecessarily duplicating personal information.

## 9. Conclusion

The Day 7 design establishes a proposed structure for data flow and storage across the Zecpath recruitment pipeline. It defines how raw inputs, structured profiles, scores, reports, interview results, and hiring decisions should be connected through consistent metadata.

This design provides a foundation for future integration, reliable processing, traceability, and controlled improvement of AI components.