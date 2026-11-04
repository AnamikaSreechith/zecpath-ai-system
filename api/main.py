from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException

from api.logger import logger

from api.schemas import (
    ResumeProcessRequest,
    ParseRequest,
    ParseResponse,
    CandidateScoreRequest,
    CandidateScoreResponse,
    ShortlistRequest,
    ShortlistResponse,
)

from api.services import (
    save_uploaded_resume,
    get_resume,
    load_job,
    process_resume_for_job,
    parse_response_data,
    score_candidate,
    shortlist_candidate,
)


app = FastAPI(
    title="Zecpath ATS AI API",
    description="API for resume upload, parsing, ATS scoring and candidate shortlisting.",
    version="2.0.0",
)


# --------------------------------------------------
# 1. HEALTH CHECK
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "API system successfully running",
        "status": "healthy"
    }


# --------------------------------------------------
# 2. RESUME UPLOAD
# Candidate ID is generated automatically.
# --------------------------------------------------

@app.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):

    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if not filename.strip():
        raise HTTPException(
            status_code=400,
            detail="Resume filename cannot be empty."
        )

    if extension not in {".pdf", ".docx", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail="Upload a PDF, DOCX or TXT resume."
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded resume file is empty."
        )

    try:
        result = save_uploaded_resume(
            Path(filename).name,
            content
        )

        return {
            "message": "Resume uploaded successfully.",
            **result
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:
        logger.exception("Resume upload failed.")

        raise HTTPException(
            status_code=500,
            detail=f"Resume upload failed: {exc}"
        )


# --------------------------------------------------
# 3. RESUME PROCESSING
# --------------------------------------------------

@app.post("/resume/process")
def process_resume(request: ResumeProcessRequest):

    record = get_resume(request.resume_id)

    if not record:
        raise HTTPException(
            status_code=404,
            detail="resume_id was not found."
        )

    if not load_job(request.job_id):
        raise HTTPException(
            status_code=404,
            detail="job_id was not found."
        )

    try:
        process_resume_for_job(
            request.resume_id,
            request.job_id
        )

        return {
            "message": "Resume processed successfully.",
            "resume_id": request.resume_id,
            "candidate_id": record["candidate_id"],
            "job_id": request.job_id,
            "filename": record["filename"],
            "status": "processed"
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:
        logger.exception("Resume processing failed.")

        raise HTTPException(
            status_code=500,
            detail=f"Resume processing failed: {exc}"
        )


# --------------------------------------------------
# 4. RESUME PARSING
# --------------------------------------------------

@app.post("/resume/parse", response_model=ParseResponse)
def parse_resume(request: ParseRequest):

    try:
        return parse_response_data(
            request.resume_id,
            request.job_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:
        logger.exception("Resume parsing failed.")

        raise HTTPException(
            status_code=500,
            detail=f"Resume parsing failed: {exc}"
        )


# --------------------------------------------------
# 5. CANDIDATE SCORING
# --------------------------------------------------

@app.post(
    "/candidate/score",
    response_model=CandidateScoreResponse
)
def score_candidate_endpoint(request: CandidateScoreRequest):

    try:
        return score_candidate(
            request.candidate_id,
            request.job_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    except Exception as exc:
        logger.exception("Candidate scoring failed.")

        raise HTTPException(
            status_code=500,
            detail=f"ATS scoring failed: {exc}"
        )


# --------------------------------------------------
# 6. CANDIDATE SHORTLISTING
# --------------------------------------------------

@app.post(
    "/candidate/shortlist",
    response_model=ShortlistResponse
)
def shortlist_candidate_endpoint(request: ShortlistRequest):

    try:
        return shortlist_candidate(
            request.candidate_id,
            request.job_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    except Exception as exc:
        logger.exception("Candidate shortlisting failed.")

        raise HTTPException(
            status_code=500,
            detail=f"Shortlisting failed: {exc}"
        )