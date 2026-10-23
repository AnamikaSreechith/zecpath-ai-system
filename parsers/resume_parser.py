import re
import json
from pathlib import Path
from parsers.experience_parser import parse_experience
from parsers.resume_section_classifier import segment_resume
from parsers.skill_extraction_engine import extract_skills

from pypdf import PdfReader
from docx import Document

from utils.logger import get_logger


logger = get_logger(__name__)


def get_candidate_id(file_path):
    """Generate a stable candidate ID from the resume filename."""

    file_name = Path(file_path).stem.lower()

    match = re.search(
        r"resume[_-]?(\d+)",
        file_name
    )

    if match:
        number = int(match.group(1))
        return f"CAND-{number:03d}"

    # Fallback for test or custom filenames.
    return "CAND-001"

def extract_pdf_text(file_path):
    """Extract text from a text-based PDF resume."""
    reader = PdfReader(str(file_path))
    pages = []

    for page in reader.pages:
        pages.append(page.extract_text() or "")

    text = "\n".join(pages)

    if not text.strip():
        raise ValueError(
            "No text found in PDF. It may be a scanned document requiring OCR."
        )

    logger.info("Text extracted from PDF: %s", file_path)

    return text


def extract_docx_text(file_path):
    """Extract paragraphs and table content from a DOCX resume."""
    document = Document(str(file_path))
    parts = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            parts.append(paragraph.text)

    # Also extract text stored in tables.
    for table in document.tables:
        for row in table.rows:
            row_text = [
                cell.text.strip()
                for cell in row.cells
                if cell.text.strip()
            ]

            if row_text:
                parts.append(" | ".join(row_text))

    text = "\n".join(parts)

    if not text.strip():
        raise ValueError("No text found in DOCX resume.")

    logger.info("Text extracted from DOCX: %s", file_path)

    return text


def clean_resume_text(text):
    """Clean whitespace, bullet symbols, and unwanted control characters."""

    if not text or not text.strip():
        raise ValueError("Resume text cannot be empty.")

    # Normalize line endings.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove unwanted control characters.
    text = re.sub(
        r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]",
        "",
        text
    )

    # Standardize common bullet symbols.
    text = re.sub(
        r"[•●▪◦‣⁃]",
        "-",
        text
    )

    # Remove trailing spaces from each line.
    lines = [line.strip() for line in text.split("\n")]

    text = "\n".join(lines)

    # Remove excessive blank lines.
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    # Normalize repeated spaces.
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    return text.strip()


def parse_resume_text(text):
    """Validate resume text and return a basic structured result."""

    if not text or not text.strip():
        raise ValueError("Resume text cannot be empty.")

    cleaned_text = clean_resume_text(text)

    logger.info("Resume text received and cleaned")

    return {
        "raw_text": text.strip(),
        "cleaned_text": cleaned_text,
        "status": "processed"
    }


def extract_resume(
    file_path,
    output_dir="data/extracted_resumes"
):
    """
    Extract, clean, segment, extract skills and experience,
    and save structured resume data.
    """

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Resume file not found: {file_path}"
        )

    extension = file_path.suffix.lower()

    # Step 1: Get a stable candidate ID.
    candidate_id = get_candidate_id(file_path)

    # Step 2: Extract raw text from the resume.
    if extension == ".pdf":
        raw_text = extract_pdf_text(file_path)

    elif extension == ".docx":
        raw_text = extract_docx_text(file_path)

    else:
        raise ValueError(
            "Unsupported file type. Use PDF or DOCX."
        )

    # Step 3: Clean the extracted resume text.
    result = parse_resume_text(raw_text)

    # Step 4: Detect and separate resume sections.
    sections = segment_resume(
        result["cleaned_text"]
    )

    # Step 5: Extract skills from the Skills section.
    skills_text = sections.get(
        "skills",
        ""
    )

    if skills_text.strip():
        skills = extract_skills(skills_text)
    else:
        skills = []

    # Step 6: Extract and structure work experience.
    experience_text = sections.get(
        "work_experience",
        ""
    )

    if experience_text.strip():
        experience = parse_experience(
            experience_text,
            candidate_id=candidate_id
        )
    else:
        experience = {
            "candidate_id": candidate_id,
            "experiences": [],
            "total_experience_months": 0,
            "gaps": [],
            "overlaps": []
        }

    # Step 7: Add structured sections.
    result["sections"] = sections

    # Step 8: Add normalized and scored skills.
    result["extracted_skills"] = skills

    # Step 9: Add structured experience.
    result["experience"] = experience

    # Step 10: Create output directory.
    output_path = Path(output_dir)

    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    # Step 11: Create output JSON filename.
    output_file = (
        output_path /
        f"{file_path.stem}.json"
    )

    # Step 12: Save complete structured result.
    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "candidate_id": candidate_id,
                "source_file": file_path.name,
                **result
            },
            file,
            indent=4,
            ensure_ascii=False
        )

    logger.info(
        "Structured resume output saved: %s",
        output_file
    )

    return {
        "candidate_id": candidate_id,
        **result
    }