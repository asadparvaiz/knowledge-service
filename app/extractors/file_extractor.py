from __future__ import annotations

from pathlib import Path

from docx import Document
from pypdf import PdfReader


def extract_text_from_file(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(file_path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if suffix == ".docx":
        doc = Document(str(file_path))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    if suffix in {".txt", ".md", ".csv", ".log"}:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    raise ValueError(f"unsupported file type '{suffix}'")
