from pydantic import BaseModel, Field
from typing import List


# ============================================================
# RESUME UPLOAD
# ============================================================

class ResumeUploadResponse(BaseModel):
    message: str
    filename: str
    status: str
    file_size_bytes: int
    saved_path: str


# ============================================================
# RESUME PARSING
# ============================================================

class ParseRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        description="Raw resume text to be parsed."
    )


class ParseResponse(BaseModel):
    status: str
    raw_text: str


# ============================================================
# ATS SCORING
# ============================================================

class ScoreRequest(BaseModel):
    skill_match: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Skill matching score between 0 and 1."
    )

    experience_relevance: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Experience relevance score between 0 and 1."
    )

    education_alignment: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Education alignment score between 0 and 1."
    )

    semantic_similarity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Semantic similarity score between 0 and 1."
    )


class ScoreResponse(BaseModel):
    final_score: float
    match_level: str
    score_breakdown: dict
    weights: dict


# ============================================================
# CANDIDATE
# ============================================================

class Candidate(BaseModel):
    candidate_id: str = Field(
        ...,
        min_length=1,
        description="Unique candidate identifier."
    )

    score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Final ATS score between 0 and 100."
    )


# ============================================================
# SHORTLISTING
# ============================================================

class ShortlistRequest(BaseModel):
    candidates: List[Candidate] = Field(
        ...,
        min_length=1,
        description="List of candidates to rank and shortlist."
    )


class ShortlistResponse(BaseModel):
    results: list