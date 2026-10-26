from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    BackgroundTasks
)

from uuid import uuid4
from typing import Dict, Any

from pathlib import Path

from api.logger import logger

from api.schemas import (
    ParseRequest,
    ParseResponse,
    ScoreRequest,
    ScoreResponse,
    ShortlistRequest,
    ShortlistResponse
)

from api.services import (
    calculate_ats_score,
    rank_and_shortlist
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Zecpath ATS AI API",
    description=(
        "REST API for resume parsing, ATS scoring "
        "and candidate shortlisting."
    ),
    version="1.0.0"
)


# ============================================================
# UPLOAD CONFIGURATION
# ============================================================

# Uploaded resumes will be stored here.
UPLOAD_DIR = Path("data/uploads")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# ASYNC JOB STORAGE
# ============================================================

# Temporary in-memory storage for background jobs.
jobs: Dict[str, Dict[str, Any]] = {}


# ============================================================
# BACKGROUND RESUME PROCESSING
# ============================================================

def process_resume_job(
    job_id: str,
    filename: str
):
    """
    Process an uploaded resume in the background.

    This provides the asynchronous job architecture.
    The existing parsing, normalization, scoring and
    ranking engines can be connected here.
    """

    logger.info(
        f"Background job started: {job_id}"
    )

    jobs[job_id]["status"] = "processing"

    try:

        logger.info(
            f"Processing resume: {filename}"
        )

        # ----------------------------------------------------
        # Resume processing pipeline
        # ----------------------------------------------------
        #
        # Future integration point:
        #
        # 1. Extract resume text
        # 2. Normalize resume
        # 3. Match against job description
        # 4. Calculate ATS score
        # 5. Rank candidate
        # 6. Apply shortlisting rules
        #
        # ----------------------------------------------------

        jobs[job_id]["status"] = "completed"

        jobs[job_id]["result"] = {
            "filename": filename,
            "message": (
                "Resume background processing "
                "completed successfully."
            )
        }

        logger.info(
            f"Background job completed: {job_id}"
        )

    except Exception as error:

        jobs[job_id]["status"] = "failed"

        jobs[job_id]["error"] = str(error)

        logger.exception(
            f"Background job failed: {job_id}"
        )


# ============================================================
# ROOT / HEALTH CHECK
# ============================================================

@app.get("/")
def root():
    """
    Health check endpoint.
    """

    logger.info(
        "Health check endpoint accessed."
    )

    return {
        "message": "Zecpath ATS AI API is running",
        "status": "healthy"
    }


# ============================================================
# RESUME UPLOAD
# ============================================================

@app.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...)
):
    """
    Upload and save a resume file.

    Supported formats:
    - PDF
    - DOCX
    - TXT
    """

    logger.info(
        f"Resume upload request received: {file.filename}"
    )

    # --------------------------------------------------------
    # Allowed resume formats
    # --------------------------------------------------------

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt"
    }

    # --------------------------------------------------------
    # Get filename
    # --------------------------------------------------------

    filename = file.filename or ""

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not filename.strip():

        logger.error(
            "Resume upload failed: filename is empty."
        )

        raise HTTPException(
            status_code=400,
            detail="Resume filename cannot be empty."
        )

    # --------------------------------------------------------
    # Get file extension
    # --------------------------------------------------------

    extension = Path(filename).suffix.lower()

    # --------------------------------------------------------
    # Validate file format
    # --------------------------------------------------------

    if extension not in allowed_extensions:

        logger.error(
            f"Unsupported resume format: {filename}"
        )

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported resume format. "
                "Use PDF, DOCX or TXT."
            )
        )

    # --------------------------------------------------------
    # Read actual uploaded file
    # --------------------------------------------------------

    file_content = await file.read()

    # --------------------------------------------------------
    # Check whether file contains data
    # --------------------------------------------------------

    if not file_content:

        logger.error(
            f"Resume upload failed: empty file - {filename}"
        )

        raise HTTPException(
            status_code=400,
            detail="Uploaded resume file is empty."
        )

    # --------------------------------------------------------
    # Prevent unsafe file paths
    # --------------------------------------------------------

    safe_filename = Path(filename).name

    # --------------------------------------------------------
    # Create final save path
    # --------------------------------------------------------

    file_path = UPLOAD_DIR / safe_filename

    # --------------------------------------------------------
    # Save uploaded file
    # --------------------------------------------------------

    try:

        with open(file_path, "wb") as output_file:
            output_file.write(file_content)

        logger.info(
            f"Resume uploaded successfully: {safe_filename}"
        )

    except OSError as error:

        logger.exception(
            f"Failed to save resume: {safe_filename}"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save resume: {str(error)}"
        )

    # --------------------------------------------------------
    # Return upload information
    # --------------------------------------------------------

    return {
        "message": "Resume uploaded successfully",
        "filename": safe_filename,
        "status": "uploaded",
        "file_size_bytes": len(file_content),
        "saved_path": str(file_path)
    }


# ============================================================
# ASYNC RESUME PROCESSING
# ============================================================

