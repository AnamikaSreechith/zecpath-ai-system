
import re
import json
from pathlib import Path
from parsers.resume_section_classifier import segment_resume
from pypdf import PdfReader
from docx import Document

from utils.logger import get_logger

logger = get_logger(__name__)


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

    # Normalize line endings and remove control characters.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Standardize common bullet symbols.
    text = re.sub(r"[•●▪◦‣⁃]", "-", text)

    # Remove trailing spaces and repeated blank lines.
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Normalize repeated spaces without changing capitalization.
    text = re.sub(r"[ \t]+", " ", text)

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

def extract_resume(file_path, output_dir="data/extracted_resumes"):
    """Extract, clean, segment, and save text from a PDF or DOCX resume."""
    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    extension = file_path.suffix.lower()

    if extension == ".pdf":
        raw_text = extract_pdf_text(file_path)

    elif extension == ".docx":
        raw_text = extract_docx_text(file_path)

    else:
        raise ValueError("Unsupported file type. Use PDF or DOCX.")

    # Step 1: Clean the extracted resume text.
    result = parse_resume_text(raw_text)

    # Step 2: Detect and separate resume sections.
    sections = segment_resume(result["cleaned_text"])

    # Add the detected sections to the result.
    result["sections"] = sections

    # Create output directory if it does not exist.
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create output JSON filename.
    output_file = output_path / f"{file_path.stem}.json"

    # Save the complete structured result.
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            {
                "source_file": file_path.name,
                **result
            },
            file,
            indent=4,
            ensure_ascii=False
        )

    logger.info("Structured resume output saved: %s", output_file)

    return result
