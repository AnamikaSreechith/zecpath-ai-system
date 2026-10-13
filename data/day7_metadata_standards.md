# Day 7 – AI Data Metadata Standards

## 1. Objective

The objective of this document is to establish consistent metadata standards for the Zecpath AI recruitment platform.

Metadata describes a data record, including its identity, origin, creation time, processing status, and the version of the software or model that generated it.

Consistent metadata allows different recruitment modules to exchange information, trace results, identify outdated records, and prepare reliable datasets for future model evaluation and retraining.

These standards describe the proposed design and do not imply that every field is currently implemented in the application.

## 2. Metadata Principles

The platform should follow these principles:

- Use stable, unique identifiers for candidates, jobs, and records.
- Use consistent field names across modules.
- Store timestamps in UTC using ISO 8601 format.
- Track parser, scoring, and model versions separately.
- Record schema versions for structured data.
- Preserve references between related records.
- Avoid storing unnecessary personal information in metadata.
- Keep historical assessment records traceable when processing logic changes.

## 3. Candidate ID Standard

**Field:** `candidate_id`

**Purpose:** Identifies a candidate across the recruitment lifecycle.

**Example:**

```json
{
  "candidate_id": "CAND001"
}
```

Candidate IDs should be unique and stable. The same candidate should retain the same identifier across relevant applications, subject to the platform's identity and privacy policies.

A candidate ID should not contain sensitive information such as a phone number, email address, or government identification number.

## 4. Job ID Standard

**Field:** `job_id`

**Purpose:** Identifies a specific job opening.

**Example:**

```json
{
  "job_id": "JOB001"
}
```

Every job opening should have a unique identifier. Candidate assessments must reference the appropriate job ID so that scores and reports cannot be confused between different positions.

## 5. Record ID Standard

**Field:** `record_id`

**Purpose:** Uniquely identifies an individual record, such as a parsed profile, ATS score, screening report, interview result, or hiring decision.

**Example:**

```json
{
  "record_id": "ATS001"
}
```

Each newly generated assessment record should receive its own identifier. Record IDs should not be reused for unrelated results.

## 6. Timestamp Standards

The platform should use UTC timestamps in ISO 8601 format.

Recommended fields:

- `created_at`: When the record was created.
- `updated_at`: When the record was last updated, where applicable.
- `processed_at`: When a processing operation completed.
- `event_timestamp`: When a specific lifecycle event occurred.

Example:

```json
{
  "created_at": "2026-10-13T08:00:00Z",
  "updated_at": "2026-10-13T08:30:00Z",
  "processed_at": "2026-10-13T08:15:00Z"
}
```

The `Z` suffix indicates UTC time.

Timestamps help establish processing order, investigate errors, compare results, and determine when a record was generated.

## 7. Model and Parser Version Standards

AI-generated or rule-based results should identify the implementation version used to produce them.

Recommended fields:

- `model_version`: Version of the AI model, when a model is used.
- `parser_version`: Version of the parser.
- `scoring_version`: Version of the ATS scoring logic.
- `evaluation_version`: Version of the interview evaluation logic.
- `schema_version`: Version of the data structure.

Example:

```json
{
  "parser_version": "resume-parser-1.0",
  "scoring_version": "ats-rules-1.0",
  "schema_version": "1.0"
}
```

A rule-based component should use a field such as `scoring_version` or `parser_version` rather than claiming that it used a trained AI model.

When a trained model is introduced, its identifier and version should be recorded separately from the preprocessing and scoring logic.

## 8. Processing Status Standard

A consistent `processing_status` field should describe the current state of a record or operation.

Suggested values:

- `pending`: Processing has not started.
- `processing`: Processing is in progress.
- `processed`: Processing completed successfully.
- `failed`: Processing failed.
- `requires_review`: Human review is required.

Example:

```json
{
  "processing_status": "processed"
}
```

The permitted values should be documented and validated consistently across modules.

The platform should also record an error code or safe error description when processing fails, without exposing unnecessary personal information.

## 9. Standard Metadata Structure

A proposed common metadata structure is:

```json
{
  "record_id": "PROFILE001",
  "candidate_id": "CAND001",
  "job_id": "JOB001",
  "created_at": "2026-10-13T08:00:00Z",
  "updated_at": "2026-10-13T08:00:00Z",
  "processed_at": "2026-10-13T08:00:00Z",
  "parser_version": "resume-parser-1.0",
  "model_version": null,
  "schema_version": "1.0",
  "processing_status": "processed"
}
```

This is a proposed example. Fields should be included according to the record type. For example, a raw resume record may not have a model version, and a job description record may not require a candidate ID.

A `null` model version indicates that no trained model version has been recorded for this example.

## 10. Dataset Versioning

Training, validation, and testing datasets should be versioned independently of model versions.

Recommended dataset metadata fields:

- `dataset_id`: Unique dataset identifier.
- `dataset_version`: Version of the dataset.
- `created_at`: Dataset creation timestamp.
- `source_description`: Description of the source data.
- `schema_version`: Data structure version.
- `preprocessing_version`: Version of preprocessing logic.
- `split_type`: Training, validation, or testing.
- `record_count`: Number of records in the dataset.
- `approval_status`: Whether the dataset has passed the required checks.

Example:

```json
{
  "dataset_id": "RESUME_DATASET",
  "dataset_version": "1.0.0",
  "created_at": "2026-10-13T10:00:00Z",
  "schema_version": "1.0",
  "preprocessing_version": "resume-cleaning-1.0",
  "split_type": "training",
  "record_count": 100,
  "approval_status": "pending_review"
}
```

The example is illustrative and does not represent an actual dataset of 100 records.

Dataset versions should be immutable once approved for a particular experiment. Corrections or additions should produce a new version with a documented change history.

## 11. Retraining and Model Traceability

Before a retraining process, the team should:

1. Identify the approved source dataset.
2. Verify data quality and schema compatibility.
3. Check that data use complies with privacy and organizational policies.
4. Separate training, validation, and test data appropriately.
5. Record the dataset and preprocessing versions.
6. Evaluate the new model against documented metrics.
7. Register the model version and evaluation results.
8. Retain a reference between model outputs and the version that generated them.

A new model version should not silently overwrite historical assessment results. Reprocessing should generate traceable new records or explicitly version the updated results.

## 12. Privacy and Access Control

Candidate data and hiring records are sensitive. The platform should:

- Restrict access to authorized personnel.
- Avoid personal information in identifiers and filenames.
- Define retention and deletion rules.
- Protect data in storage and transit.
- Record access to sensitive records where appropriate.
- Use approved and appropriately protected datasets for training and evaluation.

## 13. Conclusion

The metadata standards define how candidate IDs, job IDs, record IDs, timestamps, processing statuses, parser versions, model versions, and dataset versions should be represented across the Zecpath AI recruitment platform.

Consistent metadata supports traceability, interoperability, reproducibility, and controlled improvement of the recruitment pipeline.

These standards provide a foundation for implementing and validating metadata across the platform as its components evolve.