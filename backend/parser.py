"""Secure resume parsing for PDF, DOCX, and TXT files."""
import io
import os
import re
from pypdf import PdfReader
from docx import Document



MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "5")) * 1024 * 1024
MAX_EXTRACT_CHARS = 35000
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def sanitize_text(text: str) -> str:
    """Removes non-printable control characters and normalizes whitespace."""
    if not text:
        return ""
    # Strip dangerous/unprintable ASCII control characters except \n, \t, \r
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    # Normalize multiple horizontal spaces
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    # Normalize excessive newlines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()[:MAX_EXTRACT_CHARS]


def extract_resume_text(filename: str, file_bytes: bytes) -> str:
    """
    Safely validates and extracts text from uploaded PDF, DOCX, or TXT resume bytes.
    Raises ValueError with a user-friendly message on invalid or corrupted files.
    """
    if not filename or not file_bytes:
        raise ValueError("No file or empty payload was provided.")

    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise ValueError(
            f"File exceeds maximum allowed size of {MAX_UPLOAD_BYTES // (1024 * 1024)} MB."
        )

    ext = os.path.splitext(filename.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file format '{ext}'. Please upload a PDF (.pdf), Word Document (.docx), or Text (.txt) file."
        )

    extracted_text = ""

    try:
        if ext == ".pdf":
            # Verify magic bytes for PDF
            if not file_bytes.startswith(b"%PDF"):
                raise ValueError("Invalid PDF format. The file header does not match a valid PDF document.")
            
            reader = PdfReader(io.BytesIO(file_bytes))
            pages_text = []
            for idx, page in enumerate(reader.pages):
                txt = page.extract_text() or ""
                if txt.strip():
                    pages_text.append(txt)
            extracted_text = "\n".join(pages_text)

        elif ext == ".docx":
            # Verify magic bytes for ZIP/DOCX
            if not file_bytes.startswith(b"PK"):
                raise ValueError("Invalid DOCX format. The file is corrupt or not a valid Word document.")
            
            doc = Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            
            # Extract content from tables as well (frequently used in resumes)
            table_lines = []
            for table in doc.tables:
                for row in table.rows:
                    row_content = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_content:
                        table_lines.append(" | ".join(row_content))
            
            extracted_text = "\n".join(paragraphs + table_lines)

        elif ext == ".txt":
            try:
                extracted_text = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                extracted_text = file_bytes.decode("latin-1", errors="ignore")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Unable to read this file ({str(e)}). Please verify it is not corrupt or password-protected.")

    sanitized = sanitize_text(extracted_text)
    if len(sanitized) < 30:
        raise ValueError(
            "Extracted text is too short or empty. If this is a scanned/image-based resume, please paste the plain text directly."
        )

    return sanitized
