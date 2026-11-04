from pydantic import BaseModel, Field
from typing import Any


# --------------------------------------------------
# RESUME PROCESSING
# --------------------------------------------------

class ResumeProcessRequest(BaseModel):
    resume_id: str
    job_id: str


# --------------------------------------------------
# RESUME PARSING
# --------------------------------------------------

class ParseRequest(BaseModel):
    resume_id: str
    job_id: str


class WorkExperience(BaseModel):
    company: str | None = None
    job_title: str | None = None
    designation: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    duration_months: int | None = None


class ParseResponse(BaseModel):
    resume_id: str
    candidate_id: str
    job_id: str

    personal_details: dict[str, Any] = Field(default_factory=dict)

    technical_skills: list[str] = Field(default_factory=list)
    non_technical_skills: list[str] = Field(default_factory=list)

    work_experience: list[dict[str, Any]] = Field(default_factory=list)

    education: list[dict[str, Any]] = Field(default_factory=list)

    achievements: list[str] = Field(default_factory=list)

    matched_skills: list[str] = Field(default_factory=list)
    missing_required_skills: list[str] = Field(default_factory=list)

    status: str


# --------------------------------------------------
# CANDIDATE SCORING
# --------------------------------------------------

class CandidateScoreRequest(BaseModel):
    candidate_id: str
    job_id: str


class CandidateScoreResponse(BaseModel):
    candidate_id: str
    job_id: str

    score: float
    match_level: str

    score_breakdown: dict[str, Any] = Field(default_factory=dict)

    status: str


# --------------------------------------------------
# CANDIDATE SHORTLISTING
# --------------------------------------------------

class ShortlistRequest(BaseModel):
    candidate_id: str
    job_id: str


class ShortlistResponse(BaseModel):
    candidate_id: str
    score: float
    status: str