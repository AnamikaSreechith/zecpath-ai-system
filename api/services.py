import json
import re
import sqlite3
from pathlib import Path
from uuid import uuid4

from parsers.resume_parser import extract_resume

from matching.candidate_ranking_pipeline import generate_scores
from matching.candidate_ranking_engine import classify_candidate_status
from matching.fairness_normalization import normalize_candidate_for_scoring


BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "data" / "uploads"
PARSED_RESUME_DIR = BASE_DIR / "data" / "api_parsed_resumes"
RESUME_DATA_DIR = BASE_DIR / "data" / "resumes"
JD_DIR = BASE_DIR / "data" / "job_descriptions" / "parsed_jds"
DB_PATH = BASE_DIR / "data" / "api_storage.db"

for directory in (UPLOAD_DIR, PARSED_RESUME_DIR):
    directory.mkdir(parents=True, exist_ok=True)


DEFAULT_JOBS = {
    "JOB001": "python_developer.json",
    "JOB002": "hr_recruiter.json",
    "JOB003": "data_analyst.json",
    "JOB004": "java_developer.json",
    "JOB005": "machine_learning_engineer.json",
}


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_storage():
    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                resume_id TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'uploaded',
                parsed_path TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS resume_jobs (
                resume_id TEXT NOT NULL,
                job_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                score REAL,
                match_level TEXT,
                score_breakdown TEXT,
                PRIMARY KEY (resume_id, job_id)
            )
        """)

        conn.commit()


# --------------------------------------------------
# AUTOMATIC CANDIDATE ID GENERATION
# --------------------------------------------------

def generate_candidate_id(conn):
    """
    Generate the next available candidate ID.

    Existing dataset IDs CAND001-CAND010 are preserved.
    New uploaded candidates continue from CAND011.
    """

    existing_ids = set()

    rows = conn.execute(
        "SELECT candidate_id FROM resumes"
    ).fetchall()

    for row in rows:
        existing_ids.add(row["candidate_id"])

    if RESUME_DATA_DIR.exists():

        for file_path in RESUME_DATA_DIR.glob("*.json"):

            try:
                data = json.loads(
                    file_path.read_text(encoding="utf-8")
                )

                candidate_id = data.get("candidate_id")

                if candidate_id:
                    existing_ids.add(candidate_id)

            except (OSError, json.JSONDecodeError):
                continue

    highest_number = 0

    for candidate_id in existing_ids:

        match = re.fullmatch(r"CAND(\d+)", candidate_id)

        if match:
            number = int(match.group(1))
            highest_number = max(highest_number, number)

    next_number = highest_number + 1

    while True:

        candidate_id = f"CAND{next_number:03d}"

        if candidate_id not in existing_ids:
            return candidate_id

        next_number += 1


# --------------------------------------------------
# EXISTING DATASET CANDIDATES
# --------------------------------------------------

def find_dataset_resume(candidate_id: str):
    """Find an existing structured resume by candidate ID."""

    for file_path in sorted(RESUME_DATA_DIR.glob("*.json")):

        try:
            data = json.loads(
                file_path.read_text(encoding="utf-8")
            )

            if data.get("candidate_id") == candidate_id:
                return file_path, data

        except (OSError, json.JSONDecodeError):
            continue

    return None, None


def register_dataset_candidate(candidate_id: str):

    file_path, data = find_dataset_resume(candidate_id)

    if not file_path:
        return None

    resume_id = f"DATA-{candidate_id}"

    with get_connection() as conn:

        conn.execute("""
            INSERT OR IGNORE INTO resumes
            (resume_id, candidate_id, filename, file_path, status, parsed_path)
            VALUES (?, ?, ?, ?, 'parsed', ?)
        """, (
            resume_id,
            candidate_id,
            file_path.name,
            str(file_path),
            str(file_path)
        ))

        conn.commit()

    return get_resume(resume_id)


# --------------------------------------------------
# RESUME UPLOAD
# --------------------------------------------------

def save_uploaded_resume(filename: str, content: bytes):

    extension = Path(filename).suffix.lower()

    if extension not in {".pdf", ".docx", ".txt"}:
        raise ValueError("Use PDF, DOCX or TXT.")

    if not content:
        raise ValueError("Uploaded resume file is empty.")

    resume_id = f"RES-{uuid4().hex[:12].upper()}"

    stored_name = f"{resume_id}{extension}"
    destination = UPLOAD_DIR / stored_name

    destination.write_bytes(content)

    try:
        with get_connection() as conn:

            conn.execute("BEGIN IMMEDIATE")

            candidate_id = generate_candidate_id(conn)

            conn.execute("""
                INSERT INTO resumes
                (resume_id, candidate_id, filename, file_path, status)
                VALUES (?, ?, ?, ?, 'uploaded')
            """, (
                resume_id,
                candidate_id,
                filename,
                str(destination)
            ))

            conn.commit()

    except Exception:
        if destination.exists():
            destination.unlink()
        raise

    return {
        "resume_id": resume_id,
        "candidate_id": candidate_id,
        "filename": filename,
        "status": "uploaded"
    }


def get_resume(resume_id: str):

    with get_connection() as conn:

        row = conn.execute(
            "SELECT * FROM resumes WHERE resume_id = ?",
            (resume_id,)
        ).fetchone()

    if row:
        return dict(row)

    if resume_id.startswith("DATA-"):

        candidate_id = resume_id.replace("DATA-", "", 1)

        return register_dataset_candidate(candidate_id)

    return None


# --------------------------------------------------
# JOB DESCRIPTION
# --------------------------------------------------

def load_job(job_id: str):
    """Load only the five configured job descriptions."""

    filename = DEFAULT_JOBS.get(job_id)

    if not filename:
        return None

    path = JD_DIR / filename

    if not path.exists():
        return None

    return json.loads(
        path.read_text(encoding="utf-8")
    )


def get_skill_names(skills):

    names = []

    for skill in skills or []:

        if isinstance(skill, dict):
            name = skill.get("name", "")
        else:
            name = str(skill)

        if name:
            names.append(name.strip())

    return names


def compare_job_skills(parsed: dict, jd: dict):

    resume_skills = get_skill_names(
        parsed.get("skills", parsed.get("technical_skills", []))
    )

    resume_set = {
        skill.casefold() for skill in resume_skills
    }

    required_skills = get_skill_names(
        jd.get("required_skills", [])
    )

    matched = [
        skill for skill in required_skills
        if skill.casefold() in resume_set
    ]

    missing = [
        skill for skill in required_skills
        if skill.casefold() not in resume_set
    ]

    return {
        "matched_skills": matched,
        "missing_required_skills": missing
    }


# --------------------------------------------------
# PARSING HELPERS
# --------------------------------------------------

def normalize_parsed_resume(parsed: dict, resume_record: dict):

    skills = parsed.get("skills", [])

    if not skills:
        skills = parsed.get("extracted_skills", [])

    if not skills:
        skills = parsed.get("technical_skills", [])

    experience_data = parsed.get("experience", [])

    if isinstance(experience_data, dict):
        experience_data = experience_data.get("experiences", [])

    if not experience_data:
        experience_data = parsed.get("work_experience", [])

    education = parsed.get("education", [])

    return {
        **parsed,
        "resume_id": resume_record["resume_id"],
        "candidate_id": resume_record["candidate_id"],
        "skills": skills,
        "normalized_skills": skills,
        "experience": experience_data,
        "work_experience": experience_data,
        "education": education,
        "personal_details": parsed.get("personal_details", {}),
        "technical_skills": get_skill_names(skills),
        "non_technical_skills": parsed.get("non_technical_skills", []),
        "achievements": parsed.get("achievements", []),
        "status": "parsed"
    }


def _parse_resume_file(resume_record: dict):

    path = Path(resume_record["file_path"])

    parsed = extract_resume(
        file_path=path,
        output_dir=PARSED_RESUME_DIR,
        candidate_id=resume_record["candidate_id"]
    )

    return normalize_parsed_resume(parsed, resume_record)


# --------------------------------------------------
# PROCESS RESUME AGAINST SELECTED JOB
# --------------------------------------------------

def process_resume_for_job(resume_id: str, job_id: str):

    resume_record = get_resume(resume_id)

    if not resume_record:
        raise ValueError(
            f"Resume ID '{resume_id}' was not found."
        )

    jd = load_job(job_id)

    if not jd:
        raise ValueError(
            f"Job ID '{job_id}' was not found."
        )

    source_path = Path(resume_record["file_path"])

    if source_path.suffix.lower() == ".json":

        parsed = json.loads(
            source_path.read_text(encoding="utf-8")
        )

        parsed = normalize_parsed_resume(
            parsed,
            resume_record
        )

    else:

        parsed_path = PARSED_RESUME_DIR / f"{resume_id}.json"

        # Always parse the original uploaded file again.
        # This prevents outdated cached parsing results.
        parsed = _parse_resume_file(resume_record)

        parsed_path.write_text(
            json.dumps(
                parsed,
                indent=4,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

        with get_connection() as conn:

            conn.execute("""
                UPDATE resumes
                SET status='parsed', parsed_path=?
                WHERE resume_id=?
            """, (str(parsed_path), resume_id))

            conn.commit()

    with get_connection() as conn:

        conn.execute("""
            INSERT INTO resume_jobs (resume_id, job_id, status)
            VALUES (?, ?, 'processed')
            ON CONFLICT(resume_id, job_id)
            DO UPDATE SET status='processed'
        """, (resume_id, job_id))

        conn.commit()

    return parsed


def get_parsed_resume(resume_id: str):

    record = get_resume(resume_id)

    if not record:
        return None

    path = Path(
        record["parsed_path"] or record["file_path"]
    )

    if not path.exists():
        return None

    data = json.loads(
        path.read_text(encoding="utf-8")
    )

    return normalize_parsed_resume(data, record)


# --------------------------------------------------
# PARSE RESPONSE
# --------------------------------------------------

def parse_response_data(resume_id: str, job_id: str):

    record = get_resume(resume_id)

    if not record:
        raise ValueError("Resume ID was not found.")

    with get_connection() as conn:

        relation = conn.execute("""
            SELECT status FROM resume_jobs
            WHERE resume_id=? AND job_id=?
        """, (resume_id, job_id)).fetchone()

    if not relation:
        raise ValueError(
            "Process the resume against this job before parsing."
        )

    parsed = get_parsed_resume(resume_id)
    jd = load_job(job_id)

    if not parsed:
        raise ValueError("Parsed resume data is not available.")

    if not jd:
        raise ValueError("Job ID was not found.")

    skill_comparison = compare_job_skills(parsed, jd)

    return {
        "resume_id": resume_id,
        "candidate_id": parsed["candidate_id"],
        "job_id": job_id,
        "personal_details": parsed.get("personal_details", {}),
        "technical_skills": get_skill_names(
            parsed.get("technical_skills", [])
        ),
        "non_technical_skills": get_skill_names(
            parsed.get("non_technical_skills", [])
        ),
        "work_experience": parsed.get("work_experience", []),
        "education": parsed.get("education", []),
        "achievements": parsed.get("achievements", []),
        "matched_skills": skill_comparison["matched_skills"],
        "missing_required_skills": skill_comparison[
            "missing_required_skills"
        ],
        "status": "parsed"
    }


# --------------------------------------------------
# ATS SCORING
# --------------------------------------------------

def score_resume_for_job(parsed: dict, job_id: str):

    jd = load_job(job_id)

    if not jd:
        raise ValueError(
            f"Job ID '{job_id}' was not found."
        )

    normalized_resume = normalize_candidate_for_scoring(parsed)

    scores = generate_scores(
        [normalized_resume],
        jd
    )

    if not scores:
        raise ValueError(
            "ATS scoring engine did not return a score."
        )

    score_result = scores[0]

    status = classify_candidate_status(
        score_result["score"]
    )

    return score_result, status


def score_candidate(candidate_id: str, job_id: str):

    jd = load_job(job_id)

    if not jd:
        raise ValueError(
            f"Job ID '{job_id}' was not found."
        )

    # Prefer the latest uploaded resume processed for this job.
    with get_connection() as conn:

        row = conn.execute("""
            SELECT r.resume_id
            FROM resumes r
            JOIN resume_jobs rj ON r.resume_id = rj.resume_id
            WHERE r.candidate_id=?
              AND rj.job_id=?
              AND rj.status IN ('processed', 'scored')
            ORDER BY r.created_at DESC
            LIMIT 1
        """, (candidate_id, job_id)).fetchone()

    if row:

        parsed = get_parsed_resume(row["resume_id"])

    else:

        # Fall back to the existing structured dataset.
        dataset_path, dataset = find_dataset_resume(candidate_id)

        if not dataset:
            raise ValueError(
                "Candidate was not found. Check candidate_id."
            )

        record = {
            "resume_id": f"DATA-{candidate_id}",
            "candidate_id": candidate_id,
            "filename": dataset_path.name,
            "file_path": str(dataset_path),
            "parsed_path": str(dataset_path)
        }

        parsed = normalize_parsed_resume(
            dataset,
            record
        )

    if not parsed:
        raise ValueError(
            "Candidate resume data is not available."
        )

    score_result, status = score_resume_for_job(
        parsed,
        job_id
    )

    resume_id = parsed["resume_id"]

    with get_connection() as conn:

        conn.execute("""
            INSERT INTO resume_jobs
            (resume_id, job_id, status, score, match_level, score_breakdown)
            VALUES (?, ?, 'scored', ?, ?, ?)
            ON CONFLICT(resume_id, job_id)
            DO UPDATE SET
                status='scored',
                score=excluded.score,
                match_level=excluded.match_level,
                score_breakdown=excluded.score_breakdown
        """, (
            resume_id,
            job_id,
            score_result["score"],
            score_result["match_level"],
            json.dumps(score_result["score_breakdown"])
        ))

        conn.commit()

    return {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "score": score_result["score"],
        "match_level": score_result["match_level"],
        "score_breakdown": score_result["score_breakdown"],
        "status": status
    }


# --------------------------------------------------
# SHORTLISTING
# --------------------------------------------------

def shortlist_candidate(candidate_id: str, job_id: str):

    result = score_candidate(candidate_id, job_id)

    return {
        "candidate_id": candidate_id,
        "score": result["score"],
        "status": result["status"]
    }


# Initialize database when API starts.
initialize_storage()