@app.post("/resume/process")
async def process_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Start asynchronous resume processing.

    The API returns a job ID immediately while
    the resume is processed in the background.
    """

    logger.info(
        f"Async resume processing requested: "
        f"{file.filename}"
    )

    # --------------------------------------------------------
    # Get filename
    # --------------------------------------------------------

    filename = file.filename or ""

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not filename.strip():

        raise HTTPException(
            status_code=400,
            detail="Resume filename cannot be empty."
        )

    # --------------------------------------------------------
    # Allowed formats
    # --------------------------------------------------------

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt"
    }

    extension = Path(filename).suffix.lower()

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported resume format. "
                "Use PDF, DOCX or TXT."
            )
        )

    # --------------------------------------------------------
    # Read uploaded file
    # --------------------------------------------------------

    file_content = await file.read()

    if not file_content:

        raise HTTPException(
            status_code=400,
            detail="Uploaded resume file is empty."
        )

    # --------------------------------------------------------
    # Create safe filename
    # --------------------------------------------------------

    safe_filename = Path(filename).name

    file_path = UPLOAD_DIR / safe_filename

    # --------------------------------------------------------
    # Save resume
    # --------------------------------------------------------

    try:

        with open(file_path, "wb") as output_file:
            output_file.write(file_content)

    except OSError as error:

        logger.exception(
            "Failed to save resume for async processing."
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save resume: {str(error)}"
        )

    # --------------------------------------------------------
    # Create unique job ID
    # --------------------------------------------------------

    job_id = str(uuid4())

    jobs[job_id] = {
        "job_id": job_id,
        "filename": safe_filename,
        "status": "queued",
        "result": None,
        "error": None
    }

    # --------------------------------------------------------
    # Add background task
    # --------------------------------------------------------

    background_tasks.add_task(
        process_resume_job,
        job_id,
        safe_filename
    )

    logger.info(
        f"Async job created: {job_id}"
    )

    # --------------------------------------------------------
    # Return immediately
    # --------------------------------------------------------

    return {
        "message": "Resume processing started.",
        "job_id": job_id,
        "filename": safe_filename,
        "status": "queued"
    }


# ============================================================
# ASYNC JOB STATUS
# ============================================================

@app.get("/resume/process/{job_id}")
def get_job_status(
    job_id: str
):
    """
    Get the current status of a resume-processing job.
    """

    job = jobs.get(job_id)

    if job is None:

        logger.error(
            f"Processing job not found: {job_id}"
        )

        raise HTTPException(
            status_code=404,
            detail="Processing job not found."
        )

    logger.info(
        f"Job status requested: {job_id}"
    )

    return job


# ============================================================
# RESUME PARSING
# ============================================================

@app.post(
    "/resume/parse",
    response_model=ParseResponse
)
def parse_resume(
    request: ParseRequest
):
    """
    Parse resume text.

    The actual PDF/DOCX extraction engine
    can be connected to this endpoint.
    """

    logger.info(
        "Resume parsing request received."
    )

    # --------------------------------------------------------
    # Validate resume text
    # --------------------------------------------------------

    if not request.text.strip():

        logger.error(
            "Resume parsing failed: empty resume text."
        )

        raise HTTPException(
            status_code=400,
            detail="Resume text cannot be empty."
        )

    # --------------------------------------------------------
    # Return parsed resume
    # --------------------------------------------------------

    logger.info(
        "Resume parsing completed successfully."
    )

    return {
        "status": "parsed",
        "raw_text": request.text
    }


# ============================================================
# CANDIDATE ATS SCORING
# ============================================================

@app.post(
    "/candidate/score",
    response_model=ScoreResponse
)
def score_candidate(
    request: ScoreRequest
):
    """
    Generate an ATS score for a candidate.
    """

    logger.info(
        "Candidate ATS scoring request received."
    )

    # --------------------------------------------------------
    # Calculate ATS score
    # --------------------------------------------------------

    try:

        result = calculate_ats_score(
            skill_match=request.skill_match,
            experience_relevance=request.experience_relevance,
            education_alignment=request.education_alignment,
            semantic_similarity=request.semantic_similarity
        )

        logger.info(
            f"Candidate ATS scoring completed. "
            f"Final score: {result['final_score']}"
        )

    except Exception as error:

        logger.exception(
            "Candidate ATS scoring failed."
        )

        raise HTTPException(
            status_code=500,
            detail=f"ATS scoring failed: {str(error)}"
        )

    # --------------------------------------------------------
    # Return scoring result
    # --------------------------------------------------------

    return result


# ============================================================
# CANDIDATE SHORTLISTING
# ============================================================

@app.post(
    "/candidate/shortlist",
    response_model=ShortlistResponse
)
def shortlist_candidate(
    request: ShortlistRequest
):
    """
    Rank and shortlist candidates.
    """

    logger.info(
        f"Candidate shortlisting request received. "
        f"Number of candidates: {len(request.candidates)}"
    )

    # --------------------------------------------------------
    # Convert Pydantic candidate objects
    # into dictionaries
    # --------------------------------------------------------

    candidates = [
        candidate.model_dump()
        for candidate in request.candidates
    ]

    # --------------------------------------------------------
    # Rank and shortlist
    # --------------------------------------------------------

    try:

        results = rank_and_shortlist(
            candidates
        )

        logger.info(
            "Candidate ranking and shortlisting "
            "completed successfully."
        )

    except Exception as error:

        logger.exception(
            "Candidate ranking and shortlisting failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Candidate shortlisting failed: "
                f"{str(error)}"
            )
        )

    # --------------------------------------------------------
    # Return ranked results
    # --------------------------------------------------------

    return {
        "results": results
    